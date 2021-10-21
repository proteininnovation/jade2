import unittest
import warnings
import shutil

from jade2.deep_learning.torch.metrics import *
import numpy as np

class TestNNMetrics(unittest.TestCase):
    def test_factory(self):
        factory = NNMetricFactory()
        l = factory.list_metrics()
        metric = factory.create_metric(l[0])
        self.assertEqual(metric.name(), l[0])

    def test_regression(self):
        reg = RegressionMetric()
        x = np.arange(0, 1, .1)
        y = np.arange(0, 1, .1)
        data = reg.apply(x, y)
        self.assertTrue(data['r2'] > .99)
        self.assertTrue(data['pearsonr'] > .99)

    def test_binary_classification(self):
        cla = BinaryClassficationMetric()
        x = np.array([0, 0, 1, 1, 1, 1])
        y = np.array([0, 1, 0, 1, 1, 0])
        data = cla.apply(x, y)
        print(data)
        self.assertTrue(data['true_positives'] == 2)
        self.assertTrue(data['n_correct'] == 3)
        self.assertTrue(data['false_positives'] == 1)
        self.assertTrue(data['true_negatives'] == 1)
        self.assertTrue(data['false_negatives'] == 2)
        self.assertTrue(data['n_total'] == 6)
        self.assertTrue(data['accuracy'] == .5)

    def test_runner(self):
        runner = NNMetrics(['regression'])
        x = np.arange(0, 1, .1)
        y = np.arange(0, 1, .1)
        runner.update(x, y)
        runner.update(x, y)

        self.assertTrue(len(runner.pred) == 2)
        data = runner.run_stored(True)
        self.assertTrue(runner.data)
        self.assertTrue('r2' in runner.data)

        self.assertTrue('r2' in data)
        self.assertTrue(data['r2'] > .99)

if __name__ == '__main__':
    unittest.main()