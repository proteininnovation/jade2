#!/usr/bin/env python

# Takes a text file with the score_analysis output for one scoretype and writes a scorefile with only the file names, with one name on each line.

import sys
from jade2.basic.file_functions import *

args = sys.argv
filename = args[1]

lines = get_lines_of_file(filename)

j = None
for i in range(len(lines)):
    if "By" in lines[i]:
        j = i

if j == None:
    raise ValueError("score_analysis file should have a line such as \"By <score_type>\"")

score_lines = []
for i in range(j+1, len(lines)):
    score_lines.append(lines[i].split())

pdb_names = []
for line in score_lines:
	pdb_names.append(line[len(line)-1]+".pdb")

outfile_name = filename[:-4] + "_pdblist.txt"
print("Wrote file:", outfile_name)
outfile = open(outfile_name, 'w')
outfile.writelines(add_newline_chars_to_list(pdb_names))
outfile.close()

