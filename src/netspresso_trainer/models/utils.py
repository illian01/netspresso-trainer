from pathlib import Path
from typing import Any, List, TypedDict, Optional, Union
import logging

import torch
import torch.nn as nn
from torch import Tensor
from torch.fx.proxy import Proxy
import omegaconf

logger = logging.getLogger("netspresso_trainer")

FXTensorType = Union[Tensor, Proxy]
FXTensorListType = Union[List[Tensor], List[Proxy]]


class BackboneOutput(TypedDict):
    intermediate_features: Optional[FXTensorListType]
    last_feature: Optional[FXTensorType]


class ModelOutput(TypedDict):
    pred: FXTensorType


class DetectionModelOutput(ModelOutput):
    boxes: Any
    proposals: Any
    anchors: Any
    objectness: Any
    pred_bbox_detlas: Any
    class_logits: Any
    box_regression: Any
    labels: Any
    regression_targets: Any
    post_boxes: Any
    post_scores: Any
    post_labels: Any


class PIDNetModelOutput(ModelOutput):
    extra_p: Optional[FXTensorType]
    extra_d: Optional[FXTensorType]


def load_from_checkpoint(model: nn.Module, model_checkpoint: Optional[Union[str, Path]]) -> nn.Module:
    if model_checkpoint is not None:
        model_state_dict = torch.load(model_checkpoint, map_location='cpu')
        missing_keys, unexpected_keys = model.load_state_dict(model_state_dict, strict=False)

        if len(missing_keys) != 0:
            logger.warning(f"Missing key(s) in state_dict: {missing_keys}")
        if len(unexpected_keys) != 0:
            logger.warning(f"Unexpected key(s) in state_dict: {unexpected_keys}")

    return model


def load_model_name(conf_model_sub: Union[omegaconf.DictConfig, str]):
    if isinstance(conf_model_sub, (omegaconf.DictConfig, omegaconf.ListConfig, dict, list)):
        assert hasattr(conf_model_sub, 'type')
        model_name: str = conf_model_sub.type
    else:
        assert isinstance(conf_model_sub, str)
        model_name = conf_model_sub
    return model_name.lower()
