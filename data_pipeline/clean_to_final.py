# %%
import os
import subprocess


# %%
def main():
    script_dir = os.path.join('helper_scripts', 'clean_to_final')
    
    for script in sorted(os.listdir(script_dir)):
        if script.startswith('_') and script.endswith('.py'):
            subprocess.run(['python', os.path.join(script_dir, script)])


# %%
if __name__ == '__main__':
    if not (wd := os.getcwd()).endswith('data_pipeline'):
        os.chdir('data_pipeline')
    
    try:
        main()
    finally:
        os.chdir(wd)