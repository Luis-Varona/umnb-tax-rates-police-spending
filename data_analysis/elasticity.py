# %%
import os

import polars as pl


# %%
SOURCE_DIR = os.path.join('..', 'data_pipeline', 'data_final')
DEST_DIR = 'elasticity_results'

POL_EXP_CAPITA = 0.5188


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest = os.path.join(DEST_DIR, 'elasticity.xlsx')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    df_final = pl.read_excel(source)
    df_elasticity = (df_final.group_by(pl.col("Municipality"))
                     .agg(pl.col("TaxBaseCapita").mean() * POL_EXP_CAPITA,
                          pl.col("LatestCensusPop").mean())
                     .with_columns((1 / pl.col("TaxBaseCapita") - 1)
                                   .alias("EstimElasticity"))
                     .drop(pl.col("TaxBaseCapita")))
    
    df_elasticity.write_excel(dest, header_format={'bold': True}, autofit=True)


# %%
if __name__ == '__main__':
    wd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    
    try:
        main()
    finally:
        os.chdir(wd)