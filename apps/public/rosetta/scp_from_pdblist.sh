#!/bin/bash

usage="$(basename "$0") [-h] [-l str] [-r str] -- program that takes a pdblist and scp's the PDBs from a remote server

Note: You need to be in the same directory as you want the PDBs to get copied to. A new subdirectory will be created for the PDBs.

where:
	-h    shows the help text
	-l    pdblist text file. Note: should have ".txt" extension
	-r    remote location from which the PDBs will be copied from (ex. <username>@<IP_address>:<path>/<to>/<pdbs>)"

while getopts :hl:r: flag
do
	case "${flag}" in
		h) echo "$usage"
			exit 1
			;;
		l) pdblist=${OPTARG};;
		r) remote_loc=${OPTARG};;
		\?)
			echo 'Invalid option: -$OPTARG'
			echo '$usage'
			exit 1
			;;
	esac
done
shift $((OPTIND-1))

SUB_DIR=${pdblist%.txt}
CURR_DIR=$(pwd)
mkdir $CURR_DIR/$SUB_DIR
NEW_DIR=$CURR_DIR/$SUB_DIR
echo "Made new directory $NEW_DIR"

while read p;
do scp ${remote_loc}/$p $NEW_DIR;
done < ${pdblist}
