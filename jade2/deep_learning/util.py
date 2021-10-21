#!/usr/bin/env python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas
from collections import defaultdict
from matplotlib.colors import ListedColormap
from argparse import ArgumentParser



def transform_dict(edge_dict):
    """
    Transforms a dictionary of dictionaries to flip key/values.
    :param edge_dict:
    :return:
    """
    new_dict = defaultdict()
    for x in edge_dict:
        for y in edge_dict[x]:
            if not y in new_dict:
                new_dict[y] = defaultdict()
            new_dict[y][x] = edge_dict[x][y]
    return new_dict

def strip_dim(local_df: pandas.DataFrame, dim: str) -> pandas.DataFrame:
    """
    Strip either 1D/2D/3D from column names, return new df w/o dimensionality annotations.
    :param local_df:
    :param dim:
    :return:
    """
    new_names = defaultdict()
    for column in local_df.columns:
        if column.split("_")[-1] == dim:
            new_names[column] = column.strip("_"+dim)
    local_df = local_df.rename(new_names, axis=1)
    return local_df

def plot_2d_decision_regions(X, y, classifier, resolution = 0.02):
    markers = ('s', 'x', 'o', '^', 'v')
    colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan')

    cmap = ListedColormap(colors[:len(np.unique(y))])

    # Plot the decision surface.  This is kinda BS.  There must be an equation to get the actual slope from the Perceptron
    x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1

    xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, resolution),
                           np.arange(x2_min, x2_max, resolution))

    predict_line = np.array([xx1.ravel(), xx2.ravel()]).T
    print(repr(predict_line))
    Z = classifier.predict(predict_line)
    print("Z "+repr(Z))

    Z = Z.reshape(xx1.shape)
    plt.contourf(xx1, xx2, Z, alpha=.4, cmap = cmap)
    plt.xlim(xx1.min(), xx1.max())
    plt.ylim(xx2.min(), xx2.max())

    for idx, c1 in enumerate(np.unique(y)):
        plt.scatter(x=X[y == c1, 0], y=X[y == c1, 1],
                    alpha=.8, c = cmap(idx),
                    marker = markers[idx], label = c1)

def plot_decision_regions(X, y, classifier, test_idx = None, resolution = 0.02):
    markers = ('s', 'x', 'o', '^', 'v')
    colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan')

    cmap = ListedColormap(colors[:len(np.unique(y))])

    # Plot the decision surface.  This is kinda BS.  There must be an equation to get the actual slope from the Perceptron
    x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1

    xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, resolution),
                           np.arange(x2_min, x2_max, resolution))

    predict_line = np.array([xx1.ravel(), xx2.ravel()]).T
    Z = classifier.predict(predict_line)

    Z = Z.reshape(xx1.shape)
    plt.contourf(xx1, xx2, Z, alpha=.4, cmap = cmap)
    plt.xlim(xx1.min(), xx1.max())
    plt.ylim(xx2.min(), xx2.max())

    for idx, c1 in enumerate(np.unique(y)):
        plt.scatter(x=X[y == c1, 0], y=X[y == c1, 1],
                    alpha=.8, c = cmap(idx),
                    marker = markers[idx], label = c1)

    if test_idx:
        X_test, y_test = X[test_idx, :],y[test_idx]
        plt.scatter(X_test[:, 0], X_test[: ,1], c='',
                    alpha=1.0, linewidth=1, marker='o',
                    s=55, label='test set')