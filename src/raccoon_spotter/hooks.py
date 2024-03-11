import logging
import random

import numpy as np
import keras
import tensorflow
from kedro.framework.hooks import hook_impl

from .utils import configs


class SeedPipelineHook:
    @property
    def _logger(self):
        return logging.getLogger(__name__)

    @hook_impl
    def before_pipeline_run(self) -> None:
        seed = configs["seed"]

        # Set seed for Python's random module
        random.seed(seed)

        # Set seed for numpy
        np.random.seed(seed)

        # Set seed for torch
        # torch.manual_seed(42)
        # torch.cuda.manual_seed_all(42)

        # Set seed for keras
        keras.utils.set_random_seed(seed)
        tensorflow.random.set_seed(seed)

        self._logger.info(f"Set seed = {seed}")
