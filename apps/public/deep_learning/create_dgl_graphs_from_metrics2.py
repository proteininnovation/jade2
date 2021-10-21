#!/usr/bin/env python3

import torch
import dgl
import time
from jade2.rosetta_jade import get_dataframe_from_json, get_dataframe_from_json_or_csv
from jade2.deep_learning.torch.tensor_creation import create_2D_tensor_from_score_data, get_onehot_encoded_sequence_tensor
from jade2.basic import *
from jade2.deep_learning.graphs import *
from jade2.deep_learning import one_body_metrics_all
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from jade2.deep_learning.torch.tensor_creation import get_prottrans_tensor

if __name__ == "__main__":
    parser = ArgumentParser("Creates and saves a list of DGL graphs using metrics for use in DGL GCNs", formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--csv", "-c",
                        help="Input CSV file. Will read if pickled data is not present. ",
                        default = "data/scores_w_stability_2D_3D.csv")

    parser.add_argument("--outgraph", '-o',
                        help = "The name of the output graph pickle. ",
                        default = "data/dgl_graph.pkl")


    parser.add_argument("--test",
                        help = "Only do the first 100 batches",
                        default = False,
                        action = "store_true")

    parser.add_argument("--out_dir", "-d",
                        help = "Output directory for temp files.",
                        default = "graph_data")

    parser.add_argument("--concat",
                        help = "Save one graph? Or every 10k?",
                        default = False,
                        action = "store_true")

    parser.add_argument("--cpus",
                        help = "CPUS for prottrans embeddings. ",
                        default = 1,
                        type = int)

    features = parser.add_argument_group("Graph Features", "Features that will go into the final graph")

    features.add_argument("--contact_feature", '-m',
                          help = "metric to use for contact map (graph) generation. Typical: CB_pair_distance_3D and total_pair_energy_3D",
                          default = 'CB_pair_distance_3D')

    features.add_argument("--onehot",
                          help = "Use one-hot for node features.  ",
                          default = False,
                          action = "store_true")

    features.add_argument("--prottrans",
                          help = "Use prottrans for node features.  Will do this on the fly now",
                          default = False,
                          action = "store_true")

    features.add_argument("--onebody_metrics",
                          help = "Use one-body metrics as additional node embeddings. ",
                          default = False,
                          action="store_true")

    features.add_argument("--set_edge_features",
                          help = "Override defaults(energy_pair_terms + CB_pair_metric). Use this option to give specific edge features to use (Comma separated, no space).  "
                                 "If this is a file, will read and parse the file as edge-feature per line. ")

    features.add_argument("--set_node_features",
                          help = "Override defaults(all_one_body). Use this option to give specific node features to use from the input CSV data. (Comma separated, no space) "
                                 "If this is a file, will read and parse the file as node-feature per line.")

    features.add_argument("--seq_column",
                          help = "The sequence column in the csv file. ",
                          default = 'sequence_1D')

    features.add_argument("--covalent_edge_features",
                          help = "Add a one-hot encoding of covalent edge features? [1,0] is covalent",
                          default = False,
                          action = "store_true")

    features.add_argument("--primary_sequence_separation_features",
                          help = "Encode the distance between primary sequence as edge features.  "
                                 "For local interactions, this should give the model some idea of primary sequence."
                                 "Note that for now, these are not symmetric - and will give the model some non-symmetry from sequence "
                                 "In that 0->1 is not the same as 1->0. Perhaps abs(distance) is better, but we'll see I guess.",

                          default = False,
                          action = "store_true")

    options = parser.parse_args()


    onehot = options.onehot
    prottrans = options.prottrans
    use_one_body_metrics = options.onebody_metrics
    seq_column = options.seq_column

    #Parse any specific node and edge features.
    edge_features = []
    node_features = one_body_metrics_all


    ########################################
    ####         Setup Features      #######
    ########################################

    if options.set_edge_features:
        if os.path.exists(options.set_edge_features):
            for line in open(options.set_edge_features, 'r'):
                line = line.strip()
                if not line: continue
                if line.startswith("#"): continue

                edge_features.append(line)
        else:
            edge_features = sorted([x.strip() for x in options.set_edge_features.split(',')])

    if options.set_node_features:
        if os.path.exists(options.set_node_features):
            for line in open(options.set_node_features, 'r'):
                line = line.strip()
                if not line: continue
                if line.startswith("#"): continue

                node_features.append(line)
        else:
            node_features = sorted([x.strip() for x in options.set_node_features.split(',')])


    outdir = options.out_dir
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    df = get_dataframe_from_json_or_csv(options.csv, options.test)

    if not options.seq_column in df.columns:
        sys.exit("Sequence column " +options.seq_column+" not found in csv data!")

    distance_metric_cutoffs = None



    ##########################
    ### Write out Features ###
    ##########################

    if not edge_features:

        energy_metrics = sorted([c for c in df.columns if c.endswith('pair_energy_3D')])
        distance_metrics = sorted(['CB_pair_distance_3D'])
        distance_metric_cutoffs = {c : 7.0 for c in distance_metrics}
        print(repr(distance_metric_cutoffs))
        edge_features = energy_metrics+distance_metrics

    print("node_features: ", node_features)
    print("edge_features: ", edge_features)

    if not os.path.exists(options.outgraph+"_features.txt"):
        out_feat = open(options.outgraph+"_features.txt", 'w')
        out_feat.write("NODE_FEATURES : "+str(node_features)+'\n')
        out_feat.write("EDGE_FEATURES : "+str(edge_features)+'\n')
        out_feat.write("COVALENT_EDGE_ENCODING :"+str(options.covalent_edge_features)+'\n')
        out_feat.write("PRIMARY_SEQ_ENCODING :"+str(options.primary_sequence_separation_features)+"\n")
        out_feat.close()



    #############################################
    ####  Create Node/Edge Features + Graph  ####
    #############################################

    graph_list = []
    save_num = 1
    print("Starting graph generation")
    for i in range(df.shape[0]):
        print(i)
        if not i % 200 :
            print(i)

        edge_data = get_edge_data_as_dict(df.iloc[i:i+1], edge_features, distance_metric_cutoffs)

        data_t= create_2D_tensor_from_score_data(df.iloc[i:i+1], one_body_metrics_all, padxy=False, scale=False, standardize=False)
        #print("2d_Data", data_t.shape)
        #print("Created 2D tensor")

        if not prottrans:
            seq_t = get_onehot_encoded_sequence_tensor(df.iloc[i:i+1], padxy=False)

        else:
            seq_t = get_prottrans_tensor([str(df[options.seq_column][i])], options.cpus)

            #Prottrans pads the X and Y of the protein. We need to remove that.
            seq_t = seq_t[:,1:seq_t.shape[1] - 1]
            seq_t = seq_t.permute(0, 2, 1).contiguous()
            #print("Loaded protrans")

        #print("SEQ", seq_t.shape)

        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        seq_t = seq_t.to(device)
        data_t = data_t.to(device)

        if use_one_body_metrics and (prottrans or onehot):
            all_node_t = torch.cat([data_t, seq_t], 1)
        elif use_one_body_metrics:
            all_node_t = data_t
        elif prottrans or onehot:
            all_node_t = seq_t
        else:
            sys.exit("You will need some node features for the graph convolution to run properly!")

        all_node_t = all_node_t.permute(0, 2, 1).contiguous()
        #print("Loaded sequence data")

        ### Create the Graph ###
        g = create_and_featurize_graph_fast(edge_data[0],  edge_features, all_node_t[0], len(df[seq_column][i]),
                                                contact_map_metric=options.contact_feature,
                                                covalent_edge_features=options.covalent_edge_features,
                                                primary_sequence_separation=options.primary_sequence_separation_features)

        graph_list.append(g)

        if not i % 10000 and not options.concat:
            save_pickle(graph_list, options.outgraph+str(save_num))
            graph_list = []
            save_num+=1

    if options.concat:
        save_pickle(graph_list, options.outgraph)

    elif len(graph_list) != 0:
        #Rest of the data.
        save_pickle(graph_list, options.outgraph+str(save_num))


