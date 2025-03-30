# %%
import os
import subprocess


# %%
SCRIPT_DIR = 'xlsx_to_clean'


# %%
def main():    
    for script in os.listdir(SCRIPT_DIR):
        if script.startswith('_') and script.endswith('.py'):
            subprocess.run(['python', os.path.join(SCRIPT_DIR, script)])


# %%
if __name__ == '__main__':
    wd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    
    try:
        main()
    finally:
        os.chdir(wd)