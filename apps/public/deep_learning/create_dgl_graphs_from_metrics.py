#!/usr/bin/env python3

import torch
import dgl
import time
from jade2.rosetta_jade import get_dataframe_from_json, get_dataframe_from_json_or_csv
from jade2.deep_learning.torch import create_2D_tensor_from_score_data, get_onehot_encoded_sequence_tensor
from jade2.basic import *
from jade2.deep_learning.graphs import *
from jade2.deep_learning import one_body_metrics_all
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

if __name__ == "__main__":
    parser = ArgumentParser("Creates and saves a list of DGL graphs using metrics for use in DGL GCNs", formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--csv", "-c",
                        help="Input CSV file. Will read if pickled data is not present. ",
                        default = "data/scores_w_stability_2D_3D.csv")

    parser.add_argument("--pt", "-p",
                        help = "Sequence embeddings for prottrans if using them as node embeddings.",
                        default = "data/protrans_embeddings.pt")

    parser.add_argument("--outgraph", '-o',
                        help = "The name of the output graph pickle. ",
                        default = "data/dgl_graph.pkl")

    parser.add_argument("--force_rewrite", "-f",
                        help = "Force load and rewrite of pickle data. ",
                        default = False,
                        action = "store_true")

    parser.add_argument("--test",
                        help = "Only do the first 100 batches",
                        default = False,
                        action = "store_true")

    parser.add_argument("--out_dir", "-d",
                        help = "Output directory for temp files.",
                        default = "data")
    features = parser.add_argument_group("Graph Features", "Features that will go into the final graph")

    features.add_argument("--contact_feature", '-m',
                          help = "metric to use for contact map (graph) generation. Typical: CB_pair_distance_3D and total_pair_energy_3D",
                          default = 'CA_pair_distance_3D')

    features.add_argument("--onehot",
                          help = "Use one-hot for node features.  ",
                          default = False,
                          action = "store_true")

    features.add_argument("--prottrans",
                          help = "Use prottrans for node features.  Must already have generated data. ",
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

    if options.prottrans and not os.path.exists(options.pt):
        sys.exit("Prottrans node features specified but pre-configured protrans tensor not present at "+options.pt)

    #Parse any specific node and edge features.
    edge_features = []
    node_features = one_body_metrics_all

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

    pk1 = outdir+"/1D_data_pickle.pkl"
    pk2 = outdir+"/2D_data_pickle.pkl"
    pk3 = outdir+"/3D_data_pickle.pkl"

    if not os.path.exists(pk1) or options.force_rewrite:
        df = get_dataframe_from_json_or_csv(options.csv)

        columns_2d = sorted([x for x in df.columns if x.split("_")[-1] == "2D" or x == options.seq_column])
        columns_3d = sorted([x for x in df.columns if x.split('_')[-1] == "3D" ])
        columns_1d = sorted([x for x in df.columns if x not in columns_2d+columns_3d or x == options.seq_column])

        print("Writing pickles.")
        df[columns_3d].to_pickle(pk3)
        df[columns_2d].to_pickle(pk2)
        df[columns_1d].to_pickle(pk1)
        df = df[columns_1d]
    else:
        print("Reading pickle")
        df = pandas.read_pickle(pk1)
        #df2 = pandas.read_pickle(pk2)
        #df3 = pandas.read_pickle(pk3)

        print("done")

    if not options.seq_column in df.columns:
        sys.exit("Sequence column " +options.seq_column+" not found in csv data!")

    distance_metric_cutoffs = None


    if not os.path.exists(outdir+"/edge_data.pl") or options.force_rewrite:
        df3 = pandas.read_pickle(pk3)
        if not edge_features:

            energy_metrics = sorted([c for c in df3.columns if c.endswith('pair_energy_3D')])
            distance_metrics = sorted([c for c in df3.columns if c.endswith('pair_distance_3D')])
            distance_metric_cutoffs = {c : 7.0 for c in distance_metrics}

            features = energy_metrics+distance_metrics

        edge_data = get_edge_data_as_dict(df3, features, distance_metric_cutoffs)
        print("Created Edge Data")
        save_pickle(edge_data, outdir+"/edge_data.pl")
        print("Saved Edge Data")
    else:
        #If we try to load and it's missing certain edge features, we will absolutely fail here.
        print("Loading edge data")
        edge_data = load_pickle(outdir+"/edge_data.pl")
        print("Done")

    if use_one_body_metrics:
        print("Creating 2D tensor")
        df2 = load_pickle(pk2)
        data_t= create_2D_tensor_from_score_data(df2, one_body_metrics_all, padxy=False, scale=False, standardize=False)
        print(data_t.shape)
        print("Created 2D tensor")
    if onehot:
        seq_t = get_onehot_encoded_sequence_tensor(df, padxy=False)
        print("Created onehot")
    else:
        seq_t = torch.load(options.pt)

        #Prottrans pads the X and Y of the protein. We need to remove that.
        seq_t = seq_t[:,1:seq_t.shape[1] - 1]
        seq_t = seq_t.permute(0, 2, 1).contiguous()
        print("Loaded protrans")
    print(seq_t.shape)


    if use_one_body_metrics and (prottrans or onehot):
        all_node_t = torch.cat([data_t, seq_t], 1)
    elif use_one_body_metrics:
        all_node_t = data_t
    elif prottrans or onehot:
        all_node_t = seq_t
    else:
        sys.exit("You will need some node features for the graph convolution to run properly!")

    all_node_t = all_node_t.permute(0, 2, 1).contiguous()
    print("Loaded sequence data")

    create_graph = True
    energy_graph = False
    graph_list = []

    if not edge_features:
        #print(edge_data[0])
        metrics = list(edge_data[0].values())[0]
        metrics = list(metrics.keys())
        energy_metrics = sorted([m for m in metrics if m != 'total_pair_energy_3D' and m.endswith("pair_energy_3D")])

        #Just use CB for now.  In the future, we may want the full distances to more accurately give the structure.
        edge_features = energy_metrics + ['CA_pair_distance_3D']

    n_batches = len(edge_data)
    if options.test:
        n_batches = 500

    print("node_features: ", node_features)
    print("edge_features: ", edge_features)

    out_feat = open(options.outgraph+"_features.txt", 'w')
    out_feat.write("NODE_FEATURES : "+str(node_features)+'\n')
    out_feat.write("EDGE_FEATURES : "+str(edge_features)+'\n')
    out_feat.write("COVALENT_EDGE_ENCODING :"+str(options.covalent_edge_features))
    out_feat.write("PRIMARY_SEQ_ENCODING :"+str(options.primary_sequence_separation_features))
    out_feat.close()

    if create_graph:
        start_time = time.time()
        for i in range(0, n_batches):
            if not i%10: print(i)

            g = create_and_featurize_graph_fast(edge_data[i],  edge_features, all_node_t[i], len(df[seq_column][i]),
                                                contact_map_metric=options.contact_feature,
                                                covalent_edge_features=options.covalent_edge_features,
                                                primary_sequence_separation=options.primary_sequence_separation_features)


            graph_list.append(g)

    print(graph_list[0])

    min_time = (time.time() - start_time)/60.0
    print("--- %.4s minutes ---" % (min_time))
    save_pickle(graph_list, options.outgraph)


