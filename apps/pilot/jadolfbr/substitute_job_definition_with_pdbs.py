#!/usr/bin/env python3

from collections import defaultdict
from argparse import ArgumentParser
import re, os, sys, glob


def replace_line(line, pdb, main_outdir, mapdir="", symdir=""):
    """
    Replace the line with passed variables. 
    :param line: 
    :param pdb: 
    :param map: 
    :param branch: 
    :return: 
    """
    pdb_base = ".".join(os.path.basename(pdb).split(".")[0:-1])
    map_file = mapdir + "/" + pdb_base + "_2mFo-DFc_map.ccp4"
    # print(map_file)
    sym_file = symdir + "/" + pdb_base + "_crys.symm"

    new_line = line.replace("%%fname%%", pdb)
    if re.search("%%map%%", line):
        new_line = new_line.replace("%%map%%", map_file)
    if re.search("%%symmdef%%", line):
        new_line = new_line.replace("%%symmdef%%", sym_file)

    if re.search("<PDB filename_pattern=", new_line):
        outpath = new_line.replace("<PDB filename_pattern=", "")
        outpath = outpath.replace("/>", " ")
        outpath = outpath.strip()
        outpath = outpath.strip('"')
        # print(outpath)

        d = os.path.join(main_outdir, os.path.dirname(outpath))
        if not os.path.exists(d):
            os.mkdir(d)
            os.system('touch ' + d + '/.gitignore')

    return new_line


def split_input_jd_to_jobs(lines):
    """
    Return a dict of the filename_pattern and the Job (including Job tags)

    :param lines: 
    :return: defaultdict
    """

    jobs = defaultdict(list)
    final_jobs = defaultdict()
    job_num = 0
    for line in lines:
        if not re.search('<', line):
            continue
        elif re.search("JobDefinition", line):
            continue
        elif re.search("<Job>", line):
            job_num += 1
            jobs[job_num].append(line)
        else:
            jobs[job_num].append(line)

    for job_num in jobs:
        # print("\n"+str(job_num))
        # print(repr(jobs[job_num]))

        pdb_path = ""
        for line in jobs[job_num]:
            if (re.search("<PDB filename_pattern=", line)):
                lineSP = line.split('=')
                pdb_path = lineSP[1].strip("/>\n").strip('"').strip('$')
                final_jobs[pdb_path] = jobs[job_num]
                break

                # for pdb in final_jobs:
                # print("\n")
                # print(pdb)
                # print(repr(final_jobs[pdb]))

    return final_jobs


def is_job_done(job_name, pdb, outdir, nstruct=2500, ext=".pdb.gz"):
    """
    Checks to see if all nstruct are present. 
    Returns true if job is done

    :param job_name: 
    :param nstruct: 
    :return: bool
    """
    final_name = outdir + "/" + job_name + pdb + "_refined"
    # print("GLOB: "+final_name+"*"+ext)
    files = glob.glob(final_name + "*" + ext)
    # print("NFILES: "+(str(len(files))))
    if len(files) == nstruct:
        print(final_name, "Is Complete")
        return True
    else:
        print(final_name, "Is missing", nstruct - len(files))
        return False


if __name__ == "__main__":
    parser = ArgumentParser("Input a base xml and output a substituted XML.")

    parser.add_argument("-j", "--jd", help="Input Job Definition XML", required=True)
    parser.add_argument("-i", "--pdbs", help="PDBList", default="PDBLIST.txt")
    parser.add_argument("-o", "--prefix", help="Any additional prefix for output XML (will use xml name)", default="")
    parser.add_argument("-m", "--mapdir", help="Map directory for PDBs")
    parser.add_argument("-s", "--symdir", help="Dir with .symm files")
    parser.add_argument("-d", "--decoy_dir",
                        help="Decoy dir for jobs.  Will create sub-directories with gitignore for cluster run here",
                        default="decoys")
    parser.add_argument("-c", "--checkpoint",
                        default=False,
                        action="store_true",
                        help="Checkpoint the output since we have problems with JD3.  "
                             "Write out a JD with only those jobs missing full PDBs.")

    parser.add_argument("-n", "--nstruct",
                        default=2500,
                        help="Nstruct we are using.  only used for checkpointing fix.")

    parser.add_argument("--test", default = False, action="store_true", help = "Run in test mode - only add one structure to the JD and add a _testing suffix.")

    options = parser.parse_args()

    if not os.path.exists(options.decoy_dir):
        os.mkdir(options.decoy_dir)

    xml_name = ".".join(os.path.basename(options.jd).split('.')[:-1])
    if options.checkpoint:
        outname = options.prefix + xml_name + "_checkpoint_substituted.xml"
    elif options.test:
        outname = options.prefix + xml_name + "_substituted_testing.xml"
    else:
        outname = options.prefix + xml_name + "_substituted.xml"

    pdblist = open(options.prefix + xml_name + "_PDBLIST.txt", 'w')

    pdb_branches = []
    for line in open(options.pdbs):
        line = line.strip()
        if not line or line.startswith("#"): continue

        pdb = line.strip()

        pdb_path = pdb

        pdb_branches.append(pdb_path)

        #Only add 1 if we are testing
        if options.test:
            break

    pdblist.close()

    print("wrote: " + options.prefix + xml_name + "_PDBLIST.txt")
    new_lines = []
    unparsed = open(options.jd, 'r').readlines()

    jobs = split_input_jd_to_jobs(unparsed)

    new_lines.append("<JobDefinitionFile>\n")

    branches = False

    # Parse experiments:
    n_jobs = 0
    for pdb in pdb_branches:
        # n_jobs+=1
        '''
        if not os.path.exists(pdb):
           sys.exit(pdb + " does not exist!")
        '''

        pdbid = os.path.basename(pdb).split(".")[0].split('_')[0]
        print("Working On:", pdbid)


        n_jobs += 1
        if options.checkpoint:
            for job in jobs:
                job_name = replace_line(job, pdb, options.decoy_dir)

                job_complete = is_job_done(job_name, pdbid, options.decoy_dir, options.nstruct)
                if job_complete:
                    continue
                else:
                    for line in jobs[job]:
                        new_line = replace_line(line, pdb, options.decoy_dir)
                        new_lines.append(new_line)
        else:
            for line in unparsed:
                if re.search("JobDefinitionFile", line): continue
                new_line = replace_line(line, pdb,  options.decoy_dir)
                new_lines.append(new_line)

    print("N Jobs: ", n_jobs)
    new_lines.append("</JobDefinitionFile>")
    if not os.path.exists("job_definitions/"):
        os.mkdir("job_definitions")
    OUT = open("job_definitions/" + outname, 'w')
    for new_line in new_lines:
        OUT.write(new_line)
    OUT.close()
    pdblist.close()

    print("Done.\nSubstituted file writted to: " + "job_definitions/" + outname)