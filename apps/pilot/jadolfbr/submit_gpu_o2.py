#!/usr/bin/env python3
from argparse import ArgumentParser
import os, re, sys





if __name__ == "__main__":
    parser = ArgumentParser("Simple app to submit jobs to the GPU queue on O2")

    parser.add_argument("--cmd", "-d",
                        help = "Script cmd-line in quotes.  We will add output directories. ",
                        required=True)

    parser.add_argument("--core_script", "-s",
                        help="Basis SLURM script - just the header. See config directory for examples.",
                        required=True)

    parser.add_argument("--gpus", "-g",
                        help = "Number of GPUs to request.  Default 1.",
                        default="1",
                        type = str)

    parser.add_argument("--cpus", "-c",
                        help = "Number of CPUs to request. Default 1.",
                        default = "1",
                        type = str)

    parser.add_argument("--mem", '-m',
                        help = "Memory per GPU. Default 1G",
                        default = "1000M",
                        type = str)

    parser.add_argument("--type", "-y",
                        help = "Any specific type of GPU requested. ",
                        choices= ['teslaM40', 'teslaK80', 'teslaV100'])

    parser.add_argument("--print_only", "-p", help="Only print what we will run for debugging",
                        default=False, action="store_true")

    parser.add_argument("--scratch",
                        help="directory to put submission scripts. ",
                        default="slurm")

    parser.add_argument("--jn",
                        help = "Job name if running basic job",
                        default = "pytorch_design")

    parser.add_argument('--time', '-t', help = "Time for slurm job as a string. D-HH:MM format.",
                        default="0-24:00", type=str)

    options = parser.parse_args()
    job_name = options.jn

    if not os.path.exists(options.scratch):
        os.mkdir(options.scratch)

    output = ""
    if os.path.exists(options.core_script):
        output = open(options.core_script, 'r').readlines()
    else:
        exit("Core Script "+options.core_script+" does not exist!")


    mem =  " --mem-per-gpu="+options.mem
    cmd = "sbatch -p gpu "+mem+" -t "+options.time

    if options.type:
        cmd = cmd +" --gres=gpu:"+options.type+":"+options.gpus
    else:
        cmd = cmd +" --gres=gpu:"+options.gpus


    cmd = cmd +" -c "+options.cpus

    cmd = cmd + " --job-name="+job_name
    r_cmd = options.cmd
    out = open(options.scratch+"/"+job_name+".sh", 'w')
    for line in output:
        out.write(line+"\n")
    out.write("\n")
    out.write(r_cmd)
    out.write("\n")
    out.close()
    #os.system('cp '+options.scratch+"/"+job_name+".sh "+options.outdir+'/cmd.sh')
    print("Running slurm Job ")
    cmd = cmd+" "+options.scratch+"/"+job_name+".sh"
    print(cmd)

    if not options.print_only:
        os.system(cmd)
