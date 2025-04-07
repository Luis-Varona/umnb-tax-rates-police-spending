# %%
import sys
from setuptools import setup
from Cython.Build import cythonize


# %%
def main():
    sys.argv.extend(["build_ext", "--inplace"])
    setup(
        packages=[],
        ext_modules=cythonize(
            'utils.pyx',
            compiler_directives={'language_level': '3'},
        ),
    )


# %%
if __name__ == '__main__':
    main()
