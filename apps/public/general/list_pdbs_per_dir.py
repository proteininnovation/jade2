#!/usr/bin/env python3
from argparse import ArgumentParser
import glob,os,sys
import numpy
from os import listdir
from os.path import isfile, join

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

def get_directories(rootdir):
    dirs = []
    for it in os.scandir(rootdir):
        if it.is_dir():
            dirs.append(it.path)
    return dirs

if __name__ == "__main__":
    parser = ArgumentParser("Simple script to list all files in all directories (non-recursively), with some summaries at the end. Pretty slow, needs to be sped up for sure")


    parser.add_argument("--dir", '-d', help = "Directory to look at")
    #parser.add_argument("--ext", '-e', default='.pdb', help = "Extension to look for")
    #parser.add_argument("--pattern", '-p', default="", help = "Any pattern to match (simple")
    #parser.add_argument('--delete', '-t', action = 'store_true', default=False, help = "Delete the pdbs found?  Default false")

    options = parser.parse_args()

    counts = []
    dirs = get_directories(options.dir)

    print("Found ", len(dirs), "Directories")

    for d in dirs:
        if not os.path.isdir(d): continue
        count = sum(1 for entry in listdir(d) if isfile(join(d, entry)))
        #pdbs = get_matching_pdbs(d, options.pattern, options.ext)
        #count = len(pdbs)
        if count > 0:
            print(d, count)
            counts.append(count)
            #if options.delete:
            #    for pdb in pdbs:
            #        os.remove(d+'/'+pdb)

    print("Total non-zero directories", len(counts))
    print('mean', numpy.mean(counts))
    print('min', numpy.min(counts))
    print('max', numpy.max(counts))