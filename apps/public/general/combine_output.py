#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import sys
import glob

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
    parser = ArgumentParser("Get number of outputs and combine.")

    parser.add_argument("--dir", '-d',
                        help = "Root directory path.",
                        required=True)

    parser.add_argument("--print_only", '-p',
                        help = "Should we just count the totals?",
                        default = False, action="store_true")
    parser.add_argument("--add", "-a",
                        help = "Add other directories to final one, dont override.",
                        default=False, action="store_true")
    parser.add_argument("--tar", '-t',
                        help = "Tar up?",
                        default=False, action="store_true")

    parser.add_argument("--out_dir", '-o',
                        help = "Any other root outdir to combine outputs")

    options = parser.parse_args()

    #Override output directory to simplify analysis.
    if options.out_dir:
        if not os.path.exists(options.out_dir):
            os.mkdir(options.out_dir)
        outdir = options.out_dir + "/" + "all_" + os.path.basename(options.dir)
    else:
        outdir = options.dir + "/" + "all_" + os.path.basename(options.dir)

    if not options.print_only:
        if not os.path.exists(outdir):
            os.mkdir(outdir)

    current_count = 1
    if options.add:
        pdbs = get_matching_pdbs(outdir, '', '.pdb')
        if len(pdbs):
            current_count = len(pdbs)

    dirs = get_directories_recursively(options.dir)
    totals = 0
    if not options.print_only:
        pdblist = open(outdir+"/PDBLIST.txt", 'w')
    for d in dirs:
        if os.path.basename(d) == os.path.basename(outdir): continue
        out_pdbs = get_matching_pdbs(d, '', '.pdb')
        totals+=len(out_pdbs)
        print(os.path.basename(d), len(out_pdbs))
        if not options.print_only:
            for pdb in out_pdbs:
                cmd = 'cp '+d+'/'+pdb+' '+outdir+'/'+os.path.basename(outdir)+"_"+str(current_count)+".pdb"
                print(cmd)
                os.system(cmd)
                pdblist.write(os.path.basename(outdir)+"_"+str(current_count)+".pdb\n")
                current_count+=1

    if not options.print_only:
        pdblist.close()

    if not os.path.exists("tars"): os.mkdir("tars")

    print("Total", totals)

    tar_cmd = "tar -C " + outdir +" -czvf tars/"+os.path.basename(outdir)+".tar.gz ."
    print(tar_cmd)
    if options.tar:
        print("Tarring output up into tar directory.")
        os.system(tar_cmd)

    pw = os.getcwd()
    print("scp $transfer:"+pw+"/tars/"+os.path.basename(outdir)+".tar.gz "+ "tars")
    print("sync_zip $transfer:"+pw+"/"+outdir+" analysis")

