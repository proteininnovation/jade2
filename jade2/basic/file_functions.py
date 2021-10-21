def get_lines_of_file(filename):
    """
    returns a list of pdb file names given a PDB list
    
    :param filename: name of PDB list file
    """
    file = open(filename)
    lines = file.readlines()
    file.close()
    stripped_lines = []
    for line in lines:
        line = line.strip()
        stripped_lines.append(line)
    return stripped_lines

def repeat_lines_in_file(filename, n, outfile_name, outpath):
    file = open(filename)
    lines = file.readlines()
    file.close()
    new_lines = []
    for line in lines:
        if line != "\n":
            for i in range(n):
                new_lines.append(line)
    for i in range(len(new_lines)):
        if "\n" not in new_lines[i]:
            new_lines[i] += "\n" 
    name = outfile_name + "-" + str(n) + ".txt"
    outfile = open(outpath + name, 'w')
    outfile.writelines(new_lines)
    outfile.close()
    print("Wrote file:", name)
    
def add_newline_chars_to_list(list_of_filelines):
    """
    adds a newline character to each string in a list
    
    :param list_of_filelines: list of strings
    :return: list of strings
    """
    new_filelines = []
    for i in range(len(list_of_filelines)):
        new_filelines.append(list_of_filelines[i] + "\n")
    return new_filelines

def get_file_name_without_path(filename_with_path):
    last_slash = filename_with_path.rfind("/")
    dot = filename_with_path.rfind(".")
    filename = filename_with_path[last_slash + 1:dot]
    return filename