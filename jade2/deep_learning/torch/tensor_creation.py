import pandas
import torch
import torch.nn as nn
import numpy as np
import re
from torch.nn.utils.rnn import pad_sequence
from transformers import BertModel, BertTokenizer
import torch.nn.functional as F
from typing import List
from jade2.basic import restype_definitions as resd
from collections import defaultdict
from sklearn.model_selection import train_test_split

aa_codes = resd.RestypeDefinitions().get_all_one_letter_codes()


def split_data_for_train_val_test_by_bins(dd: pandas.DataFrame, column: str, max: float, range=.25):
    """
    Splits data evenly across train,val,test. If n of that range is <=2, add to training data as it can't be split into thirds.
    Make sure range is large enough to prevent most of that.

    Returns total,train,val,test dataframes.

    :param df:
    :param column:
    :param range:
    :return:
    """
    n = range
    total = 0
    train = []; test = []; val = []
    for i in np.arange(0, max+n+n, n):
        if i == 0: continue
        #print("Range:", i-n, "-",i)
        d = dd[(dd[column]<i) & (dd[column] >= i-n)]
        #print(i, len(d))
        total+=len(d)

        if len(d) != 0:
            if len(d) <= 2:
                train.append(d)
                continue

            X_train, X_test = train_test_split(d, test_size=0.2, random_state=27)
            X_train, X_val = train_test_split(X_train, test_size=.075, random_state = 27)
            train.append(X_train)
            test.append(X_test)
            val.append(X_val)

    return total, pandas.concat(train), pandas.concat(val), pandas.concat(test)

def create_2D_tensor_from_score_data(df: pandas.DataFrame, metrics: List, seq_column="sequence_1D", pady = True, padxy = True, scale = False, standardize=False) -> torch.Tensor:
    """
    Create a 2D tensor from a dataframe using specific metrics and the sequence
    pad y adds padding up to the length of the largest sequence using pytorch pad_sequence
    Pad xy adds an xy padding like Prottrans first.
    """

    decoy_tensors =  []
    #print(metrics)

    #We make the metrics sorted so that when we serve the models eventually, they are in the same order for predictions
    sorted_metrics = sorted(metrics)
    for index, row in df.iterrows():

        s = row[seq_column]
        features = []
        for metric in sorted_metrics:
            #print("Loading ", metric)
            #print(row[metric])
            energies = {int(x.split(':')[0]) : float(x.split(':')[1]) for x in row[metric].split(',')}

            #Make sure all values are present. Not all metrics output zeros.
            data_2d = []
            if padxy:
                data_2d.append(0.0)
            for i in range(1, len(s)+1):
                if not i in energies:
                    data_2d.append(0.0)
                else:
                    t = energies[i]
                    data_2d.append(t)

            if padxy:
                data_2d.append(0.0)

            features.append(data_2d)

        dt = torch.tensor(features, dtype=torch.float32)

        #Permute causes everything to be super slow if its not contiguous.
        dt = dt.permute(1, 0).contiguous()
        #print(dt.shape)
        decoy_tensors.append(dt)

    #Batch first makes it so you don't have to permute - but you remove the padxy column.
    dt = pad_sequence(decoy_tensors)
    #print(dt.shape)
    dtp = dt.permute(1,2,0).contiguous()

    if scale:
        if standardize:
            means = dtp.mean(dim=[0,2], keepdim=True)
            stds = dtp.std(dim=[0,2], keepdim=True)
            dtp = (dtp - means) / stds
        else:
            dtp=F.normalize(dtp,p=2, dim=1)
    return dtp


def embed_seq(sequence, tokenizer, prottrans_model, device="cpu"):
    """
    Embed a single sequence from the tokenizer and prottrans model.
    """
    sequences = [sequence]
    sep_sequences = []
    for seq in sequences:
        sep_sequences.append(" ".join([x for x in seq]))
    #print(sep_sequences)

    clean = [re.sub(r"[UZOB]", "X", sequence) for sequence in sep_sequences]
    #print(clean)

    ids = tokenizer.batch_encode_plus(clean, add_special_tokens=True, pad_to_max_length=True)
    input_ids = torch.tensor(ids['input_ids']).to(device)
    attention_mask = torch.tensor(ids['attention_mask']).to(device)
    with torch.no_grad():
        embedding = prottrans_model(input_ids=input_ids,attention_mask=attention_mask)[0]
        print(embedding.shape)

    return embedding

def get_prottrans_tensor(sequences: List[str], cpu_cores=1) -> torch.Tensor:
    """
    Create a prottrans tensor using prot bert bfd.
    If GPU is available, will use that.
    Otherwise we run in parellel with the given number of CPUs.
    Be warned - this is SLOW because we are creating the model and moving everytime.
    This function works, but is NOT recommended.
    """
    #make the sequences into a list of lists.
    tokenizer = BertTokenizer.from_pretrained('Rostlab/prot_bert_bfd', do_lower_case=False )
    prottrans_model = BertModel.from_pretrained("Rostlab/prot_bert_bfd")
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    if device == 'cpu' and cpu_cores>1:
        torch.set_num_threads(cpu_cores)
        prottrans_model = nn.DataParallel(prottrans_model)

    prottrans_model = prottrans_model.to(device)
    prottrans_model = prottrans_model.eval()

    sep_sequences = []
    for seq in sequences:
        sep_sequences.append(" ".join([x for x in seq]))
    #print(sep_sequences)

    clean = [re.sub(r"[UZOB]", "X", sequence) for sequence in sep_sequences]
    ids = tokenizer.batch_encode_plus(clean, add_special_tokens=True, pad_to_max_length=True)
    input_ids = torch.tensor(ids['input_ids']).to(device)
    attention_mask = torch.tensor(ids['attention_mask']).to(device)
    with torch.no_grad():
        embedding = prottrans_model(input_ids=input_ids,attention_mask=attention_mask)[0]
    return embedding

def get_onehot_encoded_sequence_tensor(df: pandas.DataFrame, seq_column = "sequence_1D", padxy = True, pady = True) -> torch.Tensor:
    """
    Get a one-hot encoded sequence tensor for the dataframe.
    Tensor is shape batch,one-hot,residues

    There are 21 residues for one-hot (which treats all noncanonicals as X at the end.)

    :param df:
    :param seq_column:
    :param padxy:
    :param pady:
    :return:
    """
    ones = resd.RestypeDefinitions().get_all_one_letter_codes()
    ones.append('X')

    all_sequences = []
    for sequence in df[seq_column]:
        onehot_sequence = []
        if padxy:
            onehot_sequence.append(np.zeros(len(ones)))

        for s in sequence:
            if s in ['U','Z','O','B']: s = 'X'
            onehot_array = get_onehot_list(s, ones)
            #print(onehot_array)
            onehot_sequence.append(onehot_array)

        if padxy:
            onehot_sequence.append(np.zeros(len(ones)))

        all_sequences.append(torch.tensor(onehot_sequence, dtype = torch.float32))

    if pady:
        st = pad_sequence(all_sequences)
    else:
        st = torch.cat(all_sequences)

    #Pytorch wants channels to go in dim1.
    #print(all_sequences)

    st = st.permute(1, 2, 0).contiguous()
    return st

def get_onehot_list(val, labels: List) -> np.ndarray:
    """
    Used for manual embedding of one-hot. If val not in labels, will return a list of zeros.
    """

    if val in labels:
        zeros = np.zeros(len(labels))
        zeros[labels.index(val)] = 1.0
        return zeros
    else:
        return np.zeros(len(labels))
