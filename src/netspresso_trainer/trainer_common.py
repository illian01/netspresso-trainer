from pathlib import Path
from typing import Literal, Optional

import torch
import torch.distributed as dist
from omegaconf import DictConfig
from torch.nn.parallel import DistributedDataParallel as DDP

from .dataloaders import build_dataloader, build_dataset
from .models import SUPPORTING_TASK_LIST, build_model, is_single_task_model
from .pipelines import build_pipeline
from .utils.environment import set_device
from .utils.logger import add_file_handler, set_logger


def train_common(
    conf: DictConfig,
    task: str,
    model_name: str,
    is_graphmodule_training: bool,
    logging_dir: Path,
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
):
    distributed, world_size, rank, devices = set_device(conf.environment.seed)
    logger = set_logger(level=log_level, distributed=distributed)

    conf.distributed = distributed
    conf.world_size = world_size
    conf.rank = rank

    # Basic setup
    add_file_handler(logging_dir / "result.log", distributed=conf.distributed)

    if not distributed or dist.get_rank() == 0:
        logger.info(f"Task: {task} | Model: {model_name} | Training with torch.fx model? {is_graphmodule_training}")
        logger.info(f"Result will be saved at {logging_dir}")

    if conf.distributed and conf.rank != 0:
        torch.distributed.barrier()  # wait for rank 0 to download dataset

    single_task_model = is_single_task_model(conf.model)
    conf.model.single_task_model = single_task_model

    # Build dataloaders
    train_dataset, valid_dataset, _ = build_dataset(conf.data, conf.augmentation, task, model_name, distributed=distributed)
    assert train_dataset is not None, "For training, train split of dataset must be provided."
    if not distributed or dist.get_rank() == 0:
        logger.info(f"Summary | Dataset: <{conf.data.name}> (with {conf.data.format} format)")
        logger.info(f"Summary | Training dataset: {len(train_dataset)} sample(s)")
        if valid_dataset is not None:
            logger.info(f"Summary | Validation dataset: {len(valid_dataset)} sample(s)")

    # TODO: Temporarily set batch_size in train_dataset for RandomResize. This better to be removed later.
    train_dataset.batch_size = conf.environment.batch_size

    if conf.distributed and conf.rank == 0:
        torch.distributed.barrier()

    train_dataloader = build_dataloader(conf, task, model_name, dataset=train_dataset, phase='train')
    eval_dataloader = build_dataloader(conf, task, model_name, dataset=valid_dataset, phase='val')

    # Build model
    if is_graphmodule_training:
        assert conf.model.checkpoint.fx_model_path is not None
        assert Path(conf.model.checkpoint.fx_model_path).exists()
        model = torch.load(conf.model.checkpoint.fx_model_path)
    else:
        model = build_model(
            conf.model, task, train_dataset.num_classes,
            model_checkpoint=conf.model.checkpoint.path,
            use_pretrained=conf.model.checkpoint.use_pretrained,
        )

    model = model.to(device=devices)
    if conf.distributed:
        model = DDP(model, device_ids=[devices], find_unused_parameters=True)  # TODO: find_unused_parameters should be false (for now, PIDNet has problem)

    # Build training pipeline
    pipeline_type = 'train'
    pipeline = build_pipeline(pipeline_type=pipeline_type,
                              conf=conf,
                              task=task,
                              model_name=model_name,
                              model=model,
                              devices=devices,
                              class_map=train_dataset.class_map,
                              logging_dir=logging_dir,
                              is_graphmodule_training=is_graphmodule_training,
                              dataloaders={'train': train_dataloader, 'valid': eval_dataloader},)

    try:
        # Start train
        pipeline.train()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e
