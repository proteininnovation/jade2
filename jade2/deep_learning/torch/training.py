from copy import deepcopy
import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as util
import pandas
from typing import List
from torch.utils.tensorboard import SummaryWriter
from .hyperparameters.Parameters import Params
from pytorch_lightning import loggers as pl_loggers
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping

def prepare_directories(experiment):
    """
    Prepare directories for lightning training.
    Create if not present, clear old keys, etc.
    """
    if not os.path.exists(experiment):
        os.mkdir(experiment)
    key_file = experiment+'/run_keys.txt'

    if os.path.exists(key_file):
        os.remove(key_file)

    best_dir = experiment+'/best'
    if not os.path.exists(best_dir):
        os.mkdir(best_dir)

def run_with_lightning(model, data_loader,
                       experiment: str,
                       hp: Params,
                       gpus: int, cpus: int,
                       max_epochs: int,
                       best_model_callback,
                       out_data: List,
                       run=1, monitor='val_loss', stop_patience = 15):
    """
    Function to run with lightning with each combo - for hp tuning.

    1. Everything is logged through tensorboard.
    2. EarlyStopping will stop a run at a default patience of 5.
    3. Saves the best model found per run according to set value.  Not sure how to do more than val_loss at this time.
    4. Writes a JSON file with all output data and hp inputs for IAE
    5. Writes a txt file to get run number with hyperparameters.

    :return:
    """
    early_stop_callback = EarlyStopping(monitor='val_loss', min_delta=0.00, patience=stop_patience, verbose=True, mode='min')
    per_permute_model = ModelCheckpoint(
        monitor=monitor,
        dirpath=experiment+'/chk/'+str(run),
        filename='best_hp-{epoch:02d}-{val_loss:.4f}',
        save_top_k=1,
        mode='min',
    )

    #Note that without that default_hp_metric, you will NOT be able to ACTUALLY log hp metrics.
    ## Such a stupid fucking thing to do.
    tb_logger = pl_loggers.TensorBoardLogger(experiment+'/logs/'+str(run), default_hp_metric=False)

    trainer = Trainer(logger=tb_logger, callbacks=[best_model_callback, early_stop_callback, per_permute_model],
                      max_epochs=max_epochs, min_epochs=1,
                      auto_lr_find=False, auto_scale_batch_size=False,
                      gpus=gpus,
                      num_processes= cpus,
                      progress_bar_refresh_rate=1,
                      num_sanity_val_steps=0)


    trainer.fit(model, data_loader)
    print("Done fitting for run. ", run, "Evaluating best model.")

    best_model = per_permute_model.best_model_path
    print('best_model', best_model)

    #Add optional model path.
    # If we do that, we need to also setup the dataloader
    trainer.test(ckpt_path=best_model)

    #Write resultant data to a json for easy analysis in IAE
    out_df_data = dict()
    out_df_data.update(trainer.model.out_data)
    out_df_data.update(hp.data)

    out_data.append(out_df_data)
    out_df = pandas.DataFrame.from_dict(out_data)
    out_df.to_json(experiment+'/out_data.json', orient='records', lines=True)

    #Write hyperparemeters to text file for quick lookup.
    key_file = experiment+'/run_keys.txt'
    if not os.path.exists(key_file):
        m = 'w'
    else:
        m = 'a'
    exp_keys = open(key_file, m)

    out = []
    for key in hp.data:
        out.append(key+"="+str(hp[key]))
    exp_keys.write(str(run)+" : "+" ".join(out)+'\n\n')
    exp_keys.close()
    print("Done hp run", run)

def run_torch_model_general(
        writer:          SummaryWriter,
        model:           nn.Module,
        loss_fn:         nn.Module,
        train_loader:    util.DataLoader,
        test:            torch.Tensor,
        test_target:     torch.Tensor,
        n_epochs=        100,
        lr=              1e-4,
        zero_gradients = True,
        use_SGD=         False,
        data_parellel =  True) -> (List, List, nn.Module):
    """
    A very basic function to run a torch model.
    Returns losses_train, losses_val, best_model

    best_model is the model with the best on validation test.
    """
    if data_parellel:
        model = nn.DataParallel(model)

    if use_SGD:
        optimizer = optim.SGD(model.parameters(), lr=lr)
    else:
        optimizer = optim.Adam(model.parameters(), lr=lr)


    losses_train = []
    losses_val = []

    best_loss = 1
    best_model = model

    #Zero the gradiants, else we are continuing to optimize instead of starting over.
    if zero_gradients:
        optimizer.zero_grad()
        model.zero_grad()

    for epoch in range(n_epochs+1):
        loss_train = 0
        for data, to_train in train_loader:
            #outputs = model(imgs.view(imgs.shape[0], -1))
            outputs = model(data)

            loss = loss_fn(outputs, to_train)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loss_train += loss.item()

        with torch.no_grad():
            val_outputs = model(test)
            loss_val = loss_fn(val_outputs, test_target)

        if float(loss_val) < best_loss:
            best_loss = loss_val
            best_model = deepcopy(model)

        loss_train_avg = loss_train/len(train_loader)

        losses_train.append(loss_train_avg)
        losses_val.append(float(loss_val))

        writer.add_scalar("Loss/Train", loss_train_avg, epoch)
        writer.add_scalar("Loss/Val", loss_val, epoch)
        writer.add_scalar("Best/Loss", best_loss, epoch)

        #Add the weight changes.
        for name, weight in model.named_parameters():
            writer.add_histogram(name,weight, epoch)
            writer.add_histogram(f'{name}.grad',weight.grad, epoch)

        print(f"Epoch: {epoch}, Loss: {loss_train_avg:.4f} ValLoss: {float(loss_val):.4f}" )

    return losses_train, losses_val, best_model