# cython: language_level=3
import logging
from contextlib import contextmanager

@contextmanager
def suppress_fastexcel_logging():
    cdef object logger = logging.getLogger('fastexcel.types.dtype')
    cdef int default_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    
    try:
        yield
    finally:
        logger.setLevel(default_level)