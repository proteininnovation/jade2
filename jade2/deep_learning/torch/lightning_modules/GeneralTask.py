import pytorch_lightning as pl
import torch.nn as nn
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
import numpy as np
import jade2.deep_learning.torch.metrics as metrics
import jade2.deep_learning.torch.util as tu
from jade2.deep_learning.torch.hyperparameters.Parameters import Params
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

class GeneralTask(pl.LightningModule):
    """
    General task for non-graph learning.
    Will not currently work on multi-GPUs I think as we use my metrics instead of pt lightnings.
    """
    def __init__(self, model, params: Params, classifier = False, lr = 3e-4, outdir = "logs", run=1,
                 scheduler=False, monitor="val_loss", patience=5, factor=.9, n_classes = 2):
        super().__init__()
        self.model = model
        self.classifier = classifier
        self.lr = lr
        self.outdir = outdir
        self.run = run
        self.params = params
        self.scheduler = scheduler
        self.monitor = monitor
        self.patience = patience
        self.factor = factor
        self.n_classes = n_classes

        self.save_hyperparameters(dict(params.for_writer()))

        if self.classifier:
            self.loss_fn = nn.CrossEntropyLoss()
        else:
            self.loss_fn = nn.MSELoss()

        if classifier and n_classes == 2:
            metric_name = ['binary_classification']
        elif classifier and n_classes > 2:
            metric_name = ['multi_classification']
        else:
            metric_name = ['regression']

        #self.runner = metrics.NNAccumulator(metric_name)
        self.val_runner = metrics.RunNNMetrics(metric_name)
        self.test_runner = metrics.RunNNMetrics(metric_name)
        self.train_runner = metrics.RunNNMetrics(metric_name)

        self.losses_train = []
        self.losses_val = []

    def forward(self, *args, **kwargs):
        return self.model(*args, **kwargs)

    def on_train_start(self) -> None:
        #self.logger.log_hyperparams(dict(self.params.for_writer()))
        print("training started! on ", self.device)

    def on_test_start(self) -> None:
        #self.logger.log_hyperparams(dict(self.params.for_writer()))
        pass

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

        if self.scheduler:
            return {
                "optimizer": optimizer,
                "lr_scheduler": {
                    "scheduler": ReduceLROnPlateau(optimizer, 'min', patience=self.patience, factor=self.factor),
                    "monitor": self.monitor,
                },
            }
        else:
            return optimizer

    def general_step(self, batch, batch_idx, runner: metrics.RunNNMetrics, step_name: str):
        """
        General learning step. Returns loss, prediction, labels
        """
        bg, labels = batch
        prediction = self.forward(bg)
        loss = self.loss_fn(prediction, labels)

        if self.classifier:

            #This needs to happen for val and test.  It does not make a difference in argmax,
            # but multi-class needs this to sum to one, which log_softmax gives us.
            if step_name != "train":
                y_pred_softmax = torch.log_softmax(prediction, dim = 1)
                runner.update(torch.argmax(y_pred_softmax, dim=1), labels, loss.item())
            else:
                runner.update(torch.argmax(prediction, dim=1), labels, loss.item())
        else:
            runner.update(prediction, labels, loss.item())

        return loss, prediction, labels

    def training_step(self, batch, batch_idx):
        #print("Training step")
        loss, prediction, labels = self.general_step(batch, batch_idx, self.train_runner, "train")
        self.log('train_loss', loss.item(), on_step=False, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        #print("Validation step")
        loss, prediction, labels = self.general_step(batch, batch_idx, self.val_runner, "val")
        self.log('val_loss', loss.item(), on_step=False, on_epoch=True)
        return loss

    def test_step(self, batch, batch_idx):
        #print("Test step")
        loss, prediction, labels = self.general_step(batch, batch_idx, self.test_runner, "test")
        return loss

    def on_epoch_start(self) -> None:
        #print("Called epoch start. Clearing data.")
        pass


    def training_epoch_end(self, outputs) -> None:
        writer = self.logger.experiment
        print("Training epoch end.  Running metrics")
        self.train_runner.run_stored(True)
        self.train_runner.write(writer, self.current_epoch, use_metric_name=True, show=True, prefix="Train")
        self.losses_train.append(self.train_runner.data['loss'])
        #print("Train metrics written and cleared")
        self.train_runner.clear()

    def on_validation_epoch_end(self) -> None:
        print("Validation epoch end. Running metrics")
        writer = self.logger.experiment
        self.val_runner.run_stored(True)
        self.val_runner.write(writer, self.current_epoch, use_metric_name=True, show=True, prefix="Val")
        self.losses_val.append(self.val_runner.data['loss'])
        #print("validation metrics written and cleared")
        self.val_runner.clear()

    def on_test_end(self) -> None:
        """
        Writes data to logger, writes plots.
        Sets self.out_data for use elsewhere.
        :return:
        """
        #print("Test epoch end.  Running metrics")

        self.test_runner.run_stored(True)
        #print("Ran test stored")

        data = self.test_runner.write(self.logger.experiment, self.current_epoch, use_metric_name=True, show=True, prefix="Test")
        self.logger.log_hyperparams(dict(self.params.for_writer()), dict(data))
        #print(data)
        #out_df = pandas.DataFrame.from_dict(data, index = [0])
        #out_df.to_json(self.outdir+'/out_data.json', orient='records', lines=True)

        #Turn into

        #print("Params:",self.params.for_writer())
        #print("Data: ", data)

        y, x = self.test_runner.get_stored()

        fig= tu.plot_loss(self.losses_train, self.losses_val)
        fig.savefig(self.outdir+'/run_loss_'+str(self.run)+".pdf", dpi=300)

        self.logger.experiment.add_figure("losses", figure=fig)
        self.out_data = data

        if not self.classifier:
            fig = plt.figure(figsize=(6, 6))
            ax = fig.add_subplot(111)
            ax.scatter(x, y)
            ax.plot(x,y,"+", ms=10, mec="k")
            z = np.polyfit(x, y, 1)
            y_hat = np.poly1d(z)(x)

            ax.plot(x, y_hat, "r--", lw=1)
            text = f"$y={z[0]:0.3f}\;x{z[1]:+0.3f}$\n$R^2 = {r2_score(y,y_hat):0.3f}$"
            ax.text(0.05, 0.95, text,transform=ax.transAxes,
                    fontsize=14, verticalalignment='top')

            fig.savefig(self.outdir+'/regression_'+str(self.run)+".pdf", dpi=300)
            self.logger.experiment.add_figure("regression", figure=fig)

        self.test_runner.clear()
