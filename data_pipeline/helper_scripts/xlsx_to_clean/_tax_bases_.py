# %%
import os
import sys
from io import BytesIO

import polars as pl
import polars.selectors as cs

sys.path.append(os.path.join((WD := os.path.dirname(__file__)),
                             '..',
                             '..',
                             '..'))
from modules.fastexcel_logging import suppress_fastexcel_logging


# %%
SOURCE_DIR = os.path.join(WD, '..', '..', 'data_xlsx')
DEST_DIR = os.path.join(WD, '..', '..', 'data_clean')


# %%
def main():
    for year in list(range(2000, 2005)) + list(range(2006, 2019)):
        source = os.path.join(SOURCE_DIR,
                              str(year),
                              f'GNB{year}_tax_base.xlsx')
        dest = os.path.join(DEST_DIR,
                            str(year),
                            f'GNB{year}_tax_base_clean.xlsx')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        with suppress_fastexcel_logging():
            (clean_tax_base_data(source)
             .write_excel(dest, header_format={'bold': True}, autofit=True))


# %%
def clean_tax_base_data(source: str) -> pl.DataFrame:
    temp_df = pl.read_excel(source, has_header=False)
    skip = next(i for i, row in enumerate(temp_df.iter_rows(), 1)
                if row[1] and row[1].title().startswith("Fredericton"))
    columns = ["Index", "Municipality",
               "General Residential Assessment",
               "Federal Residential Assessment",
               "Provincial Residential Assessment",
               "Total Residential Assessment",
               "General Non-Residential Assessment",
               "Federal Non-Residential Assessment",
               "Provincial Non-Residential Assessment",
               "Total Non-Residential Assessment",
               "Total Municipal Assessment Base",
               "Total Municipal Tax Base",
               "Total Tax Base for Rate"]
    
    with BytesIO() as buffer:
        temp_df.write_excel(buffer)
        tax_base_df = (pl.read_excel(buffer,
                                     read_options={'skip_rows': skip},
                                     has_header=False))
    
    tax_base_df = (tax_base_df
                    .select(col for col in tax_base_df
                            if col.drop_nulls().len()
                            >= tax_base_df.height / 10)
                    .select(pl.nth(list(range(13)))))
    tax_base_df = (tax_base_df
                    .rename(dict(zip(tax_base_df.columns, columns)))
                    .filter(~pl.col("Municipality")
                            .str.contains(r"^(GROUP|TOTAL|of|\*)"))
                    .with_columns(cs.exclude("Municipality")
                                    .cast(pl.Float64, strict=False))
                    .fill_null(0))
    return (combine_districts(tax_base_df)
            .with_columns(pl.col("Municipality")
                          .str.to_titlecase()
                          .str.replace_all(r"\s[-\(].*", "")
                          .str.strip_chars()
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
                                       "Sainte-Anne-de-Madawaska")))


# %%
def combine_districts(tax_base_df: pl.DataFrame) -> pl.DataFrame:
    row_iter = tax_base_df.iter_rows()
    n = tax_base_df.width
    base_idx = 0
    
    for i, row in enumerate(row_iter):
        if row[0] == 0:
            for j in range(2, n):
                tax_base_df[base_idx, j] += row[j]
        else:
            base_idx = i
    
    return (tax_base_df.filter(pl.col("Index") != 0)
            .drop("Index")
            .with_columns(cs.exclude("Municipality").cast(pl.Int64)))


# %%
if __name__ == '__main__':
    main()