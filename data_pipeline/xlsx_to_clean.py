# %%
import os
import subprocess


# %%
def main():
    script_dir = os.path.join('helper_scripts', 'xlsx_to_clean')
    
    for script in os.listdir(script_dir):
        if script.startswith('_') and script.endswith('.py'):
            subprocess.run(['python', os.path.join(script_dir, script)])


# %%
if __name__ == '__main__':
    wd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    
    try:
        main()
    finally:
        os.chdir(wd)