import os
from pathlib import Path

import torch
import numpy as np 
from omegaconf import OmegaConf

from optimizers.builder import build_optimizer
from schedulers.builder import build_scheduler
from pipelines.base import BasePipeline
from utils.logger import set_logger

logger = set_logger('pipelines', level=os.getenv('LOG_LEVEL', default='INFO'))


class DetectionPipeline(BasePipeline):
    def __init__(self, args, task, model_name, model, devices, train_dataloader, eval_dataloader, class_map, **kwargs):
        super(DetectionPipeline, self).__init__(args, task, model_name, model, devices,
                                                   train_dataloader, eval_dataloader, class_map, **kwargs)
        self.num_classes = train_dataloader.dataset.num_classes

    def set_train(self):

        assert self.model is not None
        self.optimizer = build_optimizer(self.model,
                                         opt=self.args.train.opt,
                                         lr=self.args.train.lr0,
                                         wd=self.args.train.weight_decay,
                                         momentum=self.args.train.momentum)
        sched_args = OmegaConf.create({
            'epochs': self.args.train.epochs,
            'lr_noise': None,
            'sched': 'poly',
            'decay_rate': self.args.train.schd_power,
            'min_lr': 0,  # FIXME: add hyperparameter or approve to follow `self.args.train.lrf`
            'warmup_lr': 0.00001, # self.args.train.lr0
            'warmup_epochs': 5, # self.args.train.warmup_epochs
            'cooldown_epochs': 0,
        })
        self.scheduler, _ = build_scheduler(self.optimizer, sched_args)

    def train_step(self, batch):
        self.model.train()
        images, labels, bboxes = batch['pixel_values'], batch['label'], batch['bbox']
        images = images.to(self.devices)
        labels = labels.to(self.devices)
        bboxes = bboxes.to(self.devices)

        self.optimizer.zero_grad()
        out = self.model(images)
        self.loss(out, (labels, bboxes), mode='train')

        self.loss.backward()
        self.optimizer.step()
        
        out = {k: v.detach() for k, v in out.items()}
        self.metric(out['pred'], (labels, bboxes), mode='train')


        # # TODO: fn(out)
        # fn = lambda x: x
        # self.one_epoch_result.append(self.loss.result('train'))

        if self.args.distributed:
            torch.distributed.barrier()

    def valid_step(self, batch):
        self.model.eval()
        images, labels, bboxes = batch['pixel_values'], batch['label'], batch['bbox']
        images = images.to(self.devices)
        labels = labels.to(self.devices)
        bboxes = bboxes.to(self.devices)

        out = self.model(images)
        self.loss(out, (labels, bboxes), mode='valid')

        self.metric(out['pred'], (labels, bboxes), mode='valid')

        if self.args.distributed:
            torch.distributed.barrier()
        
        logs = {
            'images': images.detach().cpu().numpy(),
            'label': labels.detach().cpu().numpy(),
            'bbox': bboxes.detach().cpu().numpy(),
            'pred': out['pred'].detach().cpu().numpy()
        }
        return {k: v for k, v in logs.items()}