#!/bin/bash
#SBATCH -n 1                              # request one thread for each job in the array
#SBATCH -t 0-03:00                        # runtime in D-HH:MM format
#SBATCH -q production                     # partition to run in
#SBATCH --array=0-29                      # start counting at zero, how many jobs are in the array
#SBATCH -o /dev/null                      # where to write stdout
#SBATCH -e runlogs/%A_%a.err              # where to write stderr

DIRECTORY=/work/<username>/<project_directory>
SCRIPT=${DIRECTORY}/<rosetta_script_XML>
PDB=${DIRECTORY}/<input_PDB>
FLAGS=${DIRECTORY}/<flags_file>
OUTPUT=${DIRECTORY}/output
SUFFIX=_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}

# make the output directory if it doesn't already exist
[ ! -d "${DIRECTORY}/output" ] && mkdir -p "${DIRECTORY}/output"

/work/common/Rosetta/main/source/bin/rosetta_scripts.default.linuxgccrelease \
        @${FLAGS} \
        -in:file:s ${PDB} \
        -parser:protocol ${SCRIPT} \
        -out:path:all ${OUTPUT} \
        -out:suffix ${SUFFIX} \
	
