# %%
import logging
from contextlib import contextmanager


# %%
@contextmanager
def suppress_fastexcel_logging():
    logger = logging.getLogger('fastexcel.types.dtype')
    default_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    
    try:
        yield
    finally:
        logger.setLevel(default_level)