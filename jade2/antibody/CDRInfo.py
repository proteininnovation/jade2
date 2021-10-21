import math
from . import util
from operator import itemgetter
from itertools import groupby
from typing import Union


class CDRInfo(object):
    """
    A simple object for holding and accessing CDR information.
    """
    def __init__(self, cdr_name: str, start: int, end: int, gene: str="unk", cluster: str = "unk", distance: Union[float, None]=None):
        self.cdr_type = cdr_name
        self.cdr_start = start  # Actual CDR start

        # I know this is really stupid and needs to be refactored.  It basically existed as a grab bag of data for output at some point.
        self.new_start = self.old_start = start
        self.cdr_end =self.old_end = end

        self.old_chain = self.new_chain = cdr_name[0]

        self.cluster = cluster
        self.gene = gene

        self.regions = {
            'L1': ['L', 24, 42],
            'L2': ['L', 57, 72],
            'L3': ['L', 107, 138],
            'L4': ['L', 82, 89],
            'H1': ['H', 24, 42],
            'H2': ['H', 57, 69],
            'H3': ['H', 107, 138],
            'H4': ['H', 82, 89]}

        self.has_chainbreak = False
        self.chainbreak_indices = []

        if distance:
            self.set_distance(distance)

    def __str__(self):
        line = "CDR "+self.cdr_type +"\t"+ repr(self.cdr_start)+"\t"+repr(self.cdr_end)+"\t"+repr(self.cluster)
        return line
    
    def get_pdb_output(self, full_sequence: str) -> str:
        line = "CDR "+self.cdr_type+"\t"+repr(self.old_start)+"\t"+self.old_chain+"\t"+repr(self.new_start)+"\t"+self.new_chain+"\t"+ \
        self.get_sequence(full_sequence)+"\t"+self.cluster+"\t%.4f"%self.distance+"\t%.4f"%(self.norm_dis)+"\t%.2f"%(self.norm_dis_deg)
        return line
    
    def set_new_chain(self, chain: str):
        self.new_chain = chain
        
    def get_new_chain(self) -> str:
        return self.new_chain
    
    def get_gene(self) -> str:
        return self.gene
    
    def get_type(self) -> str:
        return self.cdr_type
    
    def get_start(self) -> int:
        """
        Starting residue of the CDR in chain.  1 - n
        """
        return self.cdr_start
    
    def get_end(self) -> int:
        """
        Ending residue of the CDR in chain. 1 - n
        """
        return self.cdr_end
    
    def get_length(self) -> int:

        #print self.cdr_type+" "+repr(self.cdr_end)+" : "+repr(self.cdr_start)
        l = self.cdr_end-self.cdr_start + 1
        #print "New Length: "+repr(l)
        return l
    
    def set_original_cdr_info(self, start: int, end: int, chain: str):
        """
        Set the original info for a CDR with a PDB.  Used after renumbering.
        """
        
        self.old_start = start
        self.old_end = end
        self.old_chain = chain
    
    def get_original_start(self) -> int:
        return self.old_start
    
    def get_original_end(self) -> int:
        return self.old_end
    
    def get_original_chain(self) -> str:
        return self.old_chain
    
    ##################
    #Sequence
    #  
    def get_sequence(self, full_sequence: str):
        """
        Get the sequence from a sequence string.
        """
        seq = full_sequence[(self.cdr_start-1):self.cdr_end]
        return seq
        
    ##################
    #Clusters
    #  
    
    def set_cluster(self, cluster: str):
        self.cluster = cluster
    
    def set_distance(self, distance):
        if distance < 1000:
            self.distance = distance
            self.norm_dis = util.get_norm_distance(self.get_length(), distance)
            try:
                self.norm_dis_deg = util.get_norm_distance_deg(self.norm_dis)
            except ValueError:
                print("Trouble in calculating normalized distance in degrees. Setting to 360: ", distance, self.norm_dis, self.norm_dis)
                self.norm_dis_deg = 360
        else:
            self.distance = distance
            self.norm_dis = distance
            self.norm_dis_deg = distance

    def get_cluster(self) -> str:
        return self.cluster
    
    def get_distance(self) -> float:
        return self.distance

    def get_chainbreak(self, abchain):

        allresnum = [i.tuple()[0] for i in abchain.get_pdb_res_info().get_all_residues()]

        cdrresnums = [i for i, x in enumerate(allresnum) if
                      x in range(self.regions[self.cdr_type][1] + 1, self.regions[self.cdr_type][2] + 2)]

        originalresidues = list(map(lambda i: abchain.get_pdb_res_info().residue(i).get_old_resnum(), cdrresnums))

        ranges = []

        for k, g in groupby(enumerate(originalresidues), lambda i, x: i - x):
            group = map(itemgetter(1), g)
            ranges.append((group[0], group[-1]))

        if len(ranges) == 1:
            self.has_chainbreak = False
            self.chainbreak_indices = None

        if len(ranges) > 1:

            self.has_chainbreak = True
            has_residues = map(lambda i: range(i[0], i[1] + 1), ranges)
            has_residues = [item for sublist in has_residues for item in sublist]
            missingresidues = [(i - min(has_residues)) for i in range(min(has_residues), max(has_residues) + 1) if
                               i not in has_residues]

            for index in missingresidues:

                if index == 0:
                    self.chainbreak_indices.append(1)

                if index == max(has_residues):
                    self.chainbreak_indices.append(max(has_residues) - min(has_residues) - 1)

                if index != 0 or index != max(has_residues):
                    self.chainbreak_indices.append(index - 1)
                    self.chainbreak_indices.append(index + 1)

            self.chainbreak_indices = sorted(list(set(self.chainbreak_indices)))

        return (self.has_chainbreak, self.chainbreak_indices)

    