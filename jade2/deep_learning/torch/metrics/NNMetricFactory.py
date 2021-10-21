from .BinaryClassificationMetric import BinaryClassficationMetric
from .MultiClassificationMetric import MultiClassficationMetric
from .RegressionMetric import RegressionMetric
from .NNSimpleMetric import NNSimpleMetric

class NNMetricFactory( object ):
    def __init__(self):
        self.metrics = {
            BinaryClassficationMetric.name() : BinaryClassficationMetric,
            RegressionMetric.name() : RegressionMetric,
            MultiClassficationMetric.name() : MultiClassficationMetric

        }

    def create_metric(self, name) -> NNSimpleMetric:
        """
        Create an NNSimpleMetric by name.
        """
        return self.metrics[name]()

    def list_metrics(self):
        print(str(self.metrics.keys()))
        return(list(self.metrics.keys()))