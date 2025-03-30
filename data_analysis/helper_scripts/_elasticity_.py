# %%
import os
import pickle

import polars as pl


# %%
SOURCE_DIR = os.path.join('..', '..', 'data_pipeline', 'data_final')
SOURCE_RES = os.path.join('..', 'fe_2sls_results', 'model_result.pkl')
DEST_DIR = os.path.join('..', 'elasticity_results')


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest = os.path.join(DEST_DIR, 'elasticity.xlsx')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    pol_exp_capita = pickle.load(open(SOURCE_RES, "rb")).params['PolExpCapita']
    df_final = pl.read_excel(source)
    df_elasticity = (df_final.group_by(pl.col("Municipality"))
                     .agg(pl.col("TaxBaseCapita").mean() * pol_exp_capita,
                          pl.col("LatestCensusPop").mean())
                     .with_columns((1 / pl.col("TaxBaseCapita") - 1)
                                   .alias("Elasticity"))
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