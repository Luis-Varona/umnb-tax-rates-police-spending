# %%
import os
import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import polars as pl

sys.path.append(os.path.join(os.path.dirname(__file__), 'helper_scripts'))
from _fastexcel_logging_ import suppress_fastexcel_logging


# %%
SOURCE_DIR = 'data_raw'
DEST_DIR = 'data_xlsx'


# %%
def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    for x in os.listdir(SOURCE_DIR):
        source = os.path.join(SOURCE_DIR, x)
        
        if x.endswith(('.xlsx', '.xls', '.xlw')):
            dest = os.path.join(DEST_DIR, f'{get_file_name(x)}.xlsx')
            copy_to_dest_as_xlsx(x, source, dest)
        elif is_subdir(x, SOURCE_DIR):
            dest_parent_path = os.path.join(DEST_DIR, x)
            os.makedirs(dest_parent_path, exist_ok=True)
            
            for file in os.listdir(os.path.join(SOURCE_DIR, x)):
                if is_excel_file(file):
                    source_temp = os.path.join(source, file)
                    dest = f'{dest_parent_path}/{get_file_name(file)}.xlsx'
                    copy_to_dest_as_xlsx(file, source_temp, dest)


# %%
def copy_to_dest_as_xlsx(file: str, source: str, dest: str) -> None:
    if not is_excel_file(file):
        raise RuntimeError(f"File `{file}` is not an Excel file.")
    
    if file.endswith('.xlsx'):
        os.system(f'cp {source} {dest}')
    else:
        with suppress_fastexcel_logging():
            if file.endswith('.xls'):
                (pl.read_excel(source, has_header=False)
                 .write_excel(dest, include_header=False, autofit=True))
            else:
                with BytesIO() as buffer:
                    (pd.read_excel(source, engine='xlrd').iloc[:, :17]
                     .to_excel(buffer, header=False, index=False))
                    (pl.read_excel(buffer, has_header=False)
                     .write_excel(dest, include_header=False, autofit=True))


# %%
def is_excel_file(file: str) -> bool:
    return file.endswith(('.xlsx', '.xls', '.xlw'))

def is_subdir(file: str, dir: str) -> bool:
    return os.path.isdir(os.path.join(os.path.dirname(__file__), dir, file))

def get_file_name(file: str) -> str:
    return Path(file).stem


# %%
if __name__ == '__main__':
    wd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    
    try:
        main()
    finally:
        os.chdir(wd)