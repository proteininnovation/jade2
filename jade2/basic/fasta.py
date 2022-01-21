#Author Jared Adolf-Bryfogle

import gzip
import os
import random
import sys
import logging
from pathlib import Path
from typing import Union, DefaultDict, List, Tuple, IO, AnyStr
from collections import defaultdict

from Bio.PDB.Polypeptide import PPBuilder
from Bio.PDB.Structure import Structure
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from jade2.basic.path import *
from weblogo import *

from jade2.basic.sequence.ClustalRunner import ClustalRunner


def get_sequences_from_fasta(fasta):
    """
    Simple function to obtain a list of sequences from a fasta file.
    Returns list of sequences and a list of names
    :param fasta:
    :return:
    """
    sequences = []
    names = []
    for line in open(fasta, 'r'):
        line = line.strip()
        if not line: continue
        if line.startswith('>'): names.append(line.strip('>'))
        else:
            sequences.append(line)

    return sequences, names

########  Fasta Input  ######

def get_label_from_fasta(fasta_path: Union[Path, str]) -> str:
    """
    Gets the first chainID found - Should be a single chain fasta file.
    """
    for record in SeqIO.parse(str(fasta_path), format='fasta'):
        label = record.id
        return label

def get_sequence_from_fasta(fasta_path: Union[Path, str], label: str) -> str:
    """
    return the sequence from a fasta file by feeding it a particular label
    """
    for record in SeqIO.parse(str(fasta_path), format='fasta'):
        logging.info("Getting sequence from "+fasta_path)
        name = record.id
        if name==label:
            seq = str(record.seq)
            return seq

def get_single_sequence_from_fasta(fasta_path: Union[Path, str]) -> str:
    """
    return the sequence from a fasta file by feeding it a particular label
    """
    for record in SeqIO.parse(str(fasta_path), format='fasta'):
        logging.info("Getting sequence from "+fasta_path)
        name = record.id
        seq = str(record.seq)
        return seq

def read_header_data_from_fasta(fasta_path: Union[Path, str]) -> DefaultDict[str, Tuple[str,str,str,str]]:
    """
    Reads > from fasta (PDBAA) and returns a defaultdict of
    pdb_chain: [method, residues, resolution, R factor]
    """
    result = defaultdict()

    for record in SeqIO.parse(str(fasta_path), format='fasta'):
        name = record.name
        lineSP = name.split()
        lis = [lineSP[2], lineSP[1], lineSP[3], lineSP[4]]
        result[lineSP[0]] = lis

    return result


########  Fasta Output #########

def write_fasta(sequence: Seq, label: str, HANDLE: IO[AnyStr]):
    """
    Writes a fasta with a sequence, chain, and open FILE handle.
    FULL Sequence on one line seems to be fine with HMMER3.
    """
    record = SeqRecord(sequence, id=label)
    SeqIO.write(record, HANDLE, "fasta")

def fasta_from_sequences(sequences: List[str], outdir: Union[Path, str], outname: Union[Path, str]) -> str:
    """
    Output a general fasta, with tag being 1_outname etc.
    Use write_fasta for more control.
    Returns path to Fasta File written
    """
    if not os.path.exists(str(outdir)):
        os.mkdir(str(outdir))
    outpath = str(outdir)+"/"+str(outname)+".fasta"
    i=1

    records = []
    for sequence in sequences:
        logging.info("Creating fasta from sequence: "+str(sequence))
        records.append(SeqRecord(sequence, id=repr(i)+"_"+str(outname)))
        i += 1
    for record in records:
        SeqIO.write(record, outpath, "fasta")

    return outpath

def chain_fasta_files_from_biostructure(structure: Structure, prefix: str, outdir: Union[Path, str]) -> List[str]:
    """
    Returns paths of fasta files written
    """

    ppb = PPBuilder(radius=float(1000))
    if not os.path.exists(str(outdir)):
        os.mkdir(str(outdir))

    model = structure[0]
    fasta_files = []
    for bio_chain in model:
        seq = ''
        chainmodel = ppb.build_peptides(bio_chain, aa_only=False)
        if renumbering.get_chain_length(bio_chain) == 0:
            continue
        for aa in chainmodel:
            seq = seq + aa.get_sequence()
        chain = bio_chain.id
        outname = prefix+"_"+chain+".fasta"
        HANDLE = outdir+"/"+outname
        fasta_files.append(outdir+"/"+outname)
        write_fasta(seq, chain, HANDLE)

    return fasta_files

def chain_fasta_from_biostructure(structure: Structure, outname: Union[Path, str], outdir: Union[Path, str]) -> str:
    """
    Creates a single fasta from biopython structure, split by individual chains.
    Returns output file path
    """

    ppb = PPBuilder(radius=float(1000))
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    model = structure[0]
    outfilename = str(outdir)+"/"+str(outname)+".fasta"
    HANDLE = open(outfilename, 'w')
    for bio_chain in model:
        seq = ''
        chainmodel = ppb.build_peptides(bio_chain, aa_only=False)
        for aa in chainmodel:
            seq = seq+aa.get_sequence()
        write_fasta(seq, bio_chain.id, HANDLE)

    return outfilename

def split_fasta_from_fasta(fasta_path: Union[Path, str], prefix: str, outdir: Union[Path, str]) -> List[str]:
    """
    If we have a multiple fasta sequence, we split it into idividual files.  Makes analysis easier.
    Returns list of paths for each fasta
    """
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    INFILE = open_file(fasta_path, 'r')
    chains = dict()
    found = False
    id = random.getrandbits(128)
    chain_num = 0
    n = ""
    for line in INFILE:
        if line[0]=='>':
            chain_num +=1
            found = True
            n = "chain_"+repr(id)+"_"+repr(chain_num)

            head = "_".join(line.split()) +"\n"
            chains[n] = head
            continue
        elif line[0] == '#':
            continue
        if found:
            chains[n] = chains[n]+line

    fasta_files = []
    for chain in chains:
        outname = prefix+"_"+chain+".fasta"
        #print outname
        OUTFILE = open(str(outdir)+"/"+str(outname), 'w')
        OUTFILE.write(chains[chain])
        OUTFILE.close()
        fasta_files.append(str(outdir)+"/"+str(outname))

    logging.info("FASTA file split.")
    INFILE.close()

    return fasta_files

########  Etc ###########

# Need to have clustal omega installed

def output_weblogo_for_sequences(sequences: List[str], outdir: str, outname: str, tag: str = "Dunbrack Lab - Antibody Database Team"):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    fasta_outdir = outdir+"/fastas"

    fasta_path = fasta_from_sequences(sequences, fasta_outdir, outname)
    clustal_runner = ClustalRunner(fasta_path)
    clustal_runner.set_extra_options("--force")
    clustal_runner.output_alignment(outdir+"/clustal", outname+".clu")

    clustal_path = outdir+"/clustal/"+outname+".clu"

    weblogo_dir = outdir+"/weblogos"

    output_weblogo(clustal_path, weblogo_dir, outname, tag)

def output_weblogo_for_fasta(fasta_path: Union[Path, str], outdir: str, outname: str, tag: str = "Dunbrack Lab - Antibody Database Team"):
    clustal_runner = ClustalRunner(fasta_path)
    clustal_runner.set_extra_options("--force")
    clustal_runner.output_alignment(outdir+"/clustal", outname+".clu")

    clustal_path = outdir+"/clustal/"+outname+".clu"

    weblogo_dir = outdir+"/weblogos"

    output_weblogo(clustal_path, weblogo_dir, outname, tag)

def output_weblogo(alignment_path: str, outdir: str, outname: str, tag: str = "Dunbrack Lab - Antibody Database Team"):
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    MSA_IN = open_file(alignment_path)
    seqs = read_seq_data(MSA_IN)
    data = LogoData.from_seqs(seqs)
    options = LogoOptions()

    #Weblogo Options
    options.logo_title = outname
    #options.fineprint = datetime.datetime.now().strftime('%b-%d-%G')
    options.creator_text = tag
    options.show_fineprint = False
    options.resolution = 900
    options.number_interval = 1
    options.scale_width = True
    options.unit_name='probability'
    options.color_scheme=std_color_schemes["charge"]
    #options.color_scheme=std_color_schemes["hydrophobicity"]

    format = LogoFormat(data, options)
    LOGO_OUT = open(outdir+"/"+outname+"_weblogo.png", 'wb')
    png_bytes = png_formatter( data, format) # LOGO_OUT)
    LOGO_OUT.write(png_bytes)

    MSA_IN.close()
    LOGO_OUT.close()

