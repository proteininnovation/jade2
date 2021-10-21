import gzip
import os
import sys
import logging
from pathlib import Path
from typing import Union, List

from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.Residue import Residue
from Bio.PDB.Structure import Structure
from Bio.PDB.Chain import Chain
from Bio.PDB.Model import Model

from jade2.basic.restype_definitions import RestypeDefinitions
from jade2.basic.numeric import *


### NOTE: All Utility function have been replaced by a Bio Structure wrapper: BioPose.
### Please see this new class for future developments!

########  NEW Biopython utility functions ##########

def is_connected_to_next(res1:Residue, res2: Residue):
    """
    Return the bond distance between two residues using Numpy array math.
    :param res1: Bio.PDB.Residue.Residue
    :param res2: Bio.PDB.Residue.Residue
    :rtype: float
    """
    distance = atomic_distance(res1, res2, 'C', 'N')
    if distance <= float(1.8):
        return True
    else:
        return False

def is_connected_to_prev(res1, res2) -> bool:
    """
    Return the bond distance between two residues using Numpy array math.
    :param res1: Bio.PDB.Residue.Residue
    :param res2: Bio.PDB.Residue.Residue
    :rtype: float
    """
    distance = atomic_distance(res1, res2, 'N', 'C')
    if distance <= float(1.8):
        return True
    else:
        return False

def atomic_distance(res1: Residue, res2: Residue, res1_atom_name: str, res2_atom_name: str) -> float:
    """
    Return the atomic distance between two arbitrary Bio residues and two arbitrary atom names.
    :param res1: Bio.PDB.Residue.Residue
    :param res2: Bio.PDB.Residue.Residue
    :param res1_atom_name: str
    :param res2_atom_name: str
    :rtype: float
    """
    try:
        return distance_numpy(res1[res1_atom_name].get_vector().get_array(), res2[res2_atom_name].get_vector().get_array())
    except Exception:
        logging.debug("Residue does not have the atom name or there is a problem in the vector.  Returning 0")
        raise IndexError

########  OLD Biopython Utility Functions replaced by BIOPose ########

def has_id(model, id) -> bool:
    """
    Returns true or false if the model has the chain.  Because biopython is not updating it's index that has_id is using.  WTF.
    """
    for i in model:
        if i.id == id:
            return True
    return False

def get_biopython_structure(path: Union[Path, str], model_id = None) -> Structure:
    structure = None
    path = str(path).strip()
    parser = PDBParser()
    cif_parser = MMCIFParser()

    extSP: List[str] = os.path.basename(path).split('.')
    if not model_id:
        model_id = os.path.basename(str(path))
    if extSP[-1] == "pdb":
        structure = parser.get_structure(model_id, path)
    elif extSP[-1] == "cif":
        structure = cif_parser.get_structure(model_id, path)
    elif extSP[-1] == 'gz':
        GZ = gzip.open(path, 'rb')

        if extSP[-2] == 'pdb':
            structure = parser.get_structure(model_id, GZ)
        elif extSP[-2] == 'cif':
            structure = cif_parser.get_structure(model_id, GZ)
        else:
            sys.exit("Unknown GZipped extenstion: "+path)

        GZ.close()
    else:
        sys.exit("Unknown extension to read PDB: "+path)
    return structure



def get_seq_from_biostructure(structure: Structure, chain_id) -> str:
    for biochain in structure[0]:
        if get_chain_length(biochain) == 0:
            continue
        if biochain.id == chain_id:
            return get_seq_from_biochain(biochain)

    print("Chain not found!")
    raise LookupError

def get_seq_from_biochain(bio_chain: Chain) -> str:

    if get_chain_length(bio_chain) == 0:
            return ""

    seq = ""
    d = RestypeDefinitions()

    for res in bio_chain:
        if res.id[0]==' ':
            aa = d.get_one_letter_from_three(res.resname)
            if not aa:
                logging.debug("Skipping non-canonical resname: "+res.resname)
                logging.debug("This could pose a problem!")
                continue
            seq = seq+aa
    return seq

def get_chain_length(bio_chain: Chain) -> int:

    l = 0
    for res in bio_chain:
        if res.id[0]==' ':
            l+=1
    return l

def get_num_biochains(model: Model) -> int:
    return len(model[0])
