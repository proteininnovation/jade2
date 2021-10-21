import torch
import torch.utils.data as data_utils
import numpy as np

def create_weighted_sampler(local_df, test_label = 'protease_stability'):
    """
    Create a weighted sampler using test weights.
    :param local_df:
    :param test_label:
    :return:
    """
    all_label_ids = torch.tensor([x for x in local_df[test_label]], dtype=torch.long)
    labels_unique, counts = np.unique(local_df[test_label], return_counts=True)
    print(labels_unique)

    class_weights = [sum(counts)/c for c in counts]
    print(class_weights)

    weights = [class_weights[e] for e in local_df[test_label]]

    print(len(local_df[test_label]))
    sampler = data_utils.WeightedRandomSampler(weights, len(local_df[test_label]))
    return sampler