# %%
import os
import pickle
import re
from io import StringIO

import polars as pl
from unidecode import unidecode


# %%
WD = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(WD, '..', 'data_pipeline', 'data_final')
DEST_DIR = os.path.join(WD, 'results')


# %%
YEARS = [2001, 2006, 2016, 2021]
COLUMNS = ["Geography (Original)", "Geography", "Median Household Income"]
COLUMN_MAP = {2001: [0, 3], 2006: [0, 2], 2016: [3, 12], 2021: [1, 8]}
ENCODINGS = {
    2001: 'iso-8859-1', 2006: 'iso-8859-1', 2016: 'utf8', 2021: 'utf8',
}
MATCH_THRESHOLD = 7


# %%
def main():
    source = os.path.join(SOURCE_DIR, 'data_final.xlsx')
    dest1 = os.path.join(DEST_DIR, 'income_dfs.pkl')
    dest2 = os.path.join(DEST_DIR, 'muni_map.pkl')
    os.makedirs(DEST_DIR, exist_ok=True)
    
    income_dfs = read_data()
    pickle.dump(income_dfs, open(dest1, "wb"))
    pickle.dump(map_munis(income_dfs, source), open(dest2, "wb"))


# %%
def read_data() -> dict[int, pl.DataFrame]:
    income_dfs = {}
    
    for year in YEARS:
        directory = os.path.join(WD, str(year))
        
        for file in os.listdir(directory):
            if file.endswith('.csv'):
                df = pl.read_csv(os.path.join(directory, file),
                                 encoding=ENCODINGS[year])
                
                if year == 2001:
                    df = (df.transpose(include_header=True)
                          .slice(1)
                          .with_columns(pl.nth(3).cast(pl.Int64)))
                elif year == 2016:
                    df = (df.filter(pl.nth(8).str.starts_with("Total") &
                                    pl.nth(12).str.contains(r'^[0-9]*$'))
                          .with_columns(pl.nth(12).cast(pl.Int64)))
                elif year == 2021:
                    df = df.filter(pl.nth(3).str.starts_with("Total") &
                                   pl.nth(4).str.starts_with("Total"))
                
                df = (df.select(pl.nth(COLUMN_MAP[year]))
                      .with_columns(pl.nth(0)
                                    .str.replace_all(r'\s+', ' ')
                                    .alias(COLUMNS[0]),
                                    
                                    pl.nth(1)
                                    .replace(0, None)
                                    .alias(COLUMNS[2]))
                      .with_columns(pl.col(COLUMNS[0])
                                    .str.replace(r'\s*\([0-9].*', '')
                                    .alias(COLUMNS[1]))
                      .select(COLUMNS)
                      .with_row_index())
                
                income_dfs[year] = df
    
    return income_dfs


# %%
def map_munis(
    income_dfs: dict[int, pl.DataFrame], source: str
) -> dict[int, dict[str, int]]:
    def process_muni(muni: str) -> str:
        muni_cmp = (unidecode(muni.lower())
                    .replace("baker brook", "baker-brook")
                    .replace("petit rocher", "petit-rocher"))
        muni_cmp = re.sub(r'^(saint|st).{0,1}(-|\s)', 'st-', muni_cmp)
        muni_cmp = re.sub(r'^(sainte|ste).{0,1}(-|\s)', 'st-', muni_cmp)
        k = min(MATCH_THRESHOLD, len(re.split(r',|\s', muni_cmp)[0]))
        return muni_cmp[:k]
    
    muni_map = {year: {} for year in YEARS}
    munis = sorted(pl.read_excel(source, columns=["Municipality"])
                   .to_series()
                   .unique())
    
    for muni in munis:
        muni_cmp = process_muni(muni)
        cands = {}
        sb = StringIO()
        sb.write(f"Choose mapping for {muni}:\n")
        
        for year, df in income_dfs.items():
            cands[year] = df.filter((pl.col(COLUMNS[1])
                                     .map_elements(process_muni, pl.Utf8)
                                     == muni_cmp) |
                                    (pl.col(COLUMNS[1]) == muni))
            sb.write(f"\n{year}:\n")
            
            for i, cand in enumerate(cands[year].iter_rows(), 1):
                sb.write(f"{i}.  {str(cand)}\n")
        
        print(sb.getvalue())
        tokens = input().split()
        
        for token, year in zip(tokens, YEARS):
            idx = int(token) - 1
            
            if idx >= 0:
                muni_map[year][muni] = (cands[year].select('index')
                                         .slice(idx, 1)
                                         .to_series())[0]
            else:
                muni_map[year][muni] = None
        
        print()
    
    return muni_map


# %%
if __name__ == '__main__':
    main()