import sys
from typing import DefaultDict, Union, Tuple, Any, List
from collections import defaultdict

from jade2.basic.structure.PDBResidue import PDBResidue

#Tuple of int, str, str
ResID = Tuple[int, str, str]
ResIDString = Tuple[str, str, str]


class PDBResInfo(object):
    """
    Analogous to Rosetta PDBInfo Class
    I should start at 1
    """

    def __init__(self):
        self.pose_to_record_map:   DefaultDict[int, PDBResidue] = defaultdict()
        self.pdb_to_pose_map:      DefaultDict[ResID, int]      = defaultdict()

        self.extra_data:           DefaultDict[str, Any]        = defaultdict()

    def __getitem__(self, item: int) -> PDBResidue:
        return self.pose_to_record_map[item]

    def set_residue(self, i, residue: PDBResidue):
        if not isinstance(residue, PDBResidue):
            sys.exit("Residue class must be passed for residue!")
        self.pose_to_record_map[i] = residue
        self.pdb_to_pose_map[(residue.tuple())] = i

    def add_residue(self, residue: PDBResidue):
        if not isinstance(residue, PDBResidue):
            sys.exit("Residue class must be passed for residue!")
        self.pose_to_record_map[len(self.pose_to_record_map) + 1] = residue

        self.pdb_to_pose_map[(residue.tuple())] = len(self.pose_to_record_map)

    def set_pdb_num(self, i: int, pdb_num: int, icode: str=" "):

        self.pdb_to_pose_map.pop(self.pose_to_record_map[i].tuple())

        self.pose_to_record_map[i].set_pdb_num(pdb_num)
        self.pose_to_record_map[i].set_icode(icode)

        self.pdb_to_pose_map[self.pose_to_record_map[i].tuple()] = i

    def set_icode(self, i: int, icode: str):
        self.pdb_to_pose_map.pop(self.pose_to_record_map[i].tuple())
        self.pose_to_record_map[i].set_icode(icode)
        self.pdb_to_pose_map[self.pose_to_record_map[i].tuple()] = i

    def get_all_residues(self) -> List[PDBResidue]:
        """
        return all residues held as an array in order.
        """
        residues = []
        for i in range(1, self.total_residue() + 1):
            residues.append(self.get_residue(i))

        return residues

    def set_extra_data(self, key: str, value: Any):
        self.extra_data[key] = value

    def get_extra_data(self, key: str) -> Any:
        return self.extra_data[key]

    #########################
    def pose2pdb(self, i: int) -> ResIDString:
        rec = self.get_residue(i)
        return (str(rec.pdb_num), rec.chain, rec.icode)

    def pdb2pose(self, resnum: int, chain_id: str, icode: str=' ') -> int:
        return self.pdb_to_pose_map[(resnum, chain_id, icode)]

    #########################

    def residue(self, i: int) -> PDBResidue:
        return self.pose_to_record_map[i]

    def get_residue(self, i: int) -> PDBResidue:
        return self.pose_to_record_map[i]

    def res(self, i: int) -> PDBResidue:
        return self.pose_to_record_map[i]

    #########################
    def get_resnum(self, pdb_num: int, chain: str, icode: str =' ') -> Union[int, None]:
        """
        Get the matching 'resnum' (i) or None if not found.
        """
        for i in range(1, self.total_residue() + 1):
            # print repr(i)
            res = self.pose_to_record_map[i]
            if res.get_pdb_num() == pdb_num and res.get_chain == chain and res.get_icode() == icode:
                return i

        return None

    def get_residue_of_pdb_num(self, pdb_num: int, icode: str):
        for residue in self.pose_to_record_map.values():
            if residue.pdb_num == pdb_num and residue.icode == icode:
                return residue

    def get_sequence(self) -> str:
        seq = ""
        for i in range(1, self.total_residue() + 1):
            seq = seq + self.pose_to_record_map[i].get_aa()
        return seq

    def get_sequence_bt_resnums(self, start: int, stop: int) ->str:
        seq = ""
        for i in range(start, stop + 1):
            seq = seq + self.pose_to_record_map[i].get_aa()

        print(seq)
        return seq

    def get_sequence_bt_residues(self, res1: PDBResidue, res2: PDBResidue, chain: str) -> str:
        # print repr(res1)
        # print repr(res2)

        seq = ""
        for i in range(1, self.total_residues() + 1):
            # print repr(i)
            res = self.pose_to_record_map[i]
            if res.get_pdb_num() >= res1.get_pdb_num() and res.get_pdb_num() <= res2.get_pdb_num() and res.get_chain() == chain:
                seq = seq + res.get_aa()

        print(seq)
        return seq

    def total_residues(self) -> int:
        return len(self.pose_to_record_map)

    def total_residue(self) -> int:
        return len(self.pose_to_record_map)
