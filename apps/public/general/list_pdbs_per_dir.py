#!/usr/bin/env python3
from argparse import ArgumentParser
import glob,os,sys
import numpy

def get_directories_recursively(inpath):
    """
    Get a list of directories recursively in a path.  Skips hidden directories.
    :param inpath: str
    :rtype: list
    """

    all_dirs = []
    for root, dirs, files in os.walk(inpath):
        all_dirs.extend([root+"/"+d for d in dirs if d[0] != '.'])
    return all_dirs

def get_matching_pdbs(directory, pattern, ext='.pdb'):
    """
    Get pdbs in a directory matching a pattern.
    :param directory:
    :param pattern:
    :param ext:
    :return:
    """
    files = glob.glob(directory+"/"+'*'+pattern+'*'+ext)
    return [os.path.basename(f) for f in files]

if __name__ == "__main__":
    parser = ArgumentParser("Simple script to list all files in all directories (recursively), with some summaries at the end")


    parser.add_argument("--dir", '-d', help = "Directory to look at")
    parser.add_argument("--ext", '-e', default='.pdb', help = "Extension to look for")
    parser.add_argument("--pattern", '-p', default="", help = "Any pattern to match (simple")
    parser.add_argument('--delete', '-t', action = 'store_true', default=False, help = "Delete the pdbs found?  Default false")

    options = parser.parse_args()

    counts = []
    dirs = get_directories_recursively(options.dir)
    for d in dirs:
        if not os.path.isdir(d): continue

        pdbs = get_matching_pdbs(d, options.pattern, options.ext)
        count = len(pdbs)
        counts.append(count)
        if count > 0:
            print(d, count)
            if options.delete:
                for pdb in pdbs:
                    os.remove(d+'/'+pdb)

    print('mean', numpy.mean(counts))
    print('min', numpy.min(counts))
    print('max', numpy.max(counts))