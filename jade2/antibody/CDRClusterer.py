import math
import sys
import os
import logging
from pathlib import Path
from typing import List, Union, DefaultDict, Tuple
from collections import defaultdict

from Bio.PDB.Polypeptide import is_aa
from jade2.basic import path
from jade2.basic.structure.BioPose import BioPose
from jade2.basic.restype_definitions import RestypeDefinitions

class CDRClusterer:
    """
    A simple class for calculating a CDRs cluster from dihedrals or a renumbered pose.
    """
    
    def __init__(self, bio_pose: BioPose, clusters: str="Kelow", cluster_file: Union[str, Path, None]= None):
        """
        :param bio_pose: BioPose
        """
        if not isinstance(bio_pose, BioPose):
            sys.exit()

        self.pose = bio_pose
        self.dihedrals = None
        self.regions = {
            "L1": ['L', 24, 42],
            "L2": ['L', 57, 72],
            "L3": ['L', 107, 138],
            "L4": ['L', 82, 89],
            "H1": ['H', 24, 42],
            "H2": ['H', 57, 69],
            "H3": ['H', 107, 138],
            "H4": ['H', 82, 89],}

        self.definitions = RestypeDefinitions()

        #Set out actual clusters to use
        if cluster_file and os.path.exists(cluster_file):
            self.centers = cluster_file
            print("Using Cluster Centroid File: ", cluster_file )
        else:
            print("Using ", clusters, "Clusters")
            self.centers = path.get_cluster_path() + "/cluster_center_dihedrals_"+clusters+".txt"

    def set_biopose(self, bio_pose: BioPose):
        self.pose = bio_pose

    def set_dihedrals_from_bio_pose(self, start: int, end: int, chain: str):
        """
        Set dihedrals from a BioPose
        :param start: int
        :param end: int
        :param chain: str
        """
        self.dihedrals = defaultdict(list)
        reslist = [i for i in self.pose.chain(chain, 0).get_residues() if
                   i.id[1] in range(start - 1, end + 2) and is_aa(i, standard=False)]

        for res in reslist[1:-1]:
            resindex = reslist.index(res)
            resnextindex = resindex + 1
            resprevindex = resindex - 1
            resnext = reslist[resnextindex]
            resprev = reslist[resprevindex]

            self.dihedrals['phi'].append(math.degrees(self.pose.phi(res, resprev)))
            self.dihedrals['psi'].append(math.degrees(self.pose.psi(res, resnext)))
            self.dihedrals['omega'].append(math.degrees(self.pose.omega(res, resnext, resprev, rosetta_definitions=False)))
    
    def set_dihedrals_from_cdr(self, cdr_name: str, chain: str):
        start = self.regions[cdr_name][1]
        end = self.regions[cdr_name][2]
        self.set_dihedrals_from_bio_pose(start, end, chain)
        
    def set_custom_dihedrals(self, dihedrals: DefaultDict[str, List[float]]):
        """
        Dihedrals is a dict: ['phi']=[x, y, z]; ['psi'] = [x, y, z]; ['omega'] = [x, y, z (degrees)]
        """
        
        self.dihedrals =  dihedrals

    def get_length(self, cdr_name: str) -> int:
        start = self.regions[cdr_name][1]
        end = self.regions[cdr_name][2]
        chain = self.regions[cdr_name][0]
        #print repr(start)+" "+repr(end)+" "+repr(chain)

        self.set_dihedrals_from_bio_pose(start, end, chain)
        #print repr(self.dihedrals)
        cdr_length = len(self.dihedrals['phi'])
        return cdr_length



    def get_fullcluster(self, cdr_name: str, chain: Union[str, None] = None, region: Union[Tuple[int, int, str], None] = None)\
            -> Tuple[str, float]:
        """
        Returns the identified cluster and distance.

        IF DIHEDRALS is SET - AKA from before using the same class - WILL USE THE SAME DIHEDRALS AS BEFORE
        Rewritten from C++ code.  Identifies the cluster of a known cdr type given either custom dihedrals or dihedrals calculated from a pose.
        Returns a pair or [cdr_cluster, distance]
        region is [int start, int end, chain] - This way you can cluster without renumbering if you want.

        """
        
        if not self.dihedrals:
            if not region:
                start = self.regions[cdr_name][1]
                end = self.regions[cdr_name][2]
                chain = self.regions[cdr_name][0]
            else:
                start = region[0]
                end = region[1]
                chain = region[2]
            self.set_dihedrals_from_bio_pose(start, end, chain)
            
        #string cdr;
        #Size length;
        #string cluster;
        #string type;
        #string fullcluster;
        #string ss;
        #string phis;
        #string psis;
        #string omegas;
        PI = math.pi


        cdr_length = len(self.dihedrals['phi'])
        pose_angles = self.dihedrals
        model_ss = ""
        cis_cutoff = 90.00
        for omega in pose_angles['omega']:

            if math.fabs(omega) >= cis_cutoff:
                model_ss = model_ss+"T"
            else:
                model_ss = model_ss+"C"



        #print "CDR: "+ cdr_name+" "+repr(cdr_length)+" "+model_ss

        k_distances_to_cluster: DefaultDict[float, str] = defaultdict()
        k_distances: List[float] = []
        line_count = 0
        cluster_found = False
        FILE = path.open_file(self.centers, 'r')
        FILE.readline() #Read header and keep going
        for line in FILE:
            line_count+=1
            lineSP = line.split()
            cdr = lineSP[0]; length = int(lineSP[1]); cluster = lineSP[2]; length_type= lineSP[3]; fullcluster = lineSP[4]; ss = lineSP[5];
            phis = lineSP[6]; psis = lineSP[7]; omegas = lineSP[8]
            
            #Should I do the measuring here, or actually put the data in ram, then go through the data?
            #TR << cdr <<" "<<length<<" "<<ss<<std::endl;
            #print(cdr, cdr_name, repr(length), repr(cdr_length), ss, model_ss)
            
            if (cdr==cdr_name and length==cdr_length and ss==model_ss):
                    cluster_found=True
                    k_distance_to_cluster=0.0
                    #Calculate, add into cluster_distances.
                    cluster_angles: DefaultDict[str, List[str]] = defaultdict()

                    cluster_angles['phi'] = []; cluster_angles['psi'] = []
                    phiSP = phis.split(','); psiSP = psis.split(',')
                    for phi in phiSP: cluster_angles['phi'].append(phi)
                    for psi in psiSP: cluster_angles['psi'].append(psi)
                    
                    #Calculate:
                    for i in range(0, cdr_length):
                        #Need to convert angles to positive values for now.
                        phi = float(cluster_angles['phi'][i])
                        psi = float(cluster_angles['psi'][i])
                        
                        phi_d = (2 * (1- math.cos ((pose_angles["phi"][i]-phi)*PI/180)))
                        psi_d = (2 * (1- math.cos ((pose_angles["psi"][i]-psi)*PI/180)))
                        k_distance_to_cluster = k_distance_to_cluster+phi_d+psi_d

                
                    k_distances_to_cluster[k_distance_to_cluster]=fullcluster
                    k_distances.append(k_distance_to_cluster)
            else:
                continue


        FILE.close()

        #Take the minimum distance as the cluster.
        cdr_cluster = ""
        cdr_distance = 0
        if not cluster_found:
            logging.debug("Cluster not found for CDR "+cdr_name)
            cdr_cluster = "NA"
            cdr_distance = 1000
            
            pair = (cdr_cluster, cdr_distance)
            return pair
        else:
            #Get minimum and set cluster.
            
            d = min(k_distances)
            cdr_distance = d          
            cdr_cluster = k_distances_to_cluster[d]
            #print cdr_name+" cluster found as "+ cdr_cluster + " at k_distance: "+repr(d)
            #TR <<"Setting this as closest cluster, as no cutoff is yet set. PLEASE manually compare structures.  " <<std::endl;
            pair = (cdr_cluster, cdr_distance)
            return pair
    
    