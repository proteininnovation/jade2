from collections import defaultdict
from abc import ABC, abstractmethod
from typing import Dict, List
import sys, os


class Parameters( ABC ):
    def __init__(self, base = "hp"):
        super().__init__()
        self.parameters = self._create_parameters()
        self.docs = self._create_docs()

        self.base = base

    @abstractmethod
    def _create_parameters(self) -> Dict:
        pass

    @abstractmethod
    def _create_docs(self) -> Dict:
        pass

    def read_params(self, filename):
        if not filename:
            return

        if not os.path.exists(filename):
            sys.exit("Filename " + filename +" Does not exist")

        args = self.parameters
        for line in open(filename, 'r'):
            if line.strip().startswith('#'): continue
            lineSP = line.strip().split('=')
            hp = lineSP[0].strip()
            if hp in self.parameters:
                args[hp] = [x.strip() for x in lineSP[1].split(';')]
                try:
                    args[hp] = [ eval(x) for x in args[hp]]
                except Exception:
                    continue

        self.parameters =  args

    def set_from_options(self, options):
        """
        Set from options as defaults, override defaults if hp file is set.
        :param options:
        :return:
        """
        for opt in self.parameters:
            new_opt = self.base+"_"+opt
            if new_opt in options.__dict__ and options.__dict__[new_opt] is not None:
                val = options.__dict__[new_opt]
                self.parameters[opt] = [val]

        hp_file = f'{self.base}_file'
        if hp_file in vars(options):
            self.read_params(vars(options)[hp_file])

    def add_parser(self, parser, group_name = "Hyperparameters", description = "Hyperparameters for the model"):
        hp_args = parser.add_argument_group(group_name, description)

        hp_args.add_argument(f"--{self.base}_file",
                             help = "A file that lists hyperparameters one per line. "
                                    "We will combine these for search if given. Ex lr = 1e-4; 2e-4")

        for hp in self.parameters:
            hp_args.add_argument(f"--{self.base}_{hp}",
                                 default = self.parameters[hp][0],
                                 help = self.docs[hp],
                                 type = type(self.parameters[hp][0]))

class Params(object):
    """
    A simple class to treat dictionary values as attributes.
    So you can do:
     p = Params(some_dict)
     p.some_value

    """
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
        self.data = my_dict
    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getattr__(self, item):
        return self.data[item]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)

    def for_writer(self):
        """
        Return a cleaned dict for the writer.  IE - remove "/"
        :return:
        """
        d = defaultdict()
        for key, value in self.data.items():
            if type(value) == str:
                r = value.replace("/", "_")
                d[key] = r
            else:
                d[key] = value

        return d