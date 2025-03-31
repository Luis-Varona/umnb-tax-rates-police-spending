---
title: "Data Summary"
author:
  - "Luis M. B. Varona[^1][^2]"
  - "Otoha Hanatani[^3]"
date: March 4, 2025
output: github_document
bibliography: config_files/references.bib
---
This report provides a summary of the Government of New Brunswick [GNB] panel
data used in our correlated random-effects [CRE] regression analysis of
municipal tax rates on police spending. We present below our included
variables, preliminary summary statistics, and our data cleaning process.

## Variables of Interest

The response variable we aim to model is the **Average Tax Rate**, or **ATR**
(given in %), regressed on the following explanatory variables using correlated
random-effects:

- **Police Spending/Capita**, or **PSC** &#x2013; CAD/person
- **Tax Base for Rate/Capita**, or **TBC** &#x2013; CAD/person
- **Non-Police Expenditure/Capita**, or **NEC** &#x2013; CAD/person, disaggregated:
  - *General Government*, or *GGS*
  - *Fire Protection*, or *FPS*
  - *Water Cost Transfer*, or *WCT*
  - *Emergency Measures*, or *EMS*
  - *Other Protection*, or *OPS*
  - *Transportation*, or *TRS*
  - *Environmental Health*, or *EHS*
  - *Public Health*, or *PHS*
  - *Environmental Development*, or *EDS*
  - *Recreation & Cultural*, or *RCS*
  - *Debt Costs*, or *DBC*
  - *Transfers*, or *TRN*
  - *Deficits*, or *DFC*
- **Non-Warrant Revenue/Capita**, or **NRC** &#x2013; CAD/person, disaggregated:
  - *Unconditional Grant*, or *UGR*
  - *Services to Other Governments*, or *OGS*
  - *Sale of Services*, or *SOS*
  - *Own-Source Revenue*, or *OSR*
  - *Conditional Transfers*, or *CTR*
  - *Other Transfers*, or *OTR*
  - *Biennial Surplus*, or *BIS*
- **Population**, or **POP** &#x2013; persons (from the latest census data)
- **Policing Provider** &#x2013; boolean, three categories:
  - *Provincial Police Service Agreement*, or *PPSA* (control, excluded to avoid collinearity)
  - *Municipal Police Service Agreement*, or *MPSA* (included indicator)
  - *Municipal Police*, or *MPSA* (included indicator)

### Summary Statistics

Summary statistics of our panel data are included in the current directory at
[`data_summary_by_stat.xlsx`](data_summary_by_stat.xlsx) and
[`data_summary_by_year.xlsx`](data_summary_by_year.xlsx). The former workbook
contains one worksheet with all years for each summary statistic, whereas the
latter contains one worksheet with all summary statistics for each year. The
years covered are 2000&#x2013;2004 and 2006&#x2013;2018, and the summary
statistics provided are

- **Count** &#x2013; number of non-null observations in a column (by year)
- **Null Count** &#x2013; number of null observations in a column (by year)
- **Mean** &#x2013; mean of a column (by year)
- **Std. Dev.** &#x2013; standard deviation of a column (by year)
- **Minimum** &#x2013; minimum value of a column (by year)
- **25%** &#x2013; 1$^\text{st}$ quartile of a column (by year)
- **Median** &#x2013; median of a column (by year)
- **75%** &#x2013; 3$^\text{rd}$ quartile of a column (by year)
- **Maximum** &#x2013; maximum value of a column (by year)

## Data Pipeline

### Data Collection and Sources

We use an unbalanced panel of annual data from 2000&#x2013;2018 on New
Brunswick municipalities, received via personal correspondence with the GNB
and Dr. Craig Brett of Mount Allison University; however, this data is also
publicly available at [@GNB00to18], albeit in a less structured format.
(The year 2005 is excluded due to missing/improperly formatted tokens, but we
may coordinate further with the GNB to obtain this data in the future.) Each
set of annual data contains 95 to 103 municipalities, with a total of 104
unique municipalities across all years.

This is supplemented by 2024 data on municipal policing provider agreements
[@And25]. We map this data backwards to municipal jurisdictions and boundaries
from previous years and integrate indicators as time-constant variables into
our panel as described below.

### Data Cleaning and Organization

The original Excel files extracted from `.zip` archives provided by the GNB and
the UMNB are contained in the [`data_raw`](../data_pipeline/data_raw)
directory. These contain annual data from 2000&#x2013;2022 on New Brunswick
municipalities, as well as 2024 data on municipal policing providers. Given
that some of these files are `.xls` and `.xlw` workbooks, we copy and convert
them all to `.xlsx` format in the [`data_xlsx`](../data_pipeline/data_xlsx)
directory. The [`raw_to_xlsx.py`](../data_pipeline/raw_to_xlsx.py) script is
used for this purpose.

Files in [`data_xlsx`](../data_pipeline/data_xlsx) are then cleaned and
organized by [`xlsx_to_clean.py`](../data_pipeline/xlsx_to_clean.py) (and its
helper scripts in
[`helper_scripts/xlsx_to_clean`](../data_pipeline/helper_scripts/xlsx_to_clean)).
Finding that data from 2005 and 2019&#x2013;2022 is unusable due to
missing/improperly formatted tokens, our output (placed in the
[`data_clean`](../data_pipeline/data_clean) directory) excludes these time
periods. No data from the original files is discarded during this process (save
for metadata and notes)&#x2014;simply reorganized into parseable form.

Addressing inconsistent municipality naming conventions across years/categories
and concatenating all annual panels within each category (budget expenditures,
budget revenues, comparative demographics, and tax bases), the
[`clean_to_final.py`](../data_pipeline/clean_to_final.py) script then writes
all four resulting worksheets&#x2014;plus a fifth for provider data&#x2014;to a
single [`data_master.xlsx`](../data_pipeline/data_final/data_master.xlsx)
workbook in [`data_final`](../data_pipeline/data_final). (The new municipal
naming convention is also used to map provider data on newer, reformed 2024
municipalities and districts to past jurisdictions.)

The [`clean_to_final.py`](../data_pipeline/clean_to_final.py) script in
question (and its helpers in
[`helper_scripts/clean_to_final`](../data_pipeline/helper_scripts/clean_to_final))
also joins the five worksheets from
[`data_master.xlsx`](../data_pipeline/data_final/data_master.xlsx) into a
single worksheet in the
[`data_final.xlsx`](../data_pipeline/data_final/data_final.xlsx) workbook (in
the same directory). This process also involves computing new variables from
existing columns as needed (e.g., **Police Spending/Capita** from
**Police Spending** and **Population**). This final dataset is then used for
our CRE regression analysis, delineated in the following section. (It is also
used to obtain the summary statistics mentioned above.)

## CRE Model Specifications

We shall use a series of $F$-tests to compare a base (restricted) model with
aggregated *NEC* and *NRC* data to two partially restricted models and one
unrestricted model with disaggregated *NEC* and/or *NRC* data. Our decision to
use a CRE model rather than a fixed-effects (FE) one arises from the presence
of *MPSA* and *MUNI*&#x2014;the demeaning process in FE models fails to deal
with such time-constant variables, but this is not a problem in CRE models.

Additionally, we shall experiment with functional form on each of the proposals
presented below before deciding on our final model. Based on prior research
into tax rate regression analyses, a log transformation may prove prudent.

### Base (Restricted) Model

Our base (restricted) correlated random-effects model is as follows (for each
municipality $i$ and year $t$):

$$\begin{aligned}
ATR_{it} ={} & \beta_1PSC_{it} + \beta_2TBC_{it} + \beta_3NEC_{it} + \beta_4NRC_{it} + \beta_5POP_{it} +{} \\
& \beta_6MPSA_i + \beta_7MUNI_i + \alpha_i + u_{it},
\end{aligned}$$

where $\alpha_i$ denotes the municipality-specific effect and $u_{it}$ denotes
the error term.

### Partially Restricted Model (with NRC)
The first partially restricted model, which
disaggregates *NEC* but not *NRC*, is given by

$$\begin{aligned}
ATR_{it} ={} & \beta_1'PSC_{it} + \beta_2'TBC_{it} +{} \\
\bigl[& \beta_{3,1}'GGS_{it} + \beta_{3,2}'FPS_{it} + \beta_{3,3}'WCT_{it} + \beta_{3,4}'EMS_{it} + \beta_{3,5}'OPS_{it} +{} \\
& \beta_{3,6}'TRS_{it} + \beta_{3,7}'EHS_{it} + \beta_{3,8}'PHS_{it} + \beta_{3,9}'EDS_{it} +{} \\
& \beta_{3,10}'RCS_{it} + \beta_{3,11}'DBC_{it} + \beta_{3,12}'TRN_{it} + \beta_{3,13}'DFC_{it}\bigr] +{} \\
& \beta_4'NRC_{it} + \beta_5'POP_{it} + \beta_6'MPSA_i + \beta_7'MUNI_i + \alpha_i' + u_{it}'.
\end{aligned}$$

### Partially Restricted Model (with NEC)

The second partially restricted model, which disaggregates *NRC* but not *NEC*,
is given by

$$\begin{aligned}
ATR_{it} ={} & \beta_1''PSC_{it} + \beta_2''TBC_{it} + \beta_3''NEC_{it} +{} \\
\bigl[& \beta_{4,1}''UGR_{it} + \beta_{4,2}''OGS_{it} + \beta_{4,3}''SOS_{it} + \beta_{4,4}''OSR_{it} + \beta_{4,5}''CTR_{it} +{} \\
& \beta_{4,6}''OTR_{it} + \beta_{4,7}''BIS_{it}\bigr] +{} \\
& \beta_5''POP_{it} + \beta_6''MPSA_i + \beta_7''MUNI_i + \alpha_i'' + u_{it}''.
\end{aligned}$$

### Unrestricted Model

The fully unrestricted model, which disaggregates both *NEC* and *NRC*, is
given by

$$\begin{aligned}
ATR_{it} ={} & \beta_1'''PSC_{it} + \beta_2'''TBC_{it} +{} \\
\bigl[& \beta_{3,1}'''GGS_{it} + \beta_{3,2}'''FPS_{it} + \beta_{3,3}'''WCT_{it} + \beta_{3,4}'''EMS_{it} + \beta_{3,5}'''OPS_{it} +{} \\
& \beta_{3,6}'''TRS_{it} + \beta_{3,7}'''EHS_{it} + \beta_{3,8}'''PHS_{it} + \beta_{3,9}'''EDS_{it} +{} \\
& \beta_{3,10}'''RCS_{it} + \beta_{3,11}'''DBC_{it} + \beta_{3,12}'''TRN_{it} + \beta_{3,13}'''DFC_{it}\bigr] +{} \\
\bigl[& \beta_{4,1}'''UGR_{it} + \beta_{4,2}'''OGS_{it} + \beta_{4,3}'''SOS_{it} + \beta_{4,4}'''OSR_{it} + \beta_{4,5}'''CTR_{it} +{} \\
& \beta_{4,6}'''OTR_{it} + \beta_{4,7}'''BIS_{it}\bigr] +{} \\
& \beta_5'''POP_{it} + \beta_6'''MPSA_i + \beta_7'''MUNI_i + \alpha_i''' + u_{it}'''.
\end{aligned}$$

[^1]: Department of Mathematics & Computer Science, Mount Allison University, Sackville, NB E4L  1E6
[^2]: Department of Politics & International Relations, Mount Allison University, Sackville, NB E4L  1A7
[^3]: Department of Economics, Mount Allison University, Sackville, NB E4L  1A7

## References
