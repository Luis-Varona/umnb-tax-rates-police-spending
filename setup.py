# %%
import os
from setuptools import setup, find_packages
from Cython.Build import cythonize


# %%
cython_files = [os.path.join('modules', 'fastexcel_logging.pyx'),
                os.path.join('modules', 'run_helpers.pyx')]

setup(
    packages=find_packages(include=['modules', 'modules.*']),
    ext_modules=cythonize(
        cython_files,
        compiler_directives={'language_level': '3'},
    ),
)