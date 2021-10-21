from .NNMetricFactory import *
from typing import List, Dict, DefaultDict
import numpy as np
import torch
from collections import defaultdict
from torch.utils.tensorboard import SummaryWriter
from typing import Union

import sys


class RunNNMetrics( object ):
    """
    A class for running and writing NNSimpleMetrics during or after training.
    NOTE - update function flattens the data. Useful, but not generalizable to more complex models.
    """
    def __init__(self, metrics: List[str] = None):
        self.metrics = defaultdict()
        self.data    = defaultdict()
        self.creator = NNMetricFactory()

        if metrics:
            for metric in metrics:
                self.metrics[metric] = self.creator.create_metric(metric)

        self.pred = []
        self.labels = []
        self.loss = 0

    def update(self, pred: Union[np.ndarray, torch.Tensor], labels: Union[np.ndarray, torch.Tensor], loss_mean: float):
        """
        Add predictions and labels to stored results.
        loss_mean should be the mean.  We'll take an even mean over the batches.
        https://discuss.pytorch.org/t/on-running-loss-and-average-loss/107890
        """
        if type(pred) != np.ndarray:
            #print("Flattening tensor")
            p = pred.detach().flatten()
            l = labels.detach().flatten()

            self.pred.append(p)
            self.labels.append(l)
            self.loss += loss_mean * p.shape[0]
        else:
            self.pred.append(pred)
            self.labels.append(labels)
            self.loss += loss_mean * pred.shape[0]

        #print("Updating val metrics")

        #print("Loss", self.loss)

    def clear(self):
        """
        Clear cached results
        """
        self.pred.clear()
        self.labels.clear()
        self.loss = 0

    def add_metric(self, metric: str):
        """
        Add metric name to list.
        """
        if metric not in self.metrics:
            self.metrics[metric] = self.creator.create_metric(metric)

    def add_metric_class(self, metric: NNSimpleMetric):
        """
        Add a NNSimpleMetric to run.
        """
        if metric.name not in self.metrics:
            self.metrics[metric.name] = metric

    def get_stored(self):
        """
        Get pred, labels as concatonated data.
        :return:
        """
        return self.__prepare(self.pred), self.__prepare(self.labels)

    def __prepare(self, data):
        """
        Prepare stored data by concat if numpy, or cat if tensor, then cpu and then to numpy.
        :param data:
        :return:
        """
        if type(data[0]) == np.ndarray:
            return np.concatenate(data)
        else:
            return torch.cat(data).cpu().numpy()

    def run_stored(self, show=False) -> DefaultDict:
        """
        Run metrics on stored data, return data.
        :return:
        """
        return self.run(self.__prepare(self.pred), self.__prepare(self.labels), show)

    def run(self, pred: Union[np.ndarray, torch.Tensor], labels: Union[np.ndarray, torch.Tensor], show = False) -> DefaultDict:
        """
        Run metrics setup in class. Return data. Data is also stored for future writing.
        """

        if type(pred) != np.ndarray:
            #print("Flattening tensor")
            p = pred.cpu().detach().flatten()
            l = labels.cpu().detach().flatten()
        else:
            p = pred
            l = labels

        self.data.clear()
        for name, metric in self.metrics.items():
            data = metric.apply(p, l)
            if show:
                metric.show()
            self.data.update(data)

        if self.loss:
            self.data['loss'] = self.loss/len(p)
        return self.data

    def show(self):
        for m in self.metrics.values():
            if m.has_data():
                m.show()

    def write(self, writer: SummaryWriter, epoch = None, use_metric_name = True, prefix = "", show=False):
        """
        Write to the summary writer. Optionally use the metric name as a group to group metrics.
        If predictions and labels are present and havn't run, we run them.
        Optionally give epoch if we are tracking these metrics through training.
        Returns raw data names and data that is actually single-valued
        """

        all_data = defaultdict()
        for metric in self.metrics.values():
            data = metric.get_data()
            for name in data:
                #print(type(data[name]))
                #print(data[name])
                if type(data[name]) == list: continue

                try:
                    if use_metric_name:
                        final_name = metric.name()+'/'+name
                    else:
                        final_name = name

                    if prefix:
                        final_name = prefix+"/"+final_name

                    writer.add_scalar(final_name, data[name], epoch)
                    all_data[name] = data[name]
                #Hard to get length of pieces of data if more than one and not lists, but still ndarray/etc. bah.
                except Exception:
                    continue
        if self.loss:
            writer.add_scalar(prefix+"/loss", self.data['loss'], epoch)
            all_data['loss'] = self.data['loss']
        return all_data










