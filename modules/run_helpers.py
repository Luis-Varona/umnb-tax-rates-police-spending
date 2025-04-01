# %%
import os
import subprocess


# %%
def run_helpers(script_dir: str) -> None:
    for script in sorted(os.listdir(script_dir)):
        if script.startswith('_') and script.endswith('.py'):
            subprocess.run(['python', os.path.join(script_dir, script)])