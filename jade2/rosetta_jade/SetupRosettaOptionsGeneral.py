import json
import os
import sys
import re
import argparse
from jade2.basic.path import *


class SetupRosettaOptionsGeneral(object):
    """
    Class for setting up more general Rosetta options for benchmarking and repeatable runs on different clusters.
    Useful for benchmarking.
    Subclass for adding more benchmarking settings for specific benchmarks.
    """
    def __init__(self, cluster_json_file):

        if not os.path.exists(cluster_json_file):
            cluster_json_file = get_rosetta_json_run_path()+"/"+ cluster_json_file
            if not os.path.exists(cluster_json_file):
                sys.exit("cluster json file not found: "+cluster_json_file)

        self.json_file  = cluster_json_file
        FILE = open(cluster_json_file, 'r')
        self.json_dict = json.load(FILE)

        FILE.close()
        self._setup_json_options()

    def get_nstruct(self):
        if "nstruct" in self.json_dict:
            return self.json_dict["nstruct"]
        else:
            return None

    def _get_make_log_root_dir(self):
        if "logs" not in self.json_dict:
            return None

        if self.get_root():
            log_dir = self.get_root() +"/"+self.json_dict["logs"]
        else:
            log_dir = self.json_dict["logs"]

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        return self.json_dict["logs"]

    def get_root(self):
        return self._get_root()

    def get_indirs(self):
        return self._get_indirs()

    def get_xml_script(self):

        if "xml_script" in self.json_dict:
            script =  self.json_dict["xml_script"]

            #Attempt searching for xml script.  May be in in_paths:
            if os.path.exists(get_xml_scripts_path()+"/"+script):
                return get_xml_scripts_path()+"/"+script
            else:
                return script

        else:
            return ""

    def get_xml_var_string(self):
        if self.get_xml_script() and "script_vars" in self.json_dict:
            pairs = self.json_dict["script_vars"]
            var_string = " -parser:script_vars "
            for k in pairs:
                var_string = var_string+" "+k+"="+pairs[k]
            return var_string

        else:
            return ""

    def get_base_rosetta_flag_string(self, indir_root = None):
        """
        Get the full flag string for output.  Optionally give indir_root for subclasses that require setting of different
         directories, but with same root as given in the cluster file.  Used primarily for complicated benchmarks.

        """
        s = " "

        if self.get_xml_script():
            s = s + " -parser:protocol "+self.get_xml_script()
        s = s + self.get_xml_var_string()

        if len(self._get_flags_files()) > 0:
            for flags_file in self._get_flags_files():
                s = s + " @"+flags_file

        if len(self._get_indirs()) > 0:
            inpaths = " "
            for indir in self._get_indirs():
                #if indir_root:
                #    inpaths = inpaths+" "+indir_root+"/"+indir
                #else:
                inpaths = inpaths+" "+indir

            s = s+" -in:path "+inpaths

        if len(self._get_set_flags()) > 0:
            for f in self._get_set_flags():
                if not re.search('-', f):
                    f = '-'+f
                s = s+" "+f

        return s

    def get_machine_file(self):
        if 'machine_file' not in self.json_dict:
            return None
        else:
            return self.json_dict['machine_file']

    def _get_job_manager_opts(self):
        if "job_manager_opts" not in self.json_dict:
            return []
        else:
            return self.json_dict["job_manager_opts"]

    def get_program(self):
        if "program" in self.json_dict:
            return self.json_dict["program"]
        else:
            return None

    def get_db_mode(self):
        if "db_mode" in self.json_dict:
            return self.json_dict["db_mode"]
        else:
            return None

    #################################################
    def _get_root(self):
        """
        Get the root Ouput Dir loaded from JSON. Default is CWD if not set.
        """
        if "root" in self.json_dict:
            return self.json_dict["root"]
        else:
            return None

    def _get_flags_files(self):
        """
        Get the list of flags files set in JSON
        """
        if "flags_paths" in self.json_dict:
            return self.json_dict["flags_paths"]
        else:
            return []

    def _get_set_flags(self):
        if "flags" in self.json_dict:
            return self.json_dict["flags"]
        else:
            return []

    def _get_indirs(self):
        """
        Get the list of input directories set in JSON
        """
        if "indirs" in self.json_dict:
            return self.json_dict["indirs"]
        else:
            return []

    def _setup_json_options(self):
        if "root" not in self.json_dict:

            self.json_dict["root"] = os.getcwd()
            if not os.path.exists(self._get_root()):
                os.mkdir(self._get_root())

        if "flags_files" not in self.json_dict:

            self.json_dict["flags_files"] = []

        if "flags" not in self.json_dict:
            self.json_dict["flags"] = []

        if "indirs" not in self.json_dict:
            self.json_dict["indirs"] = []

        if "flags_paths" not in self.json_dict:
            self.json_dict["flags_paths"] = []

        if "indir" in self.json_dict:
            for p in self.json_dict["indir"]:
                self.json_dict["indirs"].append(p)

        if "in_paths" in self.json_dict:
            for set in self.json_dict["in_paths"]:
                if "paths" not in set:
                    print("No paths set for in_path.  Skipping")
                    continue

                if "root" in set and set["root"]:
                    root_dir = set["root"]
                    for p in set["paths"]:
                        self.json_dict["indirs"].append(root_dir+"/"+p)
                else:
                    for p in set["paths"]:
                        self.json_dict["indirs"].append(p)

        if "flags_files" in self.json_dict:
            for set in self.json_dict["flags_files"]:
                if "paths" not in set:
                    print("No paths set for flags_files  Skipping")
                    continue

                if "root" in set and set["root"]:
                    root_dir = set["root"]
                    for p in set["paths"]:
                        self.json_dict["flags_paths"].append(root_dir+"/"+p)
                else:
                    for p in set["paths"]:
                        print(repr(p))
                        self.json_dict["flags_paths"].append(p)

        ########################################

    def __str__(self):
        return repr(self.json_dict)

    def __repr__(self):
        return repr(self.json_dict)



if __name__ == "__main__":
    #For Testing:
    test_file = sys.argv[1]
    setup_mpi = SetupRosettaOptionsGeneral(test_file)
    print(repr(setup_mpi))
    print("\n")
    print(setup_mpi.get_root())
    print("\n")
    print(repr(setup_mpi.get_indirs()))
    print("\n")
    print(setup_mpi.get_base_rosetta_flag_string())