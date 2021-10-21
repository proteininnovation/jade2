from .NNSimpleMetric import *
from sklearn.metrics import roc_auc_score, precision_recall_curve
from sklearn.metrics import average_precision_score

class BinaryClassficationMetric(NNSimpleMetric):
    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return "binary_classification"

    def calculate(self, pred: np.ndarray, labels: np.ndarray) -> Dict:
        """
         Given the data, calculate the classification accuracy.
         Returns true_positives, true_negatives, false_positives, false_negatives, roc_auc, pr for use elsewhere.
         :param pred:
         :param labels:
         :return:
         """
        false_positives = 0
        false_negatives = 0
        true_positives = 0
        true_negatives = 0

        total = pred.shape[0]

        #print("predictions", pred)
        #print("labels", labels)
        correct = (pred == labels).sum()

        #Calculate false positives, etc.
        for kt in zip(pred, labels):
            if kt[0] == kt[1] ==1:
                true_positives+=1
            elif kt[0] == kt[1] == 0:
                true_negatives+=1
            elif kt[0] == 1 and kt[1] == 0:
                false_negatives+=1
            elif kt[0] == 0 and kt[1] == 1:
                false_positives+=1

        accuracy = correct/total
        auc = roc_auc_score(labels, pred )
        precision, recall, thresholds = precision_recall_curve(labels, pred)
        avg_pre_recall = average_precision_score(labels, pred)

        self.data['accuracy'] = accuracy
        self.data['roc_auc'] = auc
        self.data['precision'] = precision
        self.data['recall'] = recall
        self.data['pr_thresholds'] = thresholds
        self.data['avg_precision_recall'] = avg_pre_recall
        self.data['true_positives'] = true_positives
        self.data['true_negatives'] = true_negatives
        self.data['false_positives'] = false_positives
        self.data['false_negatives'] = false_negatives
        self.data['n_total'] = total
        self.data['n_correct'] = correct

        return self.data

    def show(self):
        p = self.as_params()

        print("Accuracy: %f" % p.accuracy, "at", p.n_correct, "/", p.n_total)
        print("ROC AUC:", p.roc_auc, "avg precision/recall", p.avg_precision_recall)

        print("True Positives", p.true_positives, " False Positives", p.false_positives)
        print("True Negatives", p.true_negatives, " False Negatives", p.false_negatives)


