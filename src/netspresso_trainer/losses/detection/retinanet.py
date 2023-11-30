from typing import Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torchvision.ops import boxes as box_ops

from ..common import SigmoidFocalLoss
from ...models.heads.detection.experimental.detection._utils import Matcher


class RetinaNetLoss(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        fg_iou_thresh = 0.5
        bg_iou_thresh = 0.4
        self.proposal_matcher = Matcher(
                fg_iou_thresh,
                bg_iou_thresh,
                allow_low_quality_matches=True,
        )
        self.cls_loss = RetinaNetClassificationLoss(self.proposal_matcher.BETWEEN_THRESHOLDS)
        self.reg_loss = RetinaNetRegressionLoss()
    
    def compute_loss(self, out, target, matched_idxs):
        cls_loss = self.cls_loss(out, target, matched_idxs)
        box_loss = self.reg_loss(out, target, matched_idxs)

        # TODO: return as dict
        return cls_loss + box_loss

    def forward(self, out: Dict, target: torch.Tensor) -> torch.Tensor:
        matched_idxs = []
        anchors = out['anchors']

        for targets_per_image in target['gt']:
            if targets_per_image["boxes"].numel() == 0:
                matched_idxs.append(
                    torch.full((anchors.size(0),), -1, dtype=torch.int64, device=anchors.device)
                )
                continue

            match_quality_matrix = box_ops.box_iou(targets_per_image["boxes"], anchors)
            matched_idxs.append(self.proposal_matcher(match_quality_matrix))

        return self.compute_loss(out, target, matched_idxs)


class RetinaNetClassificationLoss(nn.Module):
    def __init__(self, between_threshold) -> None:
        super().__init__()
        self.between_threshold = between_threshold
        # TODO: Get from config
        alpha = 0.25
        gamma = 2
        self.focal_loss = SigmoidFocalLoss(alpha=alpha, gamma=gamma)
    
    def forward(self, out, target, matched_idxs):
        losses = []

        cls_logits = out["cls_logits"]

        for targets_per_image, cls_logits_per_image, matched_idxs_per_image in zip(target['gt'], cls_logits, matched_idxs):
            # determine only the foreground
            foreground_idxs_per_image = matched_idxs_per_image >= 0
            num_foreground = foreground_idxs_per_image.sum()

            # create the target classification
            gt_classes_target = torch.zeros_like(cls_logits_per_image)
            gt_classes_target[
                foreground_idxs_per_image,
                targets_per_image["labels"][matched_idxs_per_image[foreground_idxs_per_image]],
            ] = 1.0

            # find indices for which anchors should be ignored
            valid_idxs_per_image = matched_idxs_per_image != self.between_threshold

            # compute the classification loss
            losses.append(
                self.focal_loss(
                    {'pred': cls_logits_per_image[valid_idxs_per_image]},
                    gt_classes_target[valid_idxs_per_image],
                    reduction="sum",
                )
                / max(1, num_foreground)
            )

        return sum(losses) / len(target['gt'])


class RetinaNetRegressionLoss(nn.Module):
    def __init__(self) -> None:
        super().__init__()
    
    def forward(self, target, out, matched_idxs):
        pass