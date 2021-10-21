#!/usr/bin/env python3

import sys,os,re,time
from argparse import ArgumentParser
from collections import defaultdict
import xml.etree.ElementTree as ET
from xml.dom import minidom
from copy import deepcopy
from typing import *
from typing import DefaultDict

sections = ["INCLUDES", "SCOREFXNS", "SIMPLE_METRICS", "TASK_OPERATIONS",
            "PROTOCOLS", "MOVE_MAP_FACTORIES", "FILTERS", "MOVERS",
            "RESIDUE_LEVEL_TASK_OPERATIONS", "RESIDUE_SELECTORS", "OTHER", "OUTPUT"]

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml()

def read_script_vars(script_var_path: str) ->DefaultDict[str,str]:
    if not os.path.exists(script_var_path):
        exit("Script var default file not found! "+script_var_path)
    split_vars = defaultdict()
    for line in open(script_var_path, 'r').readlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        lineSP = line.split(" ")
        if len(lineSP) < 2: continue

        split_vars[lineSP[0]] = line.replace(lineSP[0], "").strip().replace('\\n', '\n').replace('\\t','\t')

    return split_vars

def parse_script_vars(local_script_vars: str) -> DefaultDict[str,str]:
    """
    Split x="y" z="b" string.
    Return a diction of vars

    """

    split_vars = defaultdict()
    SP = local_script_vars.split(' ')
    for s in SP:
        # print(s)
        sSP = s.split('=')
        # print(sSP)
        # print(sSP[0]," ",sSP[1])
        split_vars[sSP[0]] = sSP[1]
    return split_vars

def replace_script_vars(file_as_string: AnyStr, split_vars: DefaultDict[str,str]):
    """
    Replace split vars within a file - loaded as a single string.
    """
    for var in split_vars:
        # print(var)
        varS = "%%" + var + "%%"
        # print(varS)
        #print(replacements[var])
        file_as_string = file_as_string.replace(varS, split_vars[var])
    return file_as_string

def create_single_build(main, new_main):
    print("Creating non-multistage script.")
    protocols = defaultdict(list)
    for st2 in main.getroot():
        #print(st2.tag)
        rtags = []
        if st2.tag.upper() == "INCLUDES":
            for itag in st2:

                path = itag.get('path')
                print("\nincluding "+path)
                #print("Parsing "+path)

                itags[itag.tag] = itag
                ipaths[itag.tag] = path

                script_vars = itag.get('script_vars')
                blocks = itag.get('blocks')

                #Blocks that we will ONLY include.
                if blocks:
                    blocks = [x.upper() for x in blocks.split(',')]

                #Include a comment for the included module.
                comment = ET.Comment(path)
                comment.tail = '\n\t'
                new_main.getroot().append(comment)

                lines = scrub_root(open(path, 'r').read())

                # Replace any variables by pure string replacement.
                merged_vars = default_vars
                if script_vars:
                    replacements = parse_script_vars(script_vars)
                    for key in replacements:
                        merged_vars[key] = replacements[key]

                lines = replace_script_vars(lines, merged_vars)
                # Read from lines.
                subxml = ""
                try:
                    subxml = ET.ElementTree(ET.fromstring(lines))
                except Exception as e:
                    print(
                        "Included XML could not be parsed.  Please check syntax of "+path+" and try again.  Printing original error below:")
                    print(e)
                    sys.exit(1)


                total = len(subxml.getroot())
                index = 1
                #print("total", total)
                for subxmltag in subxml.getroot():
                    #print("sub", subxmltag.tag)
                    if subxmltag.tag.upper() == "PROTOCOLS":
                        index += 1
                        for stage in subxmltag:
                            protocols[itag.tag].append(stage)
                        continue

                    if blocks and subxmltag.tag.upper() not in blocks:
                        index += 1
                        print("    skipping " + subxmltag.tag.upper() + " as it is not included in blocks.")
                        continue

                    if index == total:
                        subxmltag.tail = '\n\n\t'
                        #print(subxmltag)

                    new_main.getroot().append(subxmltag)
                    index += 1

            # st2.clear()
        elif st2.tag.upper() == "PROTOCOLS":
            # print("Protocols")
            protocol_elem = ET.Element("PROTOCOLS")
            protocol_elem.tail = "\n\t"
            protocol_elem.text = "\n\n\t\t"
            new_main.getroot().append(protocol_elem)
            last = ""
            #print("working on protocols")
            for pt in st2:
                if pt.tag in protocols:
                    #print(pt.tag)
                    comment = ET.Comment(pt.tag)
                    comment.tail = '\n\t\t'
                    new_main.getroot().find('PROTOCOLS').append(comment)

                    #Include each stage individually
                    for stage_include in protocols[pt.tag]:
                        stage_include.tail = "\n\n\t\t"
                        last = stage_include
                        new_main.getroot().find('PROTOCOLS').append(stage_include)

                #Include stages from main script.
                else:
                    pt.tail = '\n\n\t\t'
                    last = pt
                    new_main.getroot().find('PROTOCOLS').append(pt)

            #Fix the tail so that the indenting is not wonky.
            last.tail = '\n\n\t'
        else:
            new_main.getroot().append(st2)
    return new_main


def scrub_root(lines):
    """
    Scrub the root tag from any script if present
    :param lines:
    :return: [str]
    """
    n = 3
    current_n = 0
    new_lines = ""
    for line in lines.split('\n'):
        if re.search('<root', line):
            current_n += 1
            continue
        elif current_n <= n and current_n != 0:
            current_n+=1
            continue
        else:
            new_lines += line+"\n"
    return new_lines

if __name__ == "__main__":

    parser = ArgumentParser("\n\nCreates a Multistage Rosetta Script (Job Definition) based on includes.\n"
                            "Remove the Common tag from any includes(modules) you use, but keep in main script. \n\n"
                            "See the xml directory for the meta_xml_example.xml script and example includes. \n"
                            "The meta script can include stages, movers, etc. \n\n"
                            "Modules are included using the <INCLUDES> syntax.  Subtags are used for each.  The name of the "
                            "tag corresponds to the name used elsewhere in the script.\n"
                            "\nEx:\n"
                            "   <INCLUDES>\n"
		                    "       <Common path=\"xmls/common_covid.xml\" blocks=\"movers,simple_metrics\"/>\n"
		                    "       <Hemlock path=\"xmls/hemlock.xml\"/>\n"
		                    "       <SC path=\"xmls/sc_design_covid.xml\" script_vars=\"decoy_per_bb=15\"/>\n"
	                        "   </INCLUDES>\n\n"
                            "\n\nSchema:\n"
                            "   blocks: \n"
                            "        If you wish to include only movers,etc from a particular script\n"
                            "        give this separated by comma. blocks=\"movers,simple_metrics\"\n"
                            "   script_vars:\n"
                            "        Give script vars for the script exactly as you would for RosettaScripts.\n"
                            "        Within the module, use %%my_var%% - and that will replaced.\n\n"
                            "\nStages:\n"
                            "   Use an individual tag such as <Hemlock/>\n"
                            "   in the protocols section to include stages in the order given from the given script. \n\n\n\n")


    parser.add_argument("script_path", help = "Path to meta script. (relative)")

    parser.add_argument("--outdir", "-d", help = "Directory to output to", default = "job_definitions")

    parser.add_argument("--outname", "-o", help = "Optional name of output.  If unset will use the base name of the input script.")

    parser.add_argument("--defaults", "-f", help = "File for script_var defaults if not given. Format is script_var space option. Use a carriage return for multi-line options ",
                        default="config/script_builder_defaults.txt")

    parser.add_argument("--skip_overall_dupe_check", '-s', help = "Skip the overall name duplication check?",
                        default = False,
                        action="store_true")

    options = parser.parse_args()

    default_vars = read_script_vars(options.defaults)

    ipaths = defaultdict()
    itags = defaultdict()

    if not os.path.exists(options.script_path):
        sys.exit("Script path "+options.script_path+" does not exist!")

    #Replace main script with any default script vars here as well.
    lines = scrub_root(open(options.script_path, 'r').read())

    # Replace any variables by pure string replacement.
    lines = replace_script_vars(lines, default_vars)
    print(lines)

    #Scrub any Root

    #main = ET.parse(options.script_path)
    main = ""
    try:
        main = ET.ElementTree(ET.fromstring(lines))
    except Exception as e:
        print("Main XML could not be parsed.  Please check syntax and try again.  Printing error below:")
        print(e)
        sys.exit(1)

    new_main = deepcopy(main)

    # print(new_main.find("Common")._children)
    if (new_main.find("Common")):
        for i in range(len(new_main.find("Common")) - 1, -1, -1):
            # print(i)
            del new_main.find("Common")[i]
    else:
        for sub in sections:
            if (new_main.find(sub)):
                 new_main.getroot().remove(new_main.find(sub))


    # new_main.find("Common")._children = []

    # root_elem = ET.Element("JobDefinitionFile"))
    # common_elem = ET.Element("Common"))

    # new_main = ET.ElementTree(root_elem)
    # print(new_main)
    # new_main.append(common_elem)
    # main.getroot().find('Common').tail = '\n\n\t'

    multi_stage = False
    protocols = defaultdict(list)
    for st1 in main.getroot():
        #print(st1.tag)
        if st1.tag.upper() == "COMMON":
            multi_stage = True
            for st2 in st1:
                # print(st2.tag)
                rtags = []
                if st2.tag.upper() == "INCLUDES":
                    for itag in st2:

                        path = itag.get('path')
                        print("\nincluding "+path)
                        # print("Parsing "+path)

                        itags[itag.tag] = itag
                        ipaths[itag.tag] = path

                        script_vars = itag.get('script_vars')
                        blocks = itag.get('blocks')

                        #Blocks that we will ONLY include.
                        if blocks:
                            blocks = [x.upper() for x in blocks.split(',')]

                        #Include a comment for the included module.
                        comment = ET.Comment(path)
                        comment.tail = '\n\t'
                        new_main.getroot().find('Common').append(comment)

                        lines = scrub_root(open(path, 'r').read())

                        # Replace any variables by pure string replacement.
                        merged_vars = default_vars
                        if script_vars:
                            replacements = parse_script_vars(script_vars)
                            for key in replacements:
                                merged_vars[key] = replacements[key]

                        lines = replace_script_vars(lines, merged_vars)
                        # Read from lines.
                        subxml = ""
                        try:
                            subxml = ET.ElementTree(ET.fromstring(lines))
                        except Exception as e:
                            print(
                                "Included XML could not be parsed.  Please check syntax of "+path+" and try again.  Printing original error below:")
                            print(e)
                            sys.exit(1)


                        total = len(subxml.getroot())
                        index = 1
                        # print("total", total)
                        for subxmltag in subxml.getroot():
                            # print("sub", subxmltag.tag)
                            if subxmltag.tag.upper() == "PROTOCOLS":
                                index += 1
                                for stage in subxmltag:
                                    protocols[itag.tag].append(stage)
                                continue

                            if blocks and subxmltag.tag.upper() not in blocks:
                                index += 1
                                print("    skipping " + subxmltag.tag.upper() + " as it is not included in blocks.")
                                continue

                            if index == total:
                                subxmltag.tail = '\n\n\t'
                                # print(subxmltag)

                            new_main.getroot().find('Common').append(subxmltag)
                            index += 1

                    # st2.clear()
                elif st2.tag.upper() == "PROTOCOLS":
                    # print("Protocols")
                    protocol_elem = ET.Element("PROTOCOLS")
                    protocol_elem.tail = "\n\t"
                    protocol_elem.text = "\n\n\t\t"
                    new_main.getroot().find('Common').append(protocol_elem)
                    last = ""
                    for pt in st2:
                        if pt.tag in protocols:
                            comment = ET.Comment(pt.tag)
                            comment.tail = '\n\t\t'
                            new_main.getroot().find('Common').find('PROTOCOLS').append(comment)

                            #Include each stage individually
                            for stage_include in protocols[pt.tag]:
                                stage_include.tail = "\n\n\t\t"
                                last = stage_include
                                new_main.getroot().find('Common').find('PROTOCOLS').append(stage_include)

                        #Include stages from main script.
                        else:
                            pt.tail = '\n\n\t\t'
                            last = pt
                            new_main.getroot().find('Common').find('PROTOCOLS').append(pt)

                    #Fix the tail so that the indenting is not wonky.
                    last.tail = '\n\n\t'
                else:
                    new_main.getroot().find('Common').append(st2)

    # print(prettify(new_main.getroot()))

    if (not multi_stage):
        new_main = create_single_build(main, new_main)

    if not os.path.exists(options.outdir):
        os.mkdir(options.outdir)

    outname= os.path.basename(options.script_path).split('.')[0]+"_full"
    if options.outname:
        outname = options.outname

    new_main.write(options.outdir+"/"+outname+'.xml')
    print("\nWrote "+options.outdir+"/"+outname+'.xml')
    time.sleep(1)
    print("\n\nChecking for duplications of tag names.\n")

    by_section_tags = defaultdict()
    all_tags = []
    for section in sections:
        by_section_tags[section] = [] #List of tag names

    current_section = "OTHER"
    line_number = 0
    for line in open(options.outdir+"/"+outname+'.xml', 'r'):
        line_number+=1
        line = line.strip()
        if not line: continue
        for section in sections:
            if (re.search(section, line)):
                current_section = section
                #print(current_section)
                break

        lineSP = line.strip(" \t\n").strip("</>").split(' ')
        if (len(lineSP) == 1): continue

        #print("LINESP: ",lineSP)
        for full_tag in lineSP:
            tagSP = full_tag.split("=")
            if tagSP[0] == "name":
                #print("tag found", full_tag)
                tag = tagSP[1]

                if not tag in all_tags:
                    #print("Adding tag name ",tag," ",full_tag)
                    all_tags.append(tag)
                    by_section_tags[current_section].append(tag)
                else:
                    if (tag in by_section_tags[current_section]):
                        print("Warning: Duplicate "+current_section +" object with tag " + tag+", " +"line number: " + repr(
                            line_number))
                        print(" ")
                    elif (not options.skip_overall_dupe_check):
                        print("Warning: Duplicate overall object with "+tag+", line number: "+repr(line_number)+" section "+current_section)
                        print(" ")
                    #print(line,"\n\n")


    print("Complete.")


