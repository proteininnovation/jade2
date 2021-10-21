#!/usr/bin/env python3

from jade2.rosetta_jade.RunRosettaBenchmarks import *
from argparse import ArgumentParser

##Main to RunRosetta.

def get_parser():
    parser = ArgumentParser(description="This program runs Rosetta MPI locally or on a cluster using slurm or qsub.  "
                                        "Relative paths are accepted.")
    return parser

if __name__ == "__main__":
    run_rosetta = RunRosettaBenchmarks()
    run_rosetta.run()