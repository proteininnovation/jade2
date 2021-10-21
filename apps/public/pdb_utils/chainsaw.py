#! /usr/bin/env python3

import sys,os
import io
from jade2.basic.path import *

if len(sys.argv) < 3:
    sys.exit("Please pass directory for chainsaw to run on, and output directory")


pdbs = get_all_pdb_paths(sys.argv[1])
outdir = sys.argv[2]

if not os.path.exists(outdir):
    os.mkdir(outdir)

count = 0
for pdb in pdbs:
    allowable_atoms=["N","O","C","CA"]
    in_file = pdb
    #print(pdb)
    out_file = sys.argv[2]
    in_pdb = open(in_file,'r')
    out_pdb = open(outdir+"/"+os.path.basename(in_file),'w')

    for line in in_pdb:
        if not line: continue
        if line.startswith('#'): continue
        tokens = line.split()
        #print(line)
        if not tokens: continue

        if tokens[0]=="ATOM" and tokens [2] in allowable_atoms:
            line_clean = line.replace(tokens[3],"GLY")
            out_pdb.write(line_clean)

    count+=1
    if count % 10 == 0:
        print("Processed "+str(count))

    in_pdb.close()
    out_pdb.close()
print("done")