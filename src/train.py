from re import escape
from pytorch_lightning import Trainer
import pytorch_lightning
from pytorch_lightning.loggers import WandbLogger
# from pytorch_lightning.tuner import lr_finder 
from data import CarsDataModule, make_transform_inception_v3
from model import get_inception_v3_model, get_inception_v2_model
# from task import DML, ProxyNCA
from proxyNCA import DML
dm = CarsDataModule(
    root="/mnt/vol_b/cars",
    classes=range(0, 98),
    test_classes=range(98, 196),
    batch_size=64,
    transform=make_transform_inception_v3(),
)
# dm.prepare_data()
dm.setup()
load_from_pth = "/home/ubuntu/few-shot-metric-learning/lightning_logs/version_11/checkpoints/epoch=0.ckpt"
if load_from_pth and  False:
    model = DML.load_from_checkpoint(load_from_pth)
else:   
    model = DML(
        # model=get_inception_v2_model(sz_embedding=64),
        # criterion=ProxyNCA(nb_classes=dm.num_classes, sz_embedding=64),
        nb_classes=dm.num_classes,
        pretrained=True,
        lr_backbone=0.45,
        weight_decay_backbone=0.0,
        lr_embedding=0.45,
        weight_decay_embedding=0.0,
        lr=0.001,
        weight_decay_proxynca=0.0,
        dataloader=dm.train_dataloader(),
        scaling_x=3.0,
        scaling_p=3.0,
        smoothing_const=0.1
    )
from pytorch_lightning.callbacks import LearningRateLogger
wandb_logger = WandbLogger(name='Adam-v1', project='ProxyNCA', save_dir="/mnt/vol_b/models/few-shot")
lr_logger = LearningRateLogger(logging_interval='step')
trainer = Trainer(max_epochs=100, gpus=1,
                     logger=wandb_logger,
                    #  logger=True,
                    
                    #  fast_dev_run=True,
                    #  val_check_interval=1.0,
                    #  limit_val_batches=0.0,
                    #  auto_lr_find=False,
                    #  overfit_batches=1,
                    weights_summary='full',
                    track_grad_norm=2,
                    callbacks=[lr_logger]
                     )
import wandb
# wandb.init(project="ProxyNCA", name="Adam-v1")
# wandb.watch(model, log='all')
trainer.fit(model, datamodule=dm)
trainer.test(model, datamodule=dm)
