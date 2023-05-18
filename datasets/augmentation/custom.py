from typing import Sequence

import torch
import torchvision.transforms as T
import torchvision.transforms.functional as F

class Pad(T.Pad):
    pass

class Resize(T.Resize):
    pass

class RandomHorizontalFlip(T.RandomHorizontalFlip):
    pass

class PadIfNeeded(torch.nn.Module):
    def __init__(self, size, fill=0, padding_mode="constant"):
        super().__init__()
        if not isinstance(size, (int, Sequence)):
            raise TypeError("Size should be int or sequence. Got {}".format(type(size)))
        if isinstance(size, Sequence) and len(size) not in (1, 2):
            raise ValueError("If size is a sequence, it should have 1 or 2 values")
        self.new_h = size[0] if isinstance(size, Sequence) else size
        self.new_w = size[1] if isinstance(size, Sequence) else size
        self.fill = fill
        self.padding_mode = padding_mode

    def forward(self, img):
        if not isinstance(img, (torch.Tensor, Image.Image)):
            raise TypeError("Image should be Tensor or PIL.Image. Got {}".format(type(img)))
        
        if isinstance(img, Image.Image):
            w, h = img.size
        else:
            w, h = img.shape[-1], img.shape[-2]
        
        w_pad_needed = max(0, self.new_w - w)
        h_pad_needed = max(0, self.new_h - h)
        padding_ltrb = [w_pad_needed // 2,
                        h_pad_needed // 2,
                        w_pad_needed // 2 + w_pad_needed % 2,
                        h_pad_needed // 2 + h_pad_needed % 2]
        return F.pad(img, padding_ltrb, self.fill, self.padding_mode)

    def __repr__(self):
        return self.__class__.__name__ + '(min_size={0}, fill={1}, padding_mode={2})'.\
            format((self.new_h, self.new_w), self.fill, self.padding_mode)

class ColorJitter(T.ColorJitter):
    pass

class RandomCrop(T.RandomCrop):
    pass

class Normalize(T.Normalize):
    pass

class AutoAugment(T.AutoAugment):
    pass

class RandomResizedCrop(T.RandomResizedCrop):
    pass

if __name__ == '__main__':
    from pathlib import Path
    
    import PIL.Image as Image
    import albumentations as A
    import cv2
    import numpy as np
    input_filename = Path("astronaut.jpg")
    im = Image.open(input_filename)
    im_array = np.array(im)
    print(f"Original image size (in array): {im_array.shape}")
    
    """Pad"""
    torch_aug = PadIfNeeded(size=(1024, 1024))
    im_torch_aug: Image.Image = torch_aug(im)
    im_torch_aug.save(f"{input_filename.stem}_torch{input_filename.suffix}")
    print(f"Aug image size (from torchvision): {np.array(im_torch_aug).shape}")
    
    album_aug = A.PadIfNeeded(min_height=1024, min_width=1024, border_mode=cv2.BORDER_CONSTANT)
    im_album_aug: np.ndarray = album_aug(image=im_array)['image']
    Image.fromarray(im_album_aug).save(f"{input_filename.stem}_album{input_filename.suffix}")
    print(f"Aug image size (from albumentations): {im_album_aug.shape}")

    print(np.all(np.array(im_torch_aug) == im_album_aug), np.mean(np.abs(np.array(im_torch_aug) - im_album_aug)))
    