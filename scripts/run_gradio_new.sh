#!/bin/bash

cd "$(dirname ${0})/.."

export PATH_AUG_DOCS="demo/docs/description_augmentation.md"
export PATH_AUG_EXAMPLE_CONFIG="config/augmentation/template/common.yaml"
export PATH_SCHEDULER_DOCS="demo/docs/description_lr_scheduler.md"
export PATH_SCHEDULER_EXAMPLE_CONFIG="config/training/template/common.yaml"

python demo/gradio_new.py\
  --image assets/kyunghwan_cat.jpg\
  --local --port 50003