#!/bin/bash
#SBATCH -n 30                             # request one thread for each job in the array
#SBATCH -t 0-18:00                        # runtime in D-HH:MM format
#SBATCH -q long                           # partition to run in
#SBATCH -o runlogs/%j.out                 # where to write stdout
#SBATCH -e runlogs/%j.err                 # where to write stderr

DIRECTORY=/work/<username>/<project_directory>
SCRIPT=${DIRECTORY}/<rosetta_script_XML>
PDB=${DIRECTORY}/<input_PDB>
FLAGS=${DIRECTORY}/<flags_file>
OUTPUT=${DIRECTORY}/output
SUFFIX=_${SLURM_JOB_ID}

# make the output directory if it doesn't already exist
[ ! -d "${DIRECTORY}/output" ] && mkdir -p "${DIRECTORY}/output"

mpirun /work/common/Rosetta/main/source/bin/multistage_rosetta_scripts.mpiserialization.linuxgccrelease \
        @${FLAGS} \
        -in:file:s ${PDB} \
        -parser:protocol ${SCRIPT} \
        -out:path:all ${OUTPUT} \
        -out:suffix ${SUFFIX} \
	
