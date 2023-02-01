import os
from pathlib import Path
import logging

import PIL.Image as Image
import torch
import torch.utils.data as data

from datasets.utils.parsers import create_parser
from datasets.base import BaseCustomDataset
from utils.logger import set_logger

logger = set_logger('datasets', level=os.getenv('LOG_LEVEL', default='INFO'))

_ERROR_RETRY = 50
_MAPPING_TXT_FILE = "mapping.txt"

class ClassificationCustomDataset(BaseCustomDataset):

    def __init__(
            self,
            args,
            root,
            split,
            parser=None,
            load_bytes=False,
            transform=None,
            target_transform=None,
    ):
        super(ClassificationCustomDataset, self).__init__(
            args,
            root,
            split,
            parser,
            load_bytes,
            transform,
            target_transform
        )
        _class_map_maybe = Path(args.train.data) / _MAPPING_TXT_FILE
        class_map = _class_map_maybe if _class_map_maybe.exists() else None
        if parser is None or isinstance(parser, str):
            parser = create_parser(parser or '', root=root, split=split, class_map=class_map)
        self.parser = parser
        self._num_classes = self.parser.num_classes
        
    def __getitem__(self, index):
        img, target = self.parser[index]
        try:
            img = img.read() if self.load_bytes else Image.open(img).convert('RGB')
        except Exception as e:
            logger.warning(f"Skipped sample (index {index}, file {self.parser.filename(index)}). {str(e)}")
            self._consecutive_errors += 1
            if self._consecutive_errors < _ERROR_RETRY:
                return self.__getitem__((index + 1) % len(self.parser))
            else:
                raise e
        self._consecutive_errors = 0
        if self.transform is not None:
            img = self.transform(img)
        if target is None:
            target = -1
        elif self.target_transform is not None:
            target = self.target_transform(target)
        return img, target