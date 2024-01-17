# Transforms

Users can easily create their own augmentation recipe simply by listing their desired data transform modules. It's possible to adjust the intensity and frequency of each transform module, and the listed transform modules are applied in sequence to produce augmented data. In NetsPresso Trainer, a visualization tool is also provided through a Gradio demo, allowing users to see how their custom augmentation recipe produces the data for the model.

## Supporting transforms

The currently supported methods in NetsPresso Trainer are as follows. Since techniques are adapted from pre-existing codes, most of the parameters remain unchanged. We note that most of these parameter descriptions are derived from original implementations.

We appreciate all the original code owners and we also do our best to make other values.

### CenterCrop

This augmentation follows the [CenterCrop](https://pytorch.org/vision/0.15/generated/torchvision.transforms.CenterCrop.html) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "centercrop" to use `CenterCrop` transform. |
| `size` | (int or list) Desired output size of the crop. If size is an int, a square crop (size, size) is made. If provided a list of length 1, it will be interpreted as (size[0], size[0]). If a list of length 2 is provided, a square crop (size[0], size[1]) is made. |

<details>
  <summary>CenterCrop example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: centercrop
        size: 224
  ```
</details>

### ColorJitter

This augmentation follows the [ColorJitter](https://pytorch.org/vision/0.15/generated/torchvision.transforms.ColorJitter.html?highlight=colorjitter#torchvision.transforms.ColorJitter) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "colorjitter" to use `ColorJitter` transform. |
| `brightness` | (float or list) The brightness scale value is randomly selected within [max(0, 1 - brightness), 1 + brightness] or given [min, max] range. |
| `contrast` | (float or list) The contrast scale value is randomly selected within [max(0, 1 - contrast), 1 + contrast] or given [min, max] range. |
| `saturation` | (float or list) The saturation scale value is randomly selected within [max(0, 1 - saturation), 1 + saturation] or given [min, max] range. |
| `hue` | (float or list) The hue scale value is randomly selected within [max(0, 1 - hue), 1 + hue] or given [min, max] range. |
| `p` | (float) The probability of applying the color jitter. If set to `1.0`, the color transform is always applied. |

<details>
  <summary>ColorJitter example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: colorjitter
        brightness: 0.25
        contrast: 0.25
        saturation: 0.25
        hue: 0.1
        p: 1.0
  ```
</details>

### Pad

Pad an image. This augmentation follows the [Pad](https://pytorch.org/vision/0.15/generated/torchvision.transforms.Pad.html#torchvision.transforms.Pad) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "pad" to use `Pad` transform. |
| `padding` | (int or list) Padding on each border. If a single int is provided this is used to pad all borders. If list of length 2 is provided this is the padding on left/right and top/bottom respectively. If a list of length 4 is provided this is the padding for the left, top, right and bottom borders respectively. |
| `fill` | (int or list) This value is only for when the `padding_mode` is "constant". If a single int is provided this is used to fill pixels with constant value. If a list of length 3, it is used to fill R, G, B channels respectively. |
| `padding_mode` | (str) Type of padding. Should be: constant, edge, reflect, or symmetric. |

<details>
  <summary>Pad example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: pad
        padding: 1
        fill: 0
        padding_mode: constant
  ```
</details>

### RandomCrop

Crop the given image at a random location. This augmentation follows the [RandomCrop](https://pytorch.org/vision/0.15/generated/torchvision.transforms.RandomCrop.html#torchvision.transforms.RandomCrop) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "randomcrop" to use `RandomCrop` transform. |
| `size` | (int or list) Desired output size of the crop. If size is an int, a square crop (size, size) is made. If provided a list of length 1, it will be interpreted as (size[0], size[0]). If a list of length 2 is provided, a square crop (size[0], size[1]) is made. |

<details>
  <summary>RandomCrop example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: randomcrop
        size: 256
  ```
</details>

### RancomErasing

Erase random area of given image. This augmentation follows the [RandomErasing](https://pytorch.org/vision/0.15/generated/torchvision.transforms.RandomErasing.html#torchvision.transforms.RandomErasing) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "randomerasing" to use `RancomErasing` transform. |
| `p` | (float) The probability of applying random erasing. If `1.0`, it always applies. |
| `scale` | (list) Range of proportion of erased area against input image. |
| `ratio` | (list) Range of aspect ratio of erased area. |
| `value` | (int, optional) Erasing value. If `None`, erase image with random noise. |
| `inplace` | (bool) Whether to operate as inplace. |

<details>
  <summary>RandomErasing example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: randomerasing
        p: 0.5
        scale: [0.02, 0.33]
        ratio: [0.3, 3.3]
        value: 0
        inplace: False
  ```
</details>

### RandomHorizontalFlip

Horizontally flip the given image randomly with a given probability. This augmentation follows the [RandomHorizontalFlip](https://pytorch.org/vision/0.15/generated/torchvision.transforms.RandomHorizontalFlip.html#torchvision.transforms.RandomHorizontalFlip) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "randomhorizontalflip" to use `RandomHorizontalFlip` transform. |
| `p` | (float) the probability of applying horizontal flip. If `1.0`, it always applies the flip. |

<details>
  <summary>RandomHorizontalFlip example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: randomhorizontalflip
        p: 0.5
  ```
</details>

### RandomResizedCrop

Crop a random portion of image with different aspect of ratio in width and height, and resize it to a given size. This augmentation follows the [RandomResizedCrop](https://pytorch.org/vision/0.15/generated/torchvision.transforms.RandomResizedCrop.html#torchvision.transforms.RandomResizedCrop) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "randomresizedcrop" to use `RandomResizedCrop` transform. |
| `size` | (int or list) Desired output size of the crop. If size is an int, a square crop (`size`, `size`) is made. If provided a list of length 1, it will be interpreted as (`size[0]`, `size[0]`). If a list of length 2 is provided, a crop with size (`size[0]`, `size[1]`) is made. |
| `scale` | (float or list) Specifies the lower and upper bounds for the random area of the crop, before resizing. The scale is defined with respect to the area of the original image. |
| `ratio` | (float or list) lower and upper bounds for the random aspect ratio of the crop, before resizing. |
| `interpolation` | (str) Desired interpolation type. Supporting interpolations are 'nearest', 'bilinear' and 'bicubic'. |

<details>
  <summary>RandomResizedCrop</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: randomresizedcrop
        size: 256
        scale: [0.08, 1.0]
        ratio: [0.75, 1.33]
        interpolation: 'bilinear'
  ```
</details>


### RandomVerticalFlip

Vertically flip the given image randomly with a given probability. This augmentation follows the [RandomVerticalFlip](https://pytorch.org/vision/0.15/generated/torchvision.transforms.RandomVerticalFlip.html#torchvision.transforms.RandomVerticalFlip) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "randomverticalflip" to use `RandomVerticalFlip` transform. |
| `p` | (float) the probability of applying vertical flip. If `1.0`, it always applies the flip. |

<details>
  <summary>RandomVerticalFlip example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: randomverticalflip
        p: 0.5
  ```
</details>

### Resize

Naively resize the input image to the given size. This augmentation follows the [Resize](https://pytorch.org/vision/0.15/generated/torchvision.transforms.Resize.html#torchvision.transforms.Resize) in torchvision library.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "resize" to use `Resize` transform. |
| `size` | (int or list) Desired output size. If size is an int, a square image (`size`, `size`) is made. If provided a list of length 1, it will be interpreted as (`size[0]`, `size[0]`). If a list of length 2 is provided, an image with size (`size[0]`, `size[1]`) is made. |
| `interpolation` | (str) Desired interpolation type. Supporting interpolations are 'nearest', 'bilinear' and 'bicubic'. |
| `max_size` | (int, optional) The maximum allowed for the longer edge of the resized image: if the longer edge of the image exceeds `max_size` after being resized according to `size`, then the image is resized again so that the longer edge is equal to `max_size`. As a result, `size` might be overruled, i.e the smaller edge may be shorter than `size`. This is only supported if `size` is an int. |

<details>
  <summary>Resize example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: resize
        size: [256, 256]
        interpolation: 'bilinear'
        max_size: ~
  ```
</details>

### TrivialAugmentWide

TrivialAugment based on [TrivialAugment: Tuning-free Yet State-of-the-Art Data Augmentation](https://openaccess.thecvf.com/content/ICCV2021/papers/Muller_TrivialAugment_Tuning-Free_Yet_State-of-the-Art_Data_Augmentation_ICCV_2021_paper.pdf). This augmentation follows the [TrivialAugmentWide](https://pytorch.org/vision/0.15/generated/torchvision.transforms.TrivialAugmentWide.html#torchvision.transforms.TrivialAugmentWide) in the torchvision library. Currently, this transform function does not support segmentation and detection data.

| Field <img width=200/> | Description |
|---|---|
| `name` | (str) Name must be "trivialaugmentwide" to use `TrivialAugmentWide` transform. |
| `num_magnitude_bins` | (int) The number of different magnitude values. |
| `interpolation` | (str) Desired interpolation type. Supporting interpolations are 'nearest', 'bilinear' and 'bicubic'. |
| `fill` | (list or int, optional) Pixel fill value for the area outside the transformed image. If given a number, the value is used for all bands respectively. |

<details>
  <summary>TrivialAugmentWide example</summary>
  
  ```yaml
  augmentation:
    transforms:
      - 
        name: trivialaugmentwide
        num_magnitude_bins: 31
        interpolation: 'bilinear'
        fill: ~
  ```
</details>