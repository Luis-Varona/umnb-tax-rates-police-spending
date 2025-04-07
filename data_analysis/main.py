# %%
import os
import sys

sys.path.append(os.path.join((WD := os.path.dirname(__file__)), '..'))
from utils import run_helpers


# %%
def main():
    script_dir1 = os.path.join(WD, 'helper_scripts', 'allow_concurrent')
    script_dir2 = os.path.join(WD, 'helper_scripts', 'second_run')
    run_helpers(script_dir1)
    run_helpers(script_dir2)


# %%
if __name__ == '__main__':
    main()
