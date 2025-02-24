# %%
import logging
import os
import shutil
from io import BytesIO
from pathlib import Path

import pandas as pd
import polars as pl


# %%
def main():
    dest_dir = os.path.join(os.getcwd(), '../data_xlsx')
    
    if os.path.exists(dest_dir):
        raise RuntimeError(f"Folder `{dest_dir}` exists; conversion "
                           "of raw GNB data may already be complete.")
    
    os.mkdir(dest_dir)
    
    for x in os.listdir():
        if x.endswith(('.xlsx', '.xls', '.xlw')):
            dest = os.path.join(dest_dir, f'{get_file_name(x)}.xlsx')
            copy_to_dest_as_xlsx(x, x, dest)
        elif is_subdir(x):
            dest_parent_path = os.path.join(dest_dir, x)
            os.mkdir(dest_parent_path)


            for file in filter(is_excel_file, os.listdir(x)):
                dest = f"{dest_parent_path}/{get_file_name(file)}.xlsx"
                copy_to_dest_as_xlsx(file, f'{x}/{file}', dest)


# %%
def copy_to_dest_as_xlsx(file: str, source: str, dest: str) -> None:
    if not is_excel_file(file):
        raise RuntimeError(f"File `{file}` is not an Excel file.")
    
    if file.endswith('.xlsx'):
        shutil.copy(source, dest)
    else:
        logger = logging.getLogger('fastexcel.types.dtype')
        default_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        
        try:
            if file.endswith('.xls'):
                (pl.read_excel(source, has_header=False)
                 .write_excel(dest, include_header=False, autofit=True))
            else:
                with BytesIO() as buffer:
                    (pd.read_excel(source, engine='xlrd').iloc[:, :11]
                     .to_excel(buffer, header=False, index=False))
                    (pl.read_excel(buffer, has_header=False)
                     .write_excel(dest, include_header=False, autofit=True))
        finally:
            logger.setLevel(default_level)


# %%
def is_excel_file(file: str) -> bool:
    return file.endswith(('.xlsx', '.xls', '.xlw'))

def is_subdir(file: str) -> bool:
    return os.path.isdir(os.path.join(os.getcwd(), file))

def get_file_name(file: str) -> str:
    return Path(file).stem


# %%
if __name__ == '__main__':
    if not (wd := os.getcwd()).endswith('data_raw'):
        os.chdir(os.path.join(wd, 'data_raw'))
    
    try:
        main()
    finally:
        os.chdir(wd)