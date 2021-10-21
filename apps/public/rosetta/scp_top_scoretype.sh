#!/bin/bash

usage="$(basename "$0") [-h] [-o str] [-f str] [-r str] -- program that takes scorefile and scp's the top scoring PDB's of a scoretype from a remote server

Note: You need to be in the same directory as you want the PDBs to get copied to. A new subdirectory will be created for the PDBs.

where:
	-h    shows the help text
	-o    score_analysis options, with quotes around (ex. '-s <scorefile> -n <top_N> --scoretypes <scoretype>'). Note: only use one scoretype.
	-f    name of text file that will be created with the output of the score_analysis.py script
	-r    remote location from which the PDBs will be copied from (ex. <username>@<IP_address>:<path>/<to>/<pdbs>)"

while getopts :ho:f:r: flag
do
	case "${flag}" in
		h) echo "$usage"
			exit 1
			;;
		o) score_analysis_options=${OPTARG};;
		f) outfile_name=${OPTARG};;
		r) remote_loc=${OPTARG};;
		\?)
			echo 'Invalid option: -$OPTARG'
			echo '$usage'
			exit 1
			;;
		
	esac
done
shift $((OPTIND-1))

score_analysis.py ${score_analysis_options} > ${outfile_name}.txt && get_pdb_names_from_top_list.py ${outfile_name}.txt && scp_from_pdblist.sh -l ${outfile_name}_pdblist.txt -r ${remote_loc}

echo "Wrote files: ${outfile_name}.txt and ${outfile_name}_pdblist.txt"
echo "Copied files from ${remote_loc}"