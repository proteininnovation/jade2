from .NNSimpleMetric import *
from sklearn.metrics import roc_auc_score, precision_recall_curve
from sklearn.metrics import average_precision_score
import torch
import numpy as np

class MultiClassficationMetric(NNSimpleMetric):
    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return "multi_classification"

    def multi_acc(self, y_pred, y_test):
        y_pred_softmax = torch.log_softmax(y_pred, dim = 1)
        _, y_pred_tags = torch.max(y_pred_softmax, dim = 1)

        correct_pred = (y_pred_tags == y_test).float()
        acc = correct_pred.sum() / len(correct_pred)

        acc = torch.round(acc * 100)

        return acc

    def calculate(self, pred: np.ndarray, labels: np.ndarray) -> Dict:
        """
         Given the data, calculate the classification accuracy.
         Returns true_positives, true_negatives, false_positives, false_negatives, roc_auc, pr for use elsewhere.
         :param pred:
         :param labels:
         :return:
         """

        print(pred)
        print(labels)

        n_classes = len(np.unique(labels))
        print("NClasses:", n_classes)

        total = pred.shape[0]

        #print("predictions", pred)
        #print("labels", labels)
        correct = (pred == labels).sum()

        #Calculate false positives, etc.
        per_class_results = defaultdict()
        for i in range(0, n_classes):
            per_class_results[i] = defaultdict(int)

        for kt in zip(pred, labels):
            #print(kt)

            for i in range(0, n_classes ):
                if kt[0] == kt[1] == i:
                    per_class_results[i]['correct']+=1
                elif kt[0] == i:
                    per_class_results[i]['false_positives']+=1
                elif kt[1] == i:
                    per_class_results[i]['false_negatives']+=1

                if kt[1] == i:
                    per_class_results[i]['total'] +=1

        #print(per_class_results)

        for i in range(0, n_classes):
            R = per_class_results[i]

            self.data['accuracy_'+str(i)] = R['correct']/R['total']
            self.data['correct_'+str(i)] = R['correct']
            self.data['false_positives_'+str(i)] = R['false_positives']
            self.data['false_negatives_'+str(i)] = R['false_negatives']
            self.data['total_'+str(i)] = R['total']

        accuracy = correct/total

        #Roc AUC for multiclass not currently possible as we need to have not called argmax.
        #auc = roc_auc_score(labels, pred, multi_class="ovo")

        self.data['accuracy'] = accuracy
        #self.data['roc_auc'] = auc
        self.data['n_total'] = total
        self.data['n_correct'] = correct

        return self.data

    def show(self):
        p = self.as_params()

        print("Accuracy: %f" % p.accuracy, "at", p.n_correct, "/", p.n_total)

        for x in self.data:
            print(x, self.data[x])



