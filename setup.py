#!/usr/bin/env python3
import argparse, os, re
from pathlib import Path



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script will setup symlinks in the bin directory to apps.")

    parser.add_argument("--all", help="Create links for all pilot apps?", default=False, action="store_true")
    parser.add_argument("--only_pilot", help="Only this particular pilot directory. Not a path.  Only name of pilot directory.", default="")
    parser.add_argument("--create_app_readme", help = "Create (or override) the readme with application information.", default=False, action="store_true")

    options = parser.parse_args()

    bin_dir = "bin"
    bin_docs = "bin_docs"
    pilot_apps = Path("apps/pilot")
    public_apps = Path("apps/public")

    if not os.path.exists(bin_dir): os.mkdir(bin_dir)
    if not os.path.exists(bin_docs): os.mkdir(bin_docs)

    base = open('base_readme.md', 'r').readlines()
    base.append("\n\n")
    base.append("# Application Docs\n")
    base.append("------------------\n\n")
    print("Copying scripts for public apps")

    for d in public_apps.glob("*"):
        if d.name==".DS_Store": continue
        if d.name=="__init__.py": continue

        base.append('\n## '+str(d.parts[-1]).capitalize() + "\n")
        base.append('-' * len(str(d.parts[-1])) + "\n\n")

        for file in d.rglob("*.py"):
            if re.search("__init__.py", str(file)): continue

            sym = bin_dir+"/"+file.name
            os.system('ln -s '+os.path.abspath(str(file))+" "+sym)
            if options.create_app_readme:
                bin_doc = bin_docs+"/"+file.name.replace('.py', '.txt')
                cmd = './'+sym+' --help > '+ bin_doc
                #print(cmd)
                os.system(cmd)

                base.append('### '+file.name + "\n\n")
                base.append("\n```")
                base.extend(open(bin_doc).readlines())
                base.append("```")
                base.append('\n\n')

        for file in d.rglob("*.sh"):
            sym = bin_dir+"/"+file.name
            os.system('ln -s '+os.path.abspath(str(file))+" "+sym)
            if options.create_app_readme:
                bin_doc = bin_docs+"/"+file.name.replace('.sh', '.txt')
                cmd = './'+sym+' --help > '+ bin_doc
                #print(cmd)
                os.system(cmd)

                base.append('### '+file.name + "\n\n")
                base.append("\n```")
                base.extend(open(bin_doc).readlines())
                base.append("```")
                base.append('\n\n')

    pilot_dirs=[]
    for d in pilot_apps.glob("*"):
        #print(d)
        #print(d.parts[-1])
        #print(options.only_pilot)
        if not os.path.isdir(d): continue
        if options.all:
            pilot_dirs.append(d)
        elif options.only_pilot and d.parts[-1] == options.only_pilot:
            pilot_dirs.append(d)
        else:
            continue

    for pilot in pilot_dirs:
        print("Copying scripts for " +pilot.name + " pilot applications")
        for file in pilot.rglob("*.py"):

            if re.search("__init__.py", str(file)): continue
            sym = bin_dir+"/"+file.name
            os.system('ln -s ' + os.path.abspath(str(file)) + " " + sym)

    #export PYTHONPATH =$PYTHONPATH: / Users / jadolfbr / Documents / projects / jade2 / jade2
    #export PATH =$PATH: / Users / jadolfbr / Documents / projects / jade2 / bin
    print("\n## Instructions for use: ##")
    print("\nIf you have not already, please add the following to your shell rc file or run before using jade2:\n")
    print("export PYTHONPATH=$PYTHONPATH:"+str(Path.cwd()))
    print("export PATH=$PATH:"+str(Path.cwd())+"/bin")

    if options.create_app_readme:
        OUT = open("README.md", 'w')
        for line in base:
            OUT.write(line)
        OUT.close()