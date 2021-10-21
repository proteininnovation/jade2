from abc import ABC, abstractmethod
from typing import Dict
import numpy as np
from collections import defaultdict
from jade2.deep_learning.torch import Params
from torch.utils.tensorboard import SummaryWriter


class NNSimpleMetric(ABC):
    """
    Metric that outputs data on input prediction and labeled numpy arrays.
    """
    def __init__(self):
        super().__init__()
        self.data = defaultdict()

    def as_params(self) -> Params:
        """
        Return data as a Params class, which allows . values to be used.
        :return:
        """
        return Params(self.data)

    def has_data(self):
        return len(self.data)

    def apply(self, pred: np.ndarray, labels: np.ndarray) -> Dict:
        """
        Returns the values in the calculation and sets the data.
        """
        self.data = self.calculate(pred, labels)
        return self.data

    def get_data(self):
        return self.data

    @staticmethod
    @abstractmethod
    def name() ->str:
        """
        The Name of the object.  Used for factory.
        """
        raise NotImplementedError()

    @abstractmethod
    def calculate(self, pred: np.ndarray, labels: np.ndarray) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def show(self):
        raise NotImplementedError()




#Notes:
## https://machinelearningmastery.com/roc-curves-and-precision-recall-curves-for-classification-in-python/


