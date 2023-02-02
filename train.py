import argparse
import os
from pathlib import Path

import torch
from omegaconf import OmegaConf

from datasets import build_dataset, build_dataloader
from models import build_model
from pipelines import ClassificationPipeline, SegmentationPipeline
from utils.environment import set_device
from utils.logger import set_logger

SUPPORT_TASK = ['classification', 'segmentation']
logger = set_logger('train', level=os.getenv('LOG_LEVEL', 'INFO'))


def parse_args_netspresso():

    parser = argparse.ArgumentParser(description="Parser for NetsPresso configuration")
    
    # -------- User arguments ----------------------------------------
    
    parser.add_argument(
        '--config', type=str, default='',
        dest='config', 
        help="Config path")
    
    parser.add_argument(
        '-o', '--output_dir', type=str, default='..',
        dest='output_dir', 
        help="Checkpoint and result saving directory")
    
    parser.add_argument(
        '--profile', action='store_true',
        help="Whether to use profile mode")
    
    parser.add_argument(
        '--report-modelsearch-api', action='store_true',
        help="Report elapsed time for single epoch to NetsPresso Modelsearch API")

    args, _ = parser.parse_known_args()    
    
    return args

def train():
    args_parsed = parse_args_netspresso()
    args = OmegaConf.load(args_parsed.config)
    distributed, world_size, rank, devices = set_device(args)
    
    args.distributed = distributed
    args.world_size = world_size
    args.rank = rank
    
    task = str(args.train.task).lower()
    assert task in SUPPORT_TASK
    
    if args.distributed and args.rank != 0:
        torch.distributed.barrier() # wait for rank 0 to download dataset
        
    train_dataset, eval_dataset = build_dataset(args)
    
    if args.distributed and args.rank == 0:
        torch.distributed.barrier()
        
    model = build_model(args, train_dataset.num_classes)
    
    train_dataloader, eval_dataloader = \
        build_dataloader(args, model, train_dataset=train_dataset, eval_dataset=eval_dataset, profile=args_parsed.profile)

    model = model.to(device=devices)
    if task == 'classification':
        trainer = ClassificationPipeline(args, model, devices, train_dataloader, eval_dataloader,
                                         is_online=args_parsed.report_modelsearch_api, profile=args_parsed.profile)
    elif task == 'segmentation':
        trainer = SegmentationPipeline(args, model, devices, train_dataloader, eval_dataloader,
                                        is_online=args_parsed.report_modelsearch_api, profile=args_parsed.profile)

    else:
        raise AssertionError(f"No such task! (task: {task})")
    
    trainer.set_train()
    trainer.train()
    
if __name__ == '__main__':
    train()