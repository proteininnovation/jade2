__author__ = 'jadolfbr'


aaweights = {
    'A' : 71.09,  # alanine
    'R' : 156.19, # arginine
    'D' : 114.11, # aspartic acid
    'N' : 115.09, # asparagine
    'C' : 103.15, # cysteine
    'E' : 129.12, # glutamic acid
    'Q' : 128.14, # glutamine
    'G' : 57.05,  # glycine
    'H' : 137.14, # histidine
    'I' : 113.16, # isoleucine
    'L' : 113.16, # leucine
    'K' : 128.17, # lysine
    'M' : 131.19, # methionine
    'F' : 147.18, # phenylalanine
    'P' : 97.12,  # proline
    'S' : 87.08,  # serine
    'T' : 101.11, # threonine
    'W' : 186.12, # tryptophan
    'Y' : 163.18, # tyrosine
    'V' : 99.14   # valine
}

def calculate_mw(sequence: str, kda= True) -> int:
    """
    Calculate the approx molecular weight of a sequence
    :param sequence:
    :return:
    """
    out = 0
    for aa in sequence:
        out+=aaweights[aa]
    if kda:
        out = out/1000.0

    return out