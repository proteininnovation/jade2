#!/usr/bin/env python3

from jade2.rosetta_jade.RunRosetta import *
from argparse import ArgumentParser

def get_parser():
    parser = ArgumentParser(description="This program runs Rosetta MPI locally or on a cluster using slurm or qsub.  "
                                        "Relative paths are accepted.")
    return parser

##Main to RunRosetta.

if __name__ == "__main__":
    run_rosetta = RunRosetta(db_mode=True)
    run_rosetta.run()