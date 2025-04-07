# %%
import os
import pickle

import polars as pl


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_pipeline', 'data_final')
SOURCE_RES = os.path.join(WD, '..', 'fe_2sls', 'stage2_results.pkl')
DEST_DIR = os.path.join(WD, '..', 'elasticity')


# %%
GROUP_COL = "Municipality"
RES_COL = "EstTaxBaseElast"


# %%
def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest = os.path.join(DEST_DIR, 'elasticity.xlsx')
    
    pol_exp_capita = pickle.load(open(SOURCE_RES, "rb")).params['PolExpCapita']
    df_final = pl.read_excel(source)
    df_elasticity = (df_final.group_by(pl.col(GROUP_COL))
                     .agg(pl.col("TaxBaseCapita").mean() * pol_exp_capita,
                          pl.col("LatestCensusPop").mean().alias("MeanPop"))
                     .with_columns((1 / pl.col("TaxBaseCapita") - 1)
                                   .alias(RES_COL))
                     .drop(pl.col("TaxBaseCapita"))
                     .sort(pl.col(GROUP_COL)))
    
    df_elasticity.write_excel(dest, header_format={'bold': True}, autofit=True)


# %%
if __name__ == '__main__':
    main()
