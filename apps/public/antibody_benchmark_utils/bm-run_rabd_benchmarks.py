#!/usr/bin/env python3

from jade2.RAbD_BM.RunBenchmarksRAbD import RunBenchmarksRAbD
from argparse import ArgumentParser

def get_parser():
    parser = ArgumentParser(description="This program runs Rosetta MPI locally or on a cluster using slurm or qsub.  "
                                        "Relative paths are accepted.")
    return parser

if __name__ == "__main__":
    bm = RunBenchmarksRAbD()
    bm.run()