# %%
import os
import sys

sys.path.append(os.path.join((WD := os.path.dirname(__file__)), '..'))
from utils import run_helpers


# %%
def main():
    script_dir = os.path.join(WD, 'helper_scripts')
    run_helpers(script_dir, False)


# %%
if __name__ == '__main__':
    main()
