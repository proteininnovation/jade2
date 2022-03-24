from .file_functions import *
from .general import *
from .numeric import *
from .path import *
from .restype_definitions import *
from .stats import *
from .string_util import *
from . import restype_definitions as resd


aacodes = resd.RestypeDefinitions().get_all_one_letter_codes()

class vector1(list):
    """
    A list indexed at 1!
    """
    def __init__(self, seq=()):
        list.__init__(self, seq)
        self.insert(0, 0)

    def __len__(self):
        return list.__len__(self) - 1

    def __iter__(self):
        from_one = [x for x in list.__iter__(self)][1:]
        return (x for x in from_one)