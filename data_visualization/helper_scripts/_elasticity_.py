# %%
import os
import sys

import polars as pl
import seaborn as sns

sys.path.append(os.path.join((WD := os.path.dirname(__file__)), '..', '..'))
from utils import config_and_save_plot


# %%
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_analysis', 'elasticity')


# %%
TITLE = "Estimated NB Municipal Tax Base Elasticity by Mean Population"
TITLESIZE = 14
XLABEL = "Mean Population from 2000\u20132018 (log scale)"
YLABEL = "Estimated Elasticity $\it{(based~on}$\n" \
    "$\it{exogenous~police~spending~effects)}$"

XCOLUMN = "MeanPop"
YCOLUMN = "EstTaxBaseElast"


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'elasticity.xlsx')
    dest = os.path.join(WD, '..', 'elasticity.png')
    
    df = pl.read_excel(source)
    save_elasticity_plot(df, dest)


# %%
def save_elasticity_plot(df: pl.DataFrame, dest: str) -> None:
    with config_and_save_plot(dest):
        plot = sns.scatterplot(df, x=XCOLUMN, y=YCOLUMN, legend=False)
        plot.set_title(TITLE, fontsize=TITLESIZE)
        plot.set_xlabel(XLABEL)
        plot.set_ylabel(YLABEL)
        
        plot.set_xscale('log')
        plot.set_xlim(1e2 / 1.1, 1e5 * 1.1)
        plot.set_xticks([10**i for i in range(2, 6)])
        plot.set_xticklabels([f"{int(i):,}" for i in plot.get_xticks()])


# %%
if __name__ == "__main__":
    main()