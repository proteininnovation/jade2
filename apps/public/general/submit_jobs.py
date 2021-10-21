#!/usr/bin/env python3

from argparse import ArgumentParser
import os,re
import sys
import glob
import time

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
    parser = ArgumentParser("Script to run sewing and other MPI jobs.  Will create slurm scripts in /slurm_scripts, and run them with sbatch, creating directories for each job.")

    parser.add_argument("--cmd", "-c",
                        help = "Rosetta command line.  We will add output directories. ",
                        required=True)

    parser.add_argument("--o2",
                        help = "Run this on o2.  o2 is setup differently for MPIrun.",
                        default= False,
                        action="store_true")

    parser.add_argument("--local",
                        help = "Run a local job.",
                        action = "store_true",
                        default = False)

    parser.add_argument("--np",  "-n",
                        help = "Number of processors to use", default=60,
                        type=int)

    parser.add_argument("--jobs", "-j",
                        help = "Number of jobs to submit", default=1,
                        type=int)

    parser.add_argument("--core_script", "-s",
                        help="Basis SLURM script - just the header. See config directory for examples.",
                        required=True)

    parser.add_argument("--outdir", "-o",
                        help = "Root outdir. Will make outer and inner directories.",
                        required=True)

    parser.add_argument("--basic", "-b",
                        help = "Just run a basic job, don't deal with sub-directories.",
                        action="store_true",
                        default = False)

    parser.add_argument("--jn",
                        help = "Job name if running basic job",
                        default = "rosetta_job")

    parser.add_argument("--print_only", "-p", help="Only print what we will run for debugging",
                        default=False, action="store_true")

    parser.add_argument("--scratch",
                        help="directory to put submission scripts. ", default="slurm_scripts")

    parser.add_argument("--replace",
                        help="Continue the next batch?  Use the output directory to get what has been done so far",
                        default=False, action="store_true")

    parser.add_argument('--time', '-t', help = "Time for slurm job as a string. D-HH:MM format.",
                        default="0-24:00", type=str)

    parser.add_argument('--mem', '-m', help="Mem requested in MB per cpu. If default, will not pass (used on andromeda.)",
                        default='default', type=str)

    options = parser.parse_args()

    if not os.path.exists(options.scratch):
        os.mkdir(options.scratch)

    if not os.path.exists(options.outdir):
        os.mkdir(options.outdir)

    output = ""

    if os.path.exists(options.core_script):
        output = open(options.core_script, 'r').readlines()
    else:
        exit("Core Script "+options.core_script+" does not exist!")

    mem=" "
    if (options.mem != "default"):
        mem =  " --mem-per-cpu="+options.mem
    cmd = "sbatch --ntasks="+str(options.np)+mem+" -t "+options.time

    d_root = os.path.basename(options.outdir)
    job_name = d_root

    tag = "-parser:protocol"
    if (re.search("multistage_rosetta_scripts", options.cmd) or re.search("rosetta_scripts_jd3", options.cmd)):
        tag="-job_definition_file"

    script = ""
    cmdSP = options.cmd.split(" ")
    for i in range(0, len(cmdSP)):
        cm = cmdSP[i].strip()
        if cm == tag:
            script = cmdSP[i+1]

    if script and not os.path.exists(script):
        sys.exit("Script for RosettaScripts not found! "+script)

    if options.basic:
        if (options.jn != "rosetta_job"):
            job_name = options.jn
        local_cmd = cmd + " --job-name="+job_name

        #local_cmd = local_cmd + " -o " + "/n/scratch3/users/j/jpa23/logs" + "/" + job_name + "_%j.out"
        #local_cmd = local_cmd + " -e " + "error_logs" + "/" + job_name + "_%j.err"

        if (options.o2 or options.local):
            r_cmd = "mpirun -np "+str(options.np)+" " + options.cmd
        else:
            r_cmd = "mpirun " + options.cmd + " -out:path:all "+options.outdir

        out = open(options.scratch+"/"+job_name+".sh", 'w')
        for line in output:
            out.write(line+"\n")
        out.write("\n")
        out.write(r_cmd)
        out.write("\n")
        out.close()
        os.system('cp '+options.scratch+"/"+job_name+".sh "+options.outdir+'/cmd.sh')
        print("Running slurm Job ")
        local_cmd = local_cmd+" "+options.scratch+"/"+job_name+".sh"
        print(local_cmd)

        if script:
            os.system('cp ' + script + ' ' + options.outdir+"/"+os.path.basename(script))

        if not options.print_only and not options.local:
            os.system(local_cmd)
        elif options.local:
            os.system(r_cmd)

        sys.exit()

    starting_dir = 0

    if not options.replace :
        dirs = get_directories_recursively(options.outdir)
        for d in dirs:
            dSP = os.path.basename(d).split("_")
            #print(d)
            print(repr(dSP))
            if dSP[0] == "all": continue
            if int(dSP[-1]) > starting_dir:
                starting_dir = int(dSP[-1])

    starting_dir+=1
    if options.local:
        n_jobs = 1
    else:
        n_jobs = options.jobs

    for i in range(starting_dir, starting_dir + n_jobs):
        job_name = str(i) + "_"+ d_root
        outdir = options.outdir+"/"+d_root+"_"+str(i)
        if not os.path.exists(outdir) and not options.print_only: os.mkdir(outdir)
        local_cmd = cmd + " --job-name="+job_name

        #local_cmd = local_cmd + " -o " + "" + "/" + job_name + "_%j.out"
        #local_cmd = local_cmd + " -e " + "logs" + "/" + job_name + "_%j.err"

        if options.o2 or options.local:
            r_cmd = "mpirun -np "+str(options.np)+" " + options.cmd+" -out:path:all "+options.outdir+"/"+d_root+'_'+str(i)
        else:
            r_cmd = "mpirun " + options.cmd+" -out:path:all "+options.outdir+"/"+d_root+'_'+str(i)

        out = open(options.scratch+"/"+job_name+".sh", 'w')
        for line in output:
            out.write(line+"\n")
        out.write("\n")
        out.write(r_cmd)
        out.write("\n")
        out.close()
        os.system('cp ' + options.scratch + "/" + job_name + ".sh " + outdir + '/cmd.sh')

        print("Running slurm Job "+str(i))
        local_cmd = local_cmd+" "+options.scratch+"/"+job_name+".sh"
        print(local_cmd)
        if script:
            os.system('cp ' + script + ' ' + outdir +"/"+os.path.basename(script))

        if not options.print_only and not options.local:
            os.system(local_cmd)
        elif options.local:
            os.system(r_cmd)

        time.sleep(.25)





