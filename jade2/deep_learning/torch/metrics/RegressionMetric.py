from .NNSimpleMetric import *
from scipy.stats import pearsonr, spearmanr, kendalltau

class RegressionMetric( NNSimpleMetric):
    """
    Calcualte Regression metrics such as r2, tau, spearmanr.
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'regression'

    def calculate(self, pred: np.ndarray, labels: np.ndarray) -> Dict:
        #print("pred", pred)
        #print("labels", labels)

        pearson, _ = pearsonr(pred, labels)
        spearman, _ = spearmanr(pred, labels)
        tau, p = kendalltau(pred, labels)
        r2 = pearson **2

        self.data['pearsonr'] = pearson
        self.data['spearmanr'] = spearman
        self.data['tau'] = tau
        self.data['r2'] = r2
        return self.data

    def show(self):
        print("r2: ", self.data['r2'], "r1", self.data['pearsonr'])
        print('spearman', self.data['spearmanr'], 'tau', self.data['tau'])