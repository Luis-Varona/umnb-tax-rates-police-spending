# %%
import os
import subprocess


# %%
def main():
    script_dir = 'cleaning_scripts'
    
    for script in os.listdir(script_dir):
        if script.startswith('_') and script.endswith('.py'):
            subprocess.run(['python', os.path.join(script_dir, script)])


# %%
if __name__ == '__main__':
    if (wd := os.getcwd()).endswith('cleaning_scripts'):
        os.chdir('..')
    
    try:
        main()
    finally:
        os.chdir(wd)