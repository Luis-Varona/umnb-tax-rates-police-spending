# cython: language_level=3
import logging
import os
import pickle
import subprocess

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

import matplotlib.pyplot as plt
import seaborn as sns


cdef class LMResultsWrapper:
    cdef object _results
    
    def __init__(self, object results):
        self._results = results
    
    @property
    def results(self) -> object:
        return self._results
    
    def save_results(self, str dest) -> None:
        with open(dest, 'wb') as f:
            pickle.dump(self._results, f)
    
    def save_summary(self, str dest_text, str dest_latex) -> None:
        cdef object summary = self._results.summary
        
        with open(dest_text, 'w') as f:
            f.write(summary.as_text())
        
        with open(dest_latex, 'w') as f:
            f.write(summary.as_latex()
                    .replace("\\begin{table}", "\\begin{table}[H]", 1))
    
    def save_all_data(self,
                      str dest_results, str dest_text, str dest_latex) -> None:
        self.save_results(dest_results)
        self.save_summary(dest_text, dest_latex)


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
