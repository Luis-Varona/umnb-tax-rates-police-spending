# %%
import os

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD,
                          '..',
                          '..',
                          'data_analysis',
                          'elasticity_results')


# %%
TITLE = "Estimated NB Municipal Tax Base Elasticity by Mean Population"
TITLESIZE = 14
XLABEL = "Mean Population from 2000\u20132018 (log scale)"
YLABEL = "Est. Elasticity from Exogenous Police Spending Effects"

XCOLUMN = "MeanPop"
YCOLUMN = "EstTaxBaseElast"


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'elasticity.xlsx')
    dest = 'elasticity.png'
    
    df = pl.read_excel(source)
    save_elasticity_plot(df, dest)


# %%
def save_elasticity_plot(df: pl.DataFrame, dest: str) -> None:
    sns.set_theme(rc={'figure.figsize': (8, 6)})
    plt.figure()
    
    plot = sns.scatterplot(df, x=XCOLUMN, y=YCOLUMN, legend=False)
    plot.set_title(TITLE, fontsize=TITLESIZE)
    plot.set_xlabel(XLABEL)
    plot.set_ylabel(YLABEL)
    
    plot.set_xscale('log')
    plot.set_xlim(1e2 / 1.1, 1e5 * 1.1)
    plot.set_xticks([10**i for i in range(2, 6)])
    plot.set_xticklabels([f"{int(i):,}" for i in plot.get_xticks()])
    
    plt.savefig(dest, dpi=300, bbox_inches='tight')
    plt.close()


# %%
if __name__ == "__main__":
    main()