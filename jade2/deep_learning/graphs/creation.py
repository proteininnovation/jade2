import dgl, torch
import numpy as np
import pandas
import sys, time
from typing import Dict, List
from collections import defaultdict
from jade2.deep_learning import transform_dict

def create_and_featurize_graph_fast(edge_dict, edge_metrics, node_tensor, n_residues, upper_cutoff=7.0, contact_map_metric='CB_pair_distance_3D', covalent_edge_features=False, primary_sequence_separation=False):

    #start_time = time.time()
    u = []
    v = []
    edge_features = []

    #print(node_tensor)
    #print(edge_dict)
    for xy in edge_dict:
        #print(xy)
        edge_feature_length = len(edge_metrics)
        if covalent_edge_features:
            edge_feature_length+=2
        if primary_sequence_separation:
            edge_feature_length+=1

        end_data = np.zeros(edge_feature_length)
        d = edge_dict[xy][contact_map_metric]
        #print(xy, d)

        #0 means no contact - not a measurable number.  If we want to do more interesting stuff in future, we can.
        if not d: continue

        if upper_cutoff:
            if d <= upper_cutoff:
                u.append(xy[0])
                v.append(xy[1])
            else:
                continue
        else:
            u.append(xy[0])
            v.append(xy[1])


        for index,metric in enumerate(edge_metrics):
            #print(metric)
            try:
                end_data[index] = edge_dict[xy][metric]
            except Exception:
                end_data[index] = 0.0

        if covalent_edge_features:
            if primary_sequence_separation:
                i_offset = -1
            else:
                i_offset = 0

            if abs(xy[1] - xy[0]) == 1:
                end_data[-2 - i_offset] = 1
                end_data[-1 - i_offset] = 0
                #print("Adding covalent features between ", str(xy))
            else:
                end_data[-2 - i_offset] = 0
                end_data[-1 - i_offset] = 1

        #Here, we do not take the absolute value
        # This is because we have edges from 1 -> 0 and 0 ->1
        # These edges are the same,
        #  except we can encode the order of the primary sequence with them instead of using a full symmetric representation.
        #  Theoretically, this should give the model the idea of a primary sequence order - which is indeed important.
        if primary_sequence_separation:
            end_data[-1] = xy[1] - xy[0]

        edge_features.append(end_data)

    g = dgl.DGLGraph((np.array(u), np.array(v)), num_nodes = n_residues)
    #print(g)
    g.ndata['data'] = torch.tensor(node_tensor.cpu()[:n_residues].numpy(), dtype=torch.float32)
    g.edata['data'] = torch.tensor( edge_features, dtype = torch.float32)
    #print(g)

    return g

def create_and_featurize_graph(
        edge_data: Dict,
        seq_len: int,
        node_tensor: torch.Tensor,
        edge_metrics: List,
        contact_map_metric='CB_pair_distance_3D'):
    """
    Create a graph and featurize edges and nodes
    Give edge_metrics as None to not featurize edges

    :param edge_data:           dict of [metric][(node1,node2) : data
    :param seq_len:                 Sequence Length
    :param node_tensor:         Tensor with/o batches to use to featurize nodes (IE just per-res data.). Index on batch to get the specific data.
    :param edge_metrics:        List of edge metrics to use
    :param contact_map_metric:  metric to use to create the actual graph.
    :param seq_column:
    :param energy_graph:        Use energy graph instead of distance graph?
    :return:
    """


    #Create graph on distances or energy
    g = create_graph_from_single_pair_data(edge_data, seq_len, metric=contact_map_metric)
    #print(g)

    #Featurize edges
    if edge_metrics:
        featurize_edges(g, edge_data, edge_metrics)

    #Featurize nodes
    #We need to turn into numpy or else we get a 'view' and copy everything to the node!
    if node_tensor != None:
        #print(node_tensor.shape)
        g.ndata['data'] = torch.tensor(node_tensor[:seq_len].numpy(), dtype=torch.float32)
    return g


def create_graph_from_single_pair_data(edge_dict: Dict, n_residues: int, metric='CA_pair_distance_3D', upper_cutoff = 7.0) -> dgl.DGLGraph:
    """
    Create a basic graph using a (distance) metric and a cutoff.
    If cutoff is None, will take all of it.

    data_dict is a dict as:
        [metric][(x,y)] = data

    x,y are integers and will become nodes according to the cutoff.
    """

    u = []
    v = []
    #data_dict = transform_dict(edge_dict)
    for xy in edge_dict:
        try:
            d = edge_dict[xy][metric]
            #print(xy, d)
            if upper_cutoff:
                if d and d <= upper_cutoff:
                    u.append(xy[0])
                    v.append(xy[1])
            else:
                u.append(xy[0])
                v.append(xy[1])
        except KeyError:
            print("Skipping ",xy, " that is missing ",metric)
            print(edge_dict[xy])
            continue


    #print(np.array(u))
    #print(np.array(v))
    g = dgl.DGLGraph((np.array(u), np.array(v)), num_nodes = n_residues)
    return g

def featurize_edges(gl: dgl.DGLGraph, edge_data, edge_metrics):
    """
    Featurize the edges with energy and distance data.
    If you want to try w/o either one, pass an empty list for metrics.
    edge_data is [(res1,res2)][metric] :data

    Note that this code does not do any scaling!  You will need to scale/standardize these properly!
    """

    n_features = len(edge_metrics)
    gl.edata['data'] = torch.zeros(gl.num_edges(), n_features, dtype = torch.float32)

    #Change into a dict first so we can add as a single tensor in order.
    #[xy][metric] = data

    #Now that we have the data in a decent format, we can add it.
    for xy in edge_data:
        r1 = xy[0]; r2 = xy[1]
        end_data = np.zeros(n_features)
        #print(r1, r2)
        if r1 <= gl.num_nodes() and r2 <= gl.num_nodes() and gl.has_edge_between(r1, r2):
            for index,metric in enumerate(edge_metrics):
                if metric in edge_data[xy]:
                    end_data[index] = edge_data[xy][metric]
        else:
            continue

        #Add the edge as a tensor
        gl.edata['data'][gl.edge_id(r1, r2)] = torch.tensor(end_data, dtype=torch.float32)
