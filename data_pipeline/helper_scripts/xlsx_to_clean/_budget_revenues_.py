# %%
import os
import sys
from io import BytesIO

import polars as pl
import polars.selectors as cs

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from _fastexcel_logging_ import suppress_fastexcel_logging


# %%
def main():
    for year in list(range(2000, 2005)) + list(range(2006, 2019)):
        source = os.path.join('data_xlsx',
                              str(year),
                              f'GNB{year}_bgt_revs.xlsx')
        dest = os.path.join('data_clean',
                            str(year),
                            f'GNB{year}_bgt_revs_clean.xlsx')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        with suppress_fastexcel_logging():
            (clean_bgt_revs_data(source)
             .write_excel(dest, header_format={'bold': True}, autofit=True))


# %%
def clean_bgt_revs_data(source: str) -> pl.DataFrame:
    temp_df = pl.read_excel(source, has_header=False)
    skip = next(i for i, row in enumerate(temp_df.iter_rows(), 1)
                if row[1] and row[1].title().startswith("Fredericton"))
    columns = ["Index", "Municipality",
               "Warrant", "Unconditional Grant",
               "Services to Other Governments", "Sale of Services",
               "Own-Source Revenue",
               "Conditional Transfers", "Other Transfers",
               "Biennial Surplus", "Total Revenue"]
    
    with BytesIO() as buffer:
        temp_df.write_excel(buffer)
        revenue_df = (pl.read_excel(buffer,
                                    read_options={'skip_rows': skip},
                                    has_header=False))
    
    revenue_df = (revenue_df
                  .select(col for col in revenue_df
                          if col.drop_nulls().len()
                          >= revenue_df.height / 10)
                  .select(pl.nth(list(range(11)))))
    return (revenue_df
            .rename(dict(zip(revenue_df.columns, columns)))
            .filter(~pl.col("Index").str.contains(r"\D"))
            .drop("Index")
            .with_columns(cs.exclude("Municipality").cast(pl.Int64))
            .with_columns(pl.col("Municipality")
                          .str.to_titlecase()
                          .str.replace_all(r"\n\s*", "")
                          .str.replace_all(r'\\', "/")
                          .str.replace_all(r"-\s*", "-")
                          .str.replace_all(" De ", " de ")
                          .str.replace_all("-De-", "-de-")
                          .str.replace(r"^Aroostock$",
                                       "Aroostook")
                          .str.replace(r"^Baker Brook$",
                                       "Baker-Brook")
                          .str.replace(r"^Grande Anse$",
                                       "Grande-Anse")
                          .str.replace(r"^Grand Bay/Westfield$",
                                       "Grand Bay-Westfield")
                          .str.replace(r"^Grand-Falls/Grand-Sault$",
                                       "Grand Falls/Grand-Sault")
                          .str.replace(r"^Grand-Sault\s*/\s*Grand(\s|-)Falls$",
                                       "Grand Falls/Grand-Sault")
                          .str.replace(r"^Lac-Baker$",
                                       "Lac Baker")
                          .str.replace(r"^Lameque$",
                                       "Lamèque")
                          .str.replace(r"^Mcadam$",
                                       "McAdam")
                          .str.replace(r"^Neguac$",
                                       "Néguac")
                          .str.replace(r"^Saint-Francois-de-Madawaska$",
                                       "Saint-François-de-Madawaska")
                          .str.replace(r"^Saint-Louis de Kent$",
                                       "Saint-Louis-de-Kent")
                          .str.replace(r"^Sainte-Marie-Saint-Rapha(e|ê)l$",
                                       "Sainte-Marie-Saint-Raphaël")
                          .str.replace(r"^Shédiac$",
                                       "Shediac")
                          .str.replace(r"^St-Hilaire$",
                                       "Saint-Hilaire")
                          .str.replace(r"^St-Isidore$",
                                       "Saint-Isidore")
                          .str.replace(r"^St. Andrews$",
                                       "Saint Andrews")
                          .str.replace(r"^St. George$",
                                       "Saint George")
                          .str.replace(r"^Ste-Anne-de-Madawaska$",
                                       "Sainte-Anne-de-Madawaska"))
            .fill_null(0))


# %%
if __name__ == '__main__':
    if (wd := os.getcwd()).endswith('xlsx_to_clean'):
        os.chdir('../..')
    elif wd.endswith('helper_scripts'):
        os.chdir('..')
    elif not wd.endswith('data_pipeline'):
        os.chdir('data_pipeline')
    
    try:
        main()
    finally:
        os.chdir(wd)