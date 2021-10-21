#!/bin/bash
#SBATCH -n 1                              # request one thread for each job in the array
#SBATCH -t 0-01:00                        # runtime in D-HH:MM format
#SBATCH -q priority                       # partition to run in
#SBATCH -o runlogs/%j.out                 # where to write stdout
#SBATCH -e runlogs/%j.err                 # where to write stderr

DIRECTORY=/work/<username>/<project_directory>
SCRIPT=${DIRECTORY}/<rosetta_script_XML>
PDB=${DIRECTORY}/${1}
FLAGS=${DIRECTORY}/<flags_file>
OUTPUT=${DIRECTORY}/output
SUFFIX=_${SLURM_JOB_ID}

# make the output directory if it doesn't already exist
[ ! -d "${DIRECTORY}/output" ] && mkdir -p "${DIRECTORY}/output"

/work/common/Rosetta/main/source/bin/rosetta_scripts.default.linuxgccrelease \
        @${FLAGS} \
        -in:file:s ${PDB} \
        -parser:protocol ${SCRIPT} \
        -out:path:all ${OUTPUT} \
        -out:suffix ${SUFFIX} \
	
