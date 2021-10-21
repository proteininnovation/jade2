#!/bin/bash
DIRECTORY=/home/<username>/<project_directory>
SBATCH_SCRIPT=${DIRECTORY}/multi-input_slurm_job.sbatch

for INPUT_PDB in ${DIRECTORY}/input/*.pdb
        do
        echo submitting job for ${INPUT_PDB}
        sbatch ${SBATCH_SCRIPT} ${INPUT_PDB}
        sleep 1
        done

