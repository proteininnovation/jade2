from typing import DefaultDict, Any, Union, Tuple, List

from collections import defaultdict


class PDBResidue(object):
    """
    Basic class to PDBInfo
    """
    def __init__(self, one_letter_aa: str, pdb_num: int, chain: str, icode: str = " "):
        self.aa = one_letter_aa
        self.pdb_num = pdb_num
        self.chain = chain
        self.icode = icode
        self.extra_info: DefaultDict[str, Any] = defaultdict()

    def __str__(self):
        s = repr(self.pdb_num)+" "+self.chain+" "+self.icode+" "+ self.aa
        return s

    def __repr__(self):
        return self.__str__()

    def tuple(self) -> Tuple[int, str, str]:
        """
        Return a tuple of pdbnum, chain, icode
        """
        return self.pdb_num, self.chain, self.icode

    def set_pdb_num(self, pdb_num: Union[str, int]):
        self.pdb_num = pdb_num

    def set_chain(self, chain: str):
        self.chain = chain

    def set_icode(self, icode: str):
        self.icode = icode

    def set_gene(self, gene: str):
        self.set_extra_info('gene', gene)
    def get_gene(self) -> str:
        if self.has_extra_info('gene'):
            return self.get_extra_info('gene')

    def set_aa(self, one_letter_aa: str):
        self.aa = one_letter_aa
        self.aa = one_letter_aa

    def set_extra_info(self, key: str, value: Any):
        self.extra_info[key] = value

    ######################
    def get_aa(self) -> str:
        return self.aa

    def get_pdb_num(self) -> int:
        return self.pdb_num

    def get_chain(self) -> str:
        return self.chain

    def get_icode(self) -> str:
        return self.icode

    def has_extra_info(self, key: str):
        if key in self.extra_info:
            return True
        else:
            return False

    def get_extra_info(self, key: str) -> Any:
        return self.extra_info[key]

    def get_extra_info_keys(self) -> List[str]:
        return sorted(self.extra_info.keys())

    def get_extra_info_dict(self) -> DefaultDict[str, Any]:
        return self.extra_info

    def init_extra_infos(self, array_of_keys: List[str], value: Any):
        for key in array_of_keys:
            self.extra_info[key] = value
