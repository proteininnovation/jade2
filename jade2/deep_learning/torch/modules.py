import torch
import torch.nn as nn
import pytorch_lightning as pl
from typing import List, Tuple


import torch.nn as nn
import torch
import jade2.deep_learning.torch.util as tu

class StandardConvolution1D(nn.Module):
    """
    Standard, exponential decaying 1D convolutional network for sequences and transfer learning.
    Includes BatchNorm1D and ELU as activation function.

    Kernel size of 3 requires padding 1
    Kernel size of 5 requires padding 2

    Decay rate determines how quickly we exponentially decrease the width of the network.
      - For Ex. Decay rate of 2 means we go from 1024 to 512 to 256, etc.

    Final_layer indicates the width of the final fully-connected linear layer
    Dim2 is the length

    Final layer is flattened.  We may want to titrate this down in the future.
    """
    def __init__(self, n_features, dim2, kernel_size = 3, padding =1, final_layer=15, decay_rate=2, ntasks=1):
        # Setup the model here.
        super().__init__()

        features = n_features
        n_labels = ntasks
        dim2 = dim2
        kernel_size = 3
        padding = 1

        # Setup Exponential decay of layers
        layer_opt = tu.get_exp_decay_layer_list(features, final_layer, decay_rate)
        print(layer_opt)
        layers_list = [self._get_conv_layer(x[0], x[1], kernel_size, padding) for x in
                       self._get_layer_mapping(features, layer_opt)]

        # Now we deal with going to a linear layer.
        layers_list.append(nn.Flatten())

        layers_list.append(self._get_linear_layer(layer_opt[-1], ntasks, dim2, ))

        self.layers = nn.Sequential(*layers_list)

    def forward(self, x):
        return self.layers(x)

        # noinspection PyTypeChecker
    def _get_conv_layer(self, features_in, features_out, kernel_size=5, padding=2):
        print(features_in, features_out, kernel_size)

        return nn.Sequential(
            nn.Conv1d(features_in, features_out, kernel_size=kernel_size, padding=padding),
            nn.BatchNorm1d(features_out),
            nn.ELU(),

        )

    def _get_linear_layer(self, in_features, out_features, original_dim2):
        """
        Get the final linear layer accounting for in_features and pooling
        """

        total_features = in_features * original_dim2

        return nn.Linear(total_features, out_features)

    def _get_layer_mapping(self, start_features, features_max_pool):
        """
        Create a list of Tuples of in,out for layer creation.
        """

        i = 0
        f_in = start_features
        feature_map = []
        for x in features_max_pool:
            if i > 0:
                f_in = features_max_pool[i - 1]
            feature_map.append((f_in, x))
            i += 1
        return feature_map

class MaxPoolProttrans(pl.LightningModule):
    """
    Model from Steven Combs that uses MaxPool1d instead of Convolutions that seems
     to work well for sequence-based models with point-mutational data
    """
    def __init__(self, n_residues, n_features=1024, classifier=False, ntasks=1):
        super().__init__()
        self.classifier = classifier
        self.ntasks = ntasks
        self.layers = nn.Sequential(
            nn.MaxPool1d(kernel_size=n_residues),
            nn.BatchNorm1d(n_features),
            nn.ELU(),
            nn.Flatten(),
            nn.Linear(n_features, 512),
            nn.ELU(),
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(512, 512),
            nn.ELU(),
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(512, 512),
            nn.ELU(),
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(512, 512),
            nn.ELU(),
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(512, 512),
            nn.ELU(),
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(512, ntasks),
        )
        if classifier:
            self.sm = nn.LogSoftmax(dim=1)

    def forward(self, x):
        if self.classifier:
            p = self.layers(x)
            return self.sm(p)
        else:
            return self.layers(x)

class BatchNorm2DModel(pl.LightningModule):
    def __init__(self, in_t: torch.Tensor, layer_opt: List[Tuple[int, bool]], n_labels = 1, kernel_size = 5, padding=2, classifier=False):
        """
        layer_opt defines how we construct the layers. is a List of Lists to keep it simple for now.
        [[n_out_features], [max_pool_booleans]]

        Both lists should be the same size.
        Ex: [[L*2,  L, L//2, L//4], [False, True, True, False]]

        If classifier_labels is 0, we do do not add LogSoftMax.

        If Kernel Size is 5, padding should be 2
        If Kernel size is 3, padding should be 1

        https://towardsdatascience.com/batch-normalization-and-dropout-in-neural-networks-explained-with-pytorch-47d7a8459bcd
        """

        super().__init__()
        assert(len(layer_opt[0]) == len(layer_opt[1]))
        last_lin = 1
        features = in_t.shape[1]
        dim2 = in_t.shape[2]


        layers_list = [self.get_conv_layer(x[0], x[1], x[2], kernel_size, padding) for x in self.get_layer_mapping(features, layer_opt)]

        #Now we deal with going to a linear layer.
        layers_list.append(nn.Flatten())

        layers_list.append(self.get_linear_layer(layer_opt[0][-1], n_labels, dim2, sum(layer_opt[1])))

        #Account for optional classifier.
        if classifier:
            layers_list.append(nn.LogSoftmax(dim=1))

        self.layers = nn.Sequential(*layers_list)

    def forward(self, x):
        return self.layers(x)

    # noinspection PyTypeChecker
    def get_conv_layer(self, features_in, features_out, max_pool = False, kernel_size = 5, padding=2):
        print(features_in, features_out, kernel_size, max_pool)

        if not max_pool:
            return nn.Sequential(
                nn.Conv1d( features_in, features_out, kernel_size=kernel_size, padding=padding),
                nn.ELU(),
                nn.BatchNorm1d(features_out),
            )
        else:
            return nn.Sequential(
                nn.Conv1d( features_in, features_out, kernel_size=kernel_size, padding=padding),
                nn.MaxPool1d(2),
                nn.ELU(),
                nn.BatchNorm1d(features_out),
            )

    def get_linear_layer(self, in_features, out_features, original_dim2, n_pools):
        """
        Get the final linear layer accounting for in_features and pooling
        """
        if n_pools != 0:
            total_features = in_features * (original_dim2//(n_pools * 2))
        else:
            total_features = in_features * original_dim2

        return nn.Linear(total_features, out_features)

    def get_layer_mapping(self, start_features, features_max_pool):
        """
        Create a list of Tuples of in,out,max_pool for layer creation.
        """

        i = 0
        f_in = start_features
        feature_map = []
        for x, y in zip(features_max_pool[0], features_max_pool[1]):
            if i >0:
                f_in = features_max_pool[0][i-1]
            feature_map.append((f_in, x, y))
            i+=1
        return feature_map



    ####Notes###:

    #https://towardsdatascience.com/pytorch-basics-how-to-train-your-neural-net-intro-to-cnn-26a14c2ea29
    #https://towardsdatascience.com/pytorch-how-and-when-to-use-module-sequential-modulelist-and-moduledict-7a54597b5f17
    #https://discuss.pytorch.org/t/linear-layer-input-neurons-number-calculation-after-conv2d/28659/2
    #https://towardsdatascience.com/pytorch-layer-dimensions-what-sizes-should-they-be-and-why-4265a41e01fd

class GeneralLinearModel(pl.LightningModule):
    def __init__(self, in_t: torch.Tensor, layer_opt: List[int], n_labels = 1, dropout1=.1, dropout_rest=.5, classifier=False):
        """
        layer_opt defines how we construct the depth and width of layers. is a List

        Ex: [L*2,  L, L//2, L//4]

        If classifier_labels is 0, we do do not add LogSoftMax.

        """

        super().__init__()
        features = in_t.shape[1]

        layers_list = [self.get_linear_layer(x[0], x[1], x[2]) for x in self.get_layer_mapping(features, layer_opt, dropout1, dropout_rest)]
        layers_list.append(self.get_last_linear_layer(layer_opt[-1], n_labels))
        #Account for optional classifier.
        if classifier:
            layers_list.append(nn.LogSoftmax(dim=1))

        self.layers = nn.Sequential(*layers_list)
        print("Initialized model")

    def forward(self, x):
        return self.layers(x)

    def get_linear_layer(self, features_in, features_out, dropout_rate):
        print(features_in, features_out, dropout_rate)

        return nn.Sequential(
            nn.Linear( features_in, features_out),
            nn.ELU(),
            nn.Dropout(dropout_rate)
        )

    def get_last_linear_layer(self, in_features, out_features):
        """
        Get the final linear layer accounting for in_features and pooling
        """

        return nn.Linear(in_features, out_features)

    def get_layer_mapping(self, start_features, features, dropout1=.1, dropout_rest=.5):
        """
        Create a list of Tuples of in,out,dropout for layer creation.
        """

        i = 0
        f_in = start_features
        dropout=dropout1
        feature_map = []
        print(features)
        for x in features:
            if i >0:
                f_in = features[i-1]
                dropout = dropout_rest
            feature_map.append((f_in, x, dropout))
            i+=1

        return feature_map