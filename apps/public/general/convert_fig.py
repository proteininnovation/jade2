#!/usr/bin/env python3


import os
import sys
from argparse import ArgumentParser

def get_parser():
    parser = ArgumentParser(description="Converts images to TIFF figures at 300 DPI for publication using sips. "
                            "Arguments: INFILE OUTFILE"
                            "Example: convert_to.py in_fig.pdf out_fig.tiff\n"
                            "Example: convert_to.py in_fig.png out_fig.eps eps")

    return parser

if __name__ == "__main__":

    parser = get_parser()
    parser.parse_args()

    if len(sys.argv) < 3:
        sys.exit()

    in_file = sys.argv[1]
    out_file = sys.argv[2]

    outformat = "tiff"
    if len(sys.argv) == 4:
        outformat = sys.argv[3]

    cmd = "sips -s format {format} {in_path} -s dpiHeight 300 -s dpiWidth 300 --out {out_path}".format(
        format = outformat, in_path = in_file, out_path = out_file)

    print(cmd)

    os.system(cmd)
    print("done")



