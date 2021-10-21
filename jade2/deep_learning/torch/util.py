from matplotlib import pyplot as plt
from typing import *
import pandas
import pickle
import numpy as np
import torch
import torch.nn as nn
import torch.utils.data as data_utils
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.metrics import roc_auc_score, precision_recall_curve


def create_sampler(local_df, test_label) -> data_utils.WeightedRandomSampler:
    """
    Create a sampler for an arbitrary classifier with data in a DF column.
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

def plot_loss(train_losses:List, val_losses:List) -> plt.Figure:
    """
    Plot training losses vs val losses.
    Original Author: Steven Combs
    """
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    ax.plot(train_losses, label='train')
    ax.plot(val_losses, label='val')
    ax.legend()
    ax.set_xlabel('epoch')
    ax.set_ylabel('loss')
    ax.grid()
    return fig

def get_exp_decay_layer_list(start_width, final_output_layer=15, decay_rate=2, max_layers=None):
    """
    Get a list of layers that decay over two until we reach the final output layer.
    Layers list used to control width and depth in modules.
    """
    layers = []
    v = start_width
    while v > final_output_layer*decay_rate:
        if max_layers and len(layers) == max_layers:
            print(layers)
            return layers
        v = v//decay_rate
        layers.append(v)

    print(layers)
    return layers

def get_linear_decay_layer_list(start_width, max_n_layers=10, max_last_layer=5):
    """
    Get a linearly decaying layer list of the desired depth starting at the width.
    Will attempt to create layers up to max_last_layer while considering the width of the last layer.
    Layers list used to control width and depth in modules.
    """
    array = []
    for i in range(1, max_n_layers+1):
        width = start_width*(max_n_layers-i)/max_n_layers
        if width > max_last_layer:
            array.append(width)
    print(array)
    return array

def create_balanced_sampler(local_df: pandas.DataFrame,
                            test_label: str) -> data_utils.WeightedRandomSampler:
    """
    Create a balanced weighted sampler from a dataframe column, already split into classes.

    :param local_df: dataframe with column of classified data.
    :param test_label: Column name.
    :return:
    """
    all_label_ids = torch.tensor([x for x in local_df[test_label]], dtype=torch.long)
    labels_unique, counts = np.unique(local_df[test_label], return_counts=True)
    #print(labels_unique)

    class_weights = [sum(counts)/c for c in counts]
    #print(class_weights)

    weights = [class_weights[e] for e in local_df[test_label]]

    sampler = data_utils.WeightedRandomSampler(weights, len(local_df[test_label]))
    return sampler

def create_balanced_dataset(local_df: pandas.DataFrame,
                            dataset: data_utils.Dataset,
                            test_label: str,
                            batch_size: int = 32) -> data_utils.DataLoader:
    """
    Create a balanced sampler, and return a configured dataloader using the test_label.
    For continuous data that still has balancing needs, add a new column to the df.
    """
    #https://medium.com/analytics-vidhya/augment-your-data-easily-with-pytorch-313f5808fc8b

    sampler = create_balanced_sampler(local_df, test_label)
    loader = data_utils.DataLoader(dataset, sampler=sampler, batch_size=batch_size)
    return loader

def plot_continuous_vs_y(best_m: nn.Module, local_loss_fn: nn.Module, local_test: torch.tensor, local_target_test: torch.tensor):
    """
    Evaluate the model and Plot continuous x and y values.
    Used for prediction models.
    Prints and returns pearson,spearman,tau
    """
    with torch.no_grad:
        output = best_m(local_test)
        best_loss = float(local_loss_fn(output, local_target_test))
        print(best_loss)
        x = output.detach().flatten().numpy()
        y = local_target_test.detach().flatten().numpy()

        plt.scatter(x , y)
        pearson, _ = pearsonr(x, y)
        spearman, _ = spearmanr(x, y)
        tau, p = kendalltau(x, y)
        print(pearson, spearman, tau)
        return pearson,spearman,tau, best_loss

def show_binary_classification_accuracy(best_m: nn.Module, local_loader: data_utils.DataLoader, chatty = False) -> Tuple:
    """
    Given the model and dataloader, calculate the classification accuracy.
    Returns true_positives, true_negatives, false_positives, false_negatives, roc_auc, pr for use elsewhere.
    :param best_m:
    :param local_loader:
    :return:
    """
    correct = 0; total = 0

    false_positives = 0
    false_negatives = 0
    true_positives = 0
    true_negatives = 0

    pred_list = []
    lab_list = []
    with torch.no_grad():
        for data, labels in local_loader:
            outputs = best_m(data)
            predicted = torch.argmax(outputs, dim=1)

            #print(predicted)
            #print(labels.shape[0])
            total += labels.shape[0]
            #print(labels.shape[0])
            #print(labels)
            correct += int((predicted == labels).sum())

            pred_list.extend(predicted.detach().flatten().numpy())
            lab_list.extend(labels.detach().flatten().numpy())

            #Calculate false positives, etc.
            for kt in zip(predicted, labels):
                if kt[0] == kt[1] ==1:
                    true_positives+=1
                elif kt[0] == kt[1] == 0:
                    true_negatives+=1
                elif kt[0] == 1 and kt[1] == 0:
                    false_negatives+=1
                elif kt[0] == 0 and kt[1] == 1:
                    false_positives+=1


    accuracy = correct/total

    print("Accuracy: %f" % (accuracy))

    auc = roc_auc_score(pred_list, lab_list)
    pr = precision_recall_curve(pred_list, lab_list)

    if chatty:

        print("True Positives", true_positives, " False Positives", false_positives, f" at {false_positives/(total-correct):.2f}")
        print("True Negatives", true_negatives, " False Negatives", false_negatives, f" at {false_negatives/(total-correct):.2f}")

    return accuracy, true_positives, true_negatives, false_positives, false_negatives, auc, pr, pred_list, lab_list

def calculate_correlations(x, y) -> Tuple:
    """
    Calculates correlations between x and y.
    Returns pearson, spearman, Kendall's tau correlations using scipy.

    """
    pearson, _ = pearsonr(x, y)
    spearman, _ = spearmanr(x, y)
    tau, p = kendalltau(x, y)
    return pearson, spearman, tau

def get_standard_loss(classifier=False):
    """
    Return NLLLoss for use with LogSoftMax if classifier, else returns MSELoss
    """
    if classifier:
        return nn.NLLLoss()
    else:
        return nn.MSELoss()

def prepare_data_1D_test(local_df: pandas.DataFrame, test_columns: List, scale=False, standardize=False, test_size = .15, random_state = 27):

    X_train, X_test = train_test_split(local_df,test_size=test_size,random_state=random_state)
    train_columns = [x for x in X_train.columns if x not in test_columns]
    if scale or standardize:
        # fit scaler on training data
        if standardize:
            norm = StandardScaler().fit(X_train[train_columns])
        else:
            norm = MinMaxScaler().fit(X_train[train_columns])

        X_train[train_columns] = norm.transform(X_train[train_columns])
        X_test[train_columns]= norm.fit_transform(X_test[train_columns])

    return X_train, X_test


