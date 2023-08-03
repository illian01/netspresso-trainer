from .csv import ClassificationCSVLogger, SegmentationCSVLogger
from .visualizer import SegmentationVisualizer, DetectionVisualizer


CSV_LOGGER = {
    'classification': ClassificationCSVLogger,
    'segmentation': SegmentationCSVLogger
}

VISUALIZER = {
    'segmentation': SegmentationVisualizer,
    'detection': DetectionVisualizer,
}