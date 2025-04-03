# cython: language_level=3
import logging
import os
import subprocess

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

import matplotlib.pyplot as plt
import seaborn as sns


cdef void run_script(str script):
    subprocess.run(['python', script])

def run_helpers(str script_dir, bint concurrent=True) -> None:
    cdef list[str] scripts = []
    cdef object entry
    cdef str name
    cdef str script
    
    for entry in os.scandir(script_dir):
        if (name := entry.name).startswith('_') and name.endswith('.py'):
            scripts.append(entry.path)
    
    if concurrent:
        with ThreadPoolExecutor() as executor:
            executor.map(run_script, scripts)
    else:
        for script in sorted(scripts):
            run_script(script)


@contextmanager
def suppress_fastexcel_logging() -> None:
    cdef object logger = logging.getLogger('fastexcel.types.dtype')
    cdef int default_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    
    try:
        yield
    finally:
        logger.setLevel(default_level)


@contextmanager
def config_and_save_plot(str dest) -> None:
    sns.set_theme(rc={'figure.figsize': (8, 6)})
    plt.figure()
    
    try:
        yield
    finally:
        plt.savefig(dest, dpi=300, bbox_inches='tight')
        plt.close()