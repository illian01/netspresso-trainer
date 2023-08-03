import os
from pathlib import Path

import torch
import numpy as np
from omegaconf import OmegaConf

from ..optimizers import build_optimizer
from ..schedulers import build_scheduler
from .base import BasePipeline
from ..utils.logger import set_logger

logger = set_logger('pipelines', level=os.getenv('LOG_LEVEL', default='INFO'))

CITYSCAPE_IGNORE_INDEX = 255  # TODO: get from configuration


class SegmentationPipeline(BasePipeline):
    def __init__(self, conf, task, model_name, model, devices, train_dataloader, eval_dataloader, class_map, **kwargs):
        super(SegmentationPipeline, self).__init__(conf, task, model_name, model, devices,
                                                   train_dataloader, eval_dataloader, class_map, **kwargs)
        self.ignore_index = CITYSCAPE_IGNORE_INDEX
        self.num_classes = train_dataloader.dataset.num_classes

    def set_train(self):

        assert self.model is not None
        self.optimizer = build_optimizer(self.model,
                                         opt=self.conf.training.opt,
                                         lr=self.conf.training.lr0,
                                         wd=self.conf.training.weight_decay,
                                         momentum=self.conf.training.momentum)
        conf_sched = OmegaConf.create({
            'epochs': self.conf.training.epochs,
            'lr_noise': None,
            'sched': 'poly',
            'decay_rate': self.conf.training.schd_power,
            'min_lr': self.conf.training.lrf,  # FIXME: add hyperparameter or approve to follow `self.conf.training.lrf`
            'warmup_lr': self.conf.training.lr0,  # self.conf.training.lr0
            'warmup_epochs': self.conf.training.warmup_epochs,  # self.conf.training.warmup_epochs
            'cooldown_epochs': 0,
        })
        self.scheduler, _ = build_scheduler(self.optimizer, conf_sched)

    def train_step(self, batch):
        self.model.train()
        images, target = batch['pixel_values'], batch['labels']
        images = images.to(self.devices)
        target = target.long().to(self.devices)

        if 'edges' in batch:
            bd_gt = batch['edges']
            bd_gt = bd_gt.to(self.devices)

        self.optimizer.zero_grad()
        out = self.model(images)
        if 'edges' in batch:
            self.loss(out, target, bd_gt=bd_gt, mode='train')
        else:
            self.loss(out, target, mode='train')

        self.loss.backward()
        self.optimizer.step()

        out = {k: v.detach() for k, v in out.items()}
        self.metric(out['pred'], target, mode='train')

        if self.conf.distributed:
            torch.distributed.barrier()

    def valid_step(self, batch):
        self.model.eval()
        images, target = batch['pixel_values'], batch['labels']
        images = images.to(self.devices)
        target = target.long().to(self.devices)

        if 'edges' in batch:
            bd_gt = batch['edges']
            bd_gt = bd_gt.to(self.devices)

        out = self.model(images)
        if 'edges' in batch:
            self.loss(out, target, bd_gt=bd_gt, mode='valid')
        else:
            self.loss(out, target, mode='valid')

        self.metric(out['pred'], target, mode='valid')

        if self.conf.distributed:
            torch.distributed.barrier()

        output_seg = torch.max(out['pred'], dim=1)[1]  # argmax

        logs = {
            'images': images.detach().cpu().numpy(),
            'target': target.detach().cpu().numpy(),
            'pred': output_seg.detach().cpu().numpy()
        }
        if 'edges' in batch:
            logs.update({
                'bd_gt': bd_gt.detach().cpu().numpy()
            })
        return {k: v for k, v in logs.items()}

    def test_step(self, batch):
        self.model.eval()
        images = batch['pixel_values']
        images = images.to(self.devices)

        out = self.model(images.unsqueeze(0))

        output_seg = torch.max(out['pred'], dim=1)[1]  # argmax

        return output_seg