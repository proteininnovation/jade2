import networkx as nx
import dgl
from collections import defaultdict
from torch.utils.data import DataLoader

def regress(device, model, bg):
    """
    Run a Graph model with DGL
    :param device:  Device to move to
    :param model: DGL GCN
    :param bg: Batched Graph
    :return:
    """
    bg = bg.to(device)

    #Not sure why we pop here, but this seems to be common practice.
    h = bg.ndata.pop('h').float()
    e = bg.edata.pop('h').float()
    h, e = h.to(device), e.to(device)
    return model(bg, h, e)

def create_loaders(train_dataset, val_dataset, test_dataset, sampler=None, batch_size=128):
    if sampler:
        train_loader = dgl.dataloading.GraphDataLoader(
            train_dataset,
            batch_size=batch_size,
            drop_last=False,
            shuffle=False,
            sampler=sampler)
    else:
        train_loader = dgl.dataloading.GraphDataLoader(
            train_dataset,
            batch_size=batch_size,
            drop_last=False,
            shuffle=True)

    test_loader = dgl.dataloading.GraphDataLoader(
        test_dataset,
        batch_size=batch_size,
        drop_last=False,
        shuffle=True)

    val_loader = dgl.dataloading.GraphDataLoader(
        val_dataset,
        batch_size=batch_size,
        drop_last=False,
        shuffle=True)

    return train_loader,val_loader,test_loader

def plot_graph_diagram(local_g, directed=True, spec = True):

    if directed:
        nx_g = local_g.to_networkx()
    else:
        nx_g = local_g.to_networkx().to_undirected()

    if spec:
        pos = nx.spectral_layout(nx_g)
        nx.draw(nx_g, pos, with_labels=True, node_color=[[.7, .7, .7]], alpha=0.8)
    else:
        nx.draw(nx_g, with_labels=True, node_color=[[.7, .7, .7]], alpha=0.8)

