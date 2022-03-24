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

class Template(pl.LightningModule):

    def __init__(self, model, params: Params, lr = 3e-4, outdir = "logs", run=1,
                 scheduler=False, monitor="val_loss", patience=5, factor=.9, n_classes = 2):
        super().__init__()

        self.save_hyperparameters(dict(params.for_writer()))

        self.model = model
        self.lr = lr
        self.outdir = outdir
        self.run = run
        self.params = params
        self.scheduler = scheduler
        self.monitor = monitor
        self.patience = patience
        self.factor = factor
        self.n_classes = n_classes

        #Setup Loss functions

        #Setup any metrics

    def _create_model(self):
        #Setup the model here.
        pass

    def forward(self, x):
        pass

    #Training
    def on_train_start(self) -> None:
        print("training started! on ", self.device)

    def on_test_start(self) -> None:
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

        #prediction = self.model(bg)
        #loss = self.loss_fn(prediction, labels)

        return loss, prediction, labels

    def training_step(self, batch, batch_idx):
        loss, prediction, labels = self.general_step(batch, batch_idx, self.train_runner, "train")
        self.log('train_loss', loss.item(), on_step=False, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        loss, prediction, labels = self.general_step(batch, batch_idx, self.val_runner, "val")
        self.log('val_loss', loss.item(), on_step=False, on_epoch=True)
        return loss

    def test_step(self, batch, batch_idx):
        loss, prediction, labels = self.general_step(batch, batch_idx, self.test_runner, "test")
        return loss