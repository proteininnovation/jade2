
import os
import sys
from collections import defaultdict


if len(sys.argv) < 2 or sys.argv[1] =="--help": sys.exit("Simple script to remove redunant lines in a PDB file. Argument=path_to_pdb.")

lines = open(sys.argv[1], 'r')
out = open("non_redun.txt", 'w')
print("Writing 'non_redun.txt")

all_lines = defaultdict()
for line in lines:
    if line in all_lines:
        continue
    else:
        out.write(line)
        all_lines[line]=1
out.close()
print("done")
