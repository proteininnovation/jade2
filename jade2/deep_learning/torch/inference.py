from pytorch_lightning.utilities.cloud_io import load as pl_load

def load_pt_lightning_model(lightning_module, chk: str):
    """
    Load a lightning model from a checkpoint.  Must create the module first.
    This works this way as the general way with PT lightning is very buggy.
    """
    checkpoint = pl_load(chk, map_location=lambda storage, loc: storage)

    # give model a chance to load something
    lightning_module.on_load_checkpoint(checkpoint)

    # load the state_dict on the model automatically
    lightning_module.load_state_dict(checkpoint['state_dict'], strict=0)
    return lightning_module