#!/usr/bin/env python3
#Author: Jared Adolf-Bryfogle

import os,sys,re
import torch, torch.nn as nn
import time
from jade2.rosetta_jade.score_util import get_dataframe_from_json_csv_pkl
from jade2.deep_learning.torch.tensor_creation import get_prottrans_tensor
from argparse import ArgumentParser
from transformers import BertModel, BertTokenizer
from jade2.basic.fasta import get_sequences_from_fasta

import pandas

def get_sequences(datafile, seq_column = "sequence_1D", test = False, test_size=100):
    """
    Read DF, return sequences.  So we do not hold the DF in memory.
    We could only read csv and grab the sequence column in the future.
    :return:
    """
    if datafile.endswith(".csv"):
        df = pandas.read_csv(datafile, usecols=[seq_column])
    else:
        df = get_dataframe_from_json_csv_pkl(options.datafile)
    print("Read DF")

    if seq_column not in df.columns:
        sys.exit("Column not found in dataframe:"+options.seq_column)

    if test:
        return df[seq_column][:test_size].to_numpy()
    else:
        return df[seq_column].to_numpy()

if __name__ == "__main__":
    parser = ArgumentParser("This script creates prottrans embeddings from a dataframe column of sequences using multiple CPUs or GPU if available."
                            "Annotate those sequences using the Sequence metric in Rosetta. Expand to use FASTA")

    parser.add_argument("--datafile", '-s',
                        help = "The CSV/JSON/PICKLE file that contains the data. Must be .pkl for pickle reading.")

    parser.add_argument("--fasta", '-f',
                        help = "A fasta file to use for sequences")

    parser.add_argument("--seq_column", '-q',
                        help = "Sequence column of the data",
                        default = "sequence_1D"
                        )

    parser.add_argument("--outfile", '-o',
                        help = "Output pickle file",
                        default = "protrans_embeddings.pt")

    parser.add_argument("--cpus", '-c',
                        help = "Number of CPUs to use if GPU not present.  Default is Total-1")

    parser.add_argument("--test", '-t',
                        help = "Test mode. Runs on 100 sequences. Outputs timings.",
                        default = False,
                        action = "store_true")

    parser.add_argument("--test_size",
                        help = "Number of sequences to use for test.",
                        default = 100,
                        type = int)

    parser.add_argument("--chunk_size",
                        help = "Chunk size for each batch.  Default is one sequence at a time. Useful if running on multiple CPUs instead of GPU",
                        default = 1,
                        type = int)

    parser.add_argument("--save_size",
                        help = "The number to dump models at.  Otherwise, RAM will keep increasing. If given 0, we will save the full tensor at the end instead.",
                        default = 10000,
                        type = int)

    parser.add_argument("--pad_with_seq",
                        help = "Pad with specific residues.  Pad syntax is AAA-VVV, where - is the primary sequence")

    options = parser.parse_args()

    if options.fasta and options.datafile:
        sys.exit("Cannot pass both a fasta and datafile.   Choose one.")

    cpus = 1
    if not options.cpus:
        cpus = os.cpu_count() -1
    else:
        cpus = options.cpus

    test_size = options.test_size

    #print(sep_sequences)

    if options.datafile:
        sequences = get_sequences(options.datafile, options.seq_column, options.test, test_size=test_size)
    elif options.fasta:
        sequences, names = get_sequences_from_fasta(options.fasta)
        if options.test:
            sequences = sequences[:test_size]
    else:
        sys.exit("Must pass either datafile or fasta to load sequences")

    print("NSequences:",len(sequences))
    i = 1

    if options.pad_with_seq:
        new_sequences = []
        for seq in sequences:
            new_seq = options.pad_with_seq.replace('-', seq)
            new_sequences.append(new_seq)
        sequences = new_sequences

    #Chunk the sequences.
    chunked_sequences = [sequences[i:i + options.chunk_size] for i in range(0, len(sequences), options.chunk_size)]
    print("Chunks: ", len(chunked_sequences))
    for x in chunked_sequences:
        print("c", len(x))

    max_length = max([len(x) for x in sequences])
    #[print(len(x)) for x in sequences]

    tokenizer = BertTokenizer.from_pretrained('Rostlab/prot_bert_bfd', do_lower_case=False )
    prottrans_model = BertModel.from_pretrained("Rostlab/prot_bert_bfd")
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    if device == 'cpu' and cpus>1:
        torch.set_num_threads(cpus)
        prottrans_model = nn.DataParallel(prottrans_model)

    prottrans_model = prottrans_model.to(device)
    prottrans_model = prottrans_model.eval()


    embeddings = []
    save_num = 1
    print("Starting")
    start_time = time.time()

    total_complete = 0
    i=0

    for s in chunked_sequences:


        sep_sequences = []
        for seq in s:
            i+=1
            # print("Chunk_size", len(s))
            if not options.test:
                if not i % 500: print(i)
            else:
                if not i % 10: print(i)

            new_seq = seq
            print(len(seq), max_length)

            if len(seq) < max_length:
                for x in range(max_length - len(seq)):
                    new_seq+="X"

            assert(len(new_seq) == max_length)
            sep_sequences.append(" ".join([x for x in new_seq]))

        #print(sep_sequences)
        clean = [re.sub(r"[UZOB]", "X", sequence) for sequence in sep_sequences]
        ids = tokenizer.batch_encode_plus(clean, add_special_tokens=True, pad_to_max_length=True)
        input_ids = torch.tensor(ids['input_ids']).to(device)
        attention_mask = torch.tensor(ids['attention_mask']).to(device)
        print("Running chunk.")
        with torch.no_grad():
            embedding = prottrans_model(input_ids=input_ids,attention_mask=attention_mask)[0]
            embeddings.append(embedding.cpu().detach())
        total_complete += len(sep_sequences)

        print(f"Chunk done, total_complete = {total_complete}")
        if options.save_size and not i % options.save_size:
            embeddings_t = torch.cat(embeddings)
            torch.save(embeddings_t, options.outfile+str(save_num))
            embeddings = []
            save_num+=1


    if options.test:
        embeddings_t = torch.cat(embeddings)
        print(embeddings_t.shape)

        print("--- %.4s seconds ---" % (time.time() - start_time))
        torch.save(embeddings_t, "test_embeddings.pt")
        exit()
    else:
        embeddings_t = torch.cat(embeddings)
        min_time = (time.time() - start_time)/60.0
        print("--- %.4s minutes ---" % (min_time))
        if save_num == 1:
            out = options.outfile
        else:
            out = options.outfile+str(save_num)

        torch.save(embeddings_t, out)
        print("Model saved to ",options.outfile)





