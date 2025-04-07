---
title: "Data Report"
author:
  - "Luis M. B. Varona[^1][^2]"
  - "Otoha Hanatani[^3]"
date: April 8, 2025
output: github_document
bibliography: references.bib
---
# Introduction

In collaboration with the Union of Municipalities of New Brunswick and Dr.
Craig Brett of Mount Allison University, we conduct a fixed-effects two-stage
least squares (or FE-2SLS) regression analysis of average tax rates on police
spending in New Brunswick municipalities, using median household income as an
instrumental variable to reduce simultaneity bias. We herein investigate
whether police spending is a significant predictor of municipal tax rates and,
if so, whether the specific policing provider plays into this correlation.
Moreover, we leverage the fact that police expenditure (as per the Provincial
Police Service Agreement with the Royal Canadian Mounted Police) is largely an
exogenous variable outside of municipal control to use this to approximate tax
base elasticity with respect to tax rates. In addition, we consider the
relationship between population and this estimated elasticity, observing that
smaller municipalities tend to exhibit higher tax base elasticity than larger
ones due to a variety of mobility factors.

(Note that this report is intended to be taken together with our
[GitHub project repository](https://github.com/Luis-Varona/umnb-tax-rates-police-spending),
with repeated references to specific scripts/file paths. However, it is
certainly possible to peruse this document independently, as we have made every
effort to ensure that all relevant information is encapsulated herein.)

## Background of the Problem

Price per unit of public goods&#x2014;particularly police spending, in the
context of this study&#x2014;varies widely across municipalities in New
Brunswick. We herein aim to regress regression municipal tax rates on the costs
of several different public goods. We place particular emphasis on the
significant variation in per capita cost of municipal bills under the
Provincial Police Service Agreement (PPSA)&#x2014;a contract between the
Government of New Brunswick (GNB) and the Royal Canadian Mounted Police (RCMP)
to provide smaller municipalities with policing services. As the RCMP provides
the province with a single combined bill, the GNB charges different
municipalities based on population, safety levels, and other factors, with this
formula acting as an exogenous factor in the cost of policing services.

On the other hand, it is common for larger municipalities have their own direct
contracts with the RCMP, further obscuring the relationship between municipal
spending patterns and taxation. For instance, the Codiac Regional Policing
Authority serves the municipalities of Dieppe, Moncton, and Riverview, none of
which pay additional fees to the GNB under the PPSA. Others still maintain
their own independent police forces like the Bathurst Police Force (although
there remains an RCMP presence in Bathurst). (As shall be revealed in our
section on Methodology, Amy Anderson of the Union of Municipalities of New
Brunswick has provided us with data on municipal policing providers as of 2024
and a way to map this backwards to jurisdictions from previous years.)

[TODO: Explain why this setup is of interest not only insofar as showing how,
and why, different level of exogeneity affect tax rates in different ways, but
also in terms of ... other stuff?]

We use a fixed-effects two-stage least squares (FE-2SLS) regression model to
investigate the relationships described above. The "fixed-effects" (FE) part of
this model allows us to control for time-invariant biases, controlling for
unobserved heterogeneity across municipalities. However, this fails to address
the problem of simultaneity bias arising from the bidirectional relationship
between average tax rate (our response variable) and tax base per capita (one
of our explanatory variables).

Hence, the "two-stage least squares" (2SLS) part of our model utilizes the fact
that median household income (our instrumental variable) is correlated with tax
base per capita but not with average tax rate. Regressing tax base on median
income and using our predicted values in the second-stage fixed-effects
regression allows us to isolate (to some extent) the effect of tax base on tax
rate from the effect of tax rate on tax base. Both aspects of our combined
FE-2SLS model are common approaches in econometrics, and we outline both more
thoroughly in the **Methodology** section.

# Literature Review

[TODO: Elaborate on this now that we have a first draft, especially with
regards to what methodology we took away]

We review two relevant articles on municipal taxation and
spending [@CP03; @Gad17]. @CP03 investigate the "determinants of municipal tax
rates in British Columbia," considering population, distance from major
metropolitan centers (namely Vancouver), income, and several other factors as
determinants of tax rates. They do not particularly emphasize spending patterns
as a potential factor in municipal taxation, but the methodology presented in
their paper will provide a useful framework on which to build for our project.

@Gad17 provides a study in how extra tax revenue truly affects the
quantity and quality of public services. Again, we are going the
"other way" in that we are examining how public spnding costs affect taxation,
but several of the case studies here are of interest. The relevant study also
investigates municipalities specifically, so the methodology laid out
(especially in Section B: Local Public Revenues) proves useful.

[TODO: Add lit. review for stuff like our elasticity estimates, median income
as an instrument for tax base/capita, etc. specifically]

[TODO: Moreover, and this is important&#x2014;add literature review on whether
or not police expenditure is typically this exogenous (it should not be), and
discuss further how the PPSA affects it. Maybe for the previous section too?]

[TODO: Add @CT08; @Dah24]

Finally, a review of previous studies of tax rate both as a response variable
[@Bue03, p. 116] and as an explanatory one [@Fer19, p. 8] reveals that the
inclusion of tax base on the other side of the equation is well-known to cause
simultaneity bias. While our other explanatory variables (expenditure, revenue,
etc.) are fairly *exogenous* in that they are determined outside of the model,
tax base per capita is an *endogenous* variable highly bicorrelated with (and
thus determined by) tax rate, which creates bias in regression estimates.
Findings from @AC99 [p. 689] indicate that household income is viable as an
instrument to reduce this bias, being correlated with tax base (as higher
income implies more taxable property) but not tax rate (as Canadian taxation
schemes tend not to be overly progressive). This supports the overall structure
of our FE-2SLS model described in the **Methodology** section below.

# Methodology

We now delineate our data collection process, data organization methods, and
econometric models. We use Python (namely the polars and
linearmodels/statsmodels ecosystems) to parse and clean data from Statistics
Canada and the Government of New Brunswick. Subsequently, we run several
fixed-effects and correlated random-effects regression models on the resulting
data in combination with median household income as an instrumental variable to
account for simultaneity bias.

## Data Collection and Sources

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
from previous years and integrate indicators into interaction terms in our
panel as described below.

Finally, the instrumental variable in the first stage of our 2SLS regression is
median household income, given in census data from Statistics Canada. Data is
only available from 2000 [@SC01], 2005 [@SC06], 2015 [@SC16], and 2020 [@SC21];
hence, linear interpolation is applied for the intervening years. The resulting
income data (typically correlated with tax base per capita but not with tax
rate) is then used to reduce simultaneity bias in our fixed-effects model.

## Data Cleaning and Organization

### Primary Data

Primary data is cleaned in the [`data_pipeline/`](../data_pipeline/) directory.
The original Excel files extracted from `.zip` archives provided by the GNB and
the UMNB are contained in the [`data_raw/`](../data_pipeline/data_raw/)
subdirectory. These contain annual data from 2000&#x2013;2022 on New Brunswick
municipalities, as well as 2024 data on municipal policing providers. Given
that some of these files are `.xls` and `.xlw` workbooks, we copy and convert
them all to `.xlsx` format in the [`data_xlsx/`](../data_pipeline/data_xlsx/)
subdirectory. The
[`helper_scripts/_1_raw_to_xlsx_.py`](../data_pipeline/helper_scripts/_1_raw_to_xlsx_.py)
script is used for this purpose.

Files in this [`data_xlsx/`](../data_pipeline/data_xlsx/) subdirectory are
cleaned and organized by
[`helper_scripts/_2_xlsx_to_clean_.py`](../data_pipeline/helper_scripts/_2_xlsx_to_clean_.py).
Finding that data from 2005 and 2019&#x2013;2022 is unusable due to
missing/improperly formatted tokens, our output (placed in the
[`data_clean/`](../data_pipeline/data_clean/) subdirectory) excludes these time
periods. No original data is discarded during this process (save for metadata
and notes)&#x2014;it is all simply reorganized into parseable form.

Addressing inconsistent municipality naming conventions across years/categories
and concatenating all annual panels within each category (budget expenditures,
budget revenues, comparative demographics, and tax bases), the
[`helper_scripts/_3_clean_to_final_.py`](../data_pipeline/helper_scripts/_3_clean_to_final_.py)
script then writes all four resulting worksheets&#x2014;plus a fifth for
provider data&#x2014;to a single
[`data_final/data_master.xlsx`](../data_pipeline/data_final/data_master.xlsx)
workbook. (The new municipal naming convention is also used to map provider
data on newer, reformed 2024 municipalities and districts to past jurisdictions
all the way back to 2000.)

All scripts are called and run by the main executable of the associated
directory, [`main.py`](../data_pipeline/main.py).

### Instrumental Variable Data

Data on the instrumental income data is stored and processed in the
[`data_iv/`](../data_iv/) directory. There is one folder each for 2001, 2006,
2016, and 2021 (the years in which the census data were released) containing
the original files downloaded from the Statistics Canada website. For 2016 and
2021, the downloads are straightforward, nicely formatted `.csv` files
requiring no further processing. For 2001 and 2006, however, full data is only
available in `.ivt` and `.xml` format; no schemas are available to parse the
XML data, so we use the Government of Canada's Beyond 20/20 Browser to extract
and download the data in `.csv` format. (Unfortunately, this process is not
easily documentable, as the browser requires manual processing.)

With CSV files for all four years, the
[`main.py`](../data_iv/main.py) executable script is finally used to clean and
combine the relevant columns and rows into a single polars DataFrame. This is
then saved as an `.xlsx` file in the [`results/`](../data_iv/results/)
subdirectory for immediate usage in the data analysis stage. (The
aforementioned data interpolation&#x2014;performed using Python's numpy
library&#x2014;is not applied until this stage and is thus not considered part
of the data cleaning and organization pipeline.)

It is worth noting that although household income data from Canada censuses is
publicly accessible for municipal-level geographic localities in 2000, 2005,
2015, and 2020, the only available source for 2010 is aggregated data from the
2011 National Household Survey. This survey refrained from providing
disaggregated data at lower levels of geography, so we are unable to map it to
most of the 104 municipalities in our dataset. Hence, linear interpolation is
used to estimate the missing data for 2010, just as for all the other missing
years. In the future, we may collaborate further with Statistics Canada to
obtain the geographically disaggregated data, if it remains in their records.

## Data Analysis and Modelling

All data analysis is performed in the [`data_analysis/`](../data_analysis/)
directory. Our included variables are:

- **Average Tax Rate**, or **AvgTaxRate** &#x2013; unitless
- **Police Spending per Capita**, or **PolExpCapita** &#x2013; $10^5$ CAD / person
- **Non-Police Spending per Capita**, or **OtherExpCapita** &#x2013; $10^5$ CAD / person
- **Non-Warrant Revenue per Capita**, or **OtherRevCapita** &#x2013; $10^5$ CAD / person
- **Tax Base for Rate per Capita**, or **TaxBaseCapita** &#x2013; $10^5$ CAD / person
- **Policing Provider** &#x2013; boolean, three categories:
  - *Provincial Police Service Agreement* (excluded control variable)
  - *Municipal Police Service Agreement*, or *Provider_MPSA* (included)
  - *Municipally Owned Police Force*, or *Provider_Muni* (included)
- **Median Household Income**, or **MedHouseInc** &#x2013; $10^5$ CAD / person

(These scaling factors are chosen to make our regression coefficients more
interpretable, but when visualizing our results in the form of plots, we switch
back to % for *AvgTaxRate* and CAD / person for the remaining expenditure and
revenue variables.)

Our response variable is *AvgTaxRate*, which is calculated as a weighted
average of the residential and non-residential tax rates in a municipal
jurisdiction. (That is&#x2014;as per government formulae, non-residential rates
are multiplied by a factor of $1.5$ before being integrated into the calculated
average. Said averages are already available in the raw data [@GNB00to18], not
calculated by us; we take note of the process simply to clarify the layout of
our data.) Our exogenous explanatory variables are *PolExpCapita*,
*OtherExpCapita*, *OtherRevCapita*, *PolExpCapita*&#x2217;*Provider_MPSA*, and
*PolExpCapita*&#x2217;*Provider_Muni*. Our sole endogenous explanatory variable
is *TaxBaseCapita*, for which we control simultaneity bias using *MedHouseInc*
as an instrumental variable.

Each of these variables is used throughout our FE-2SLS
regression model, carried out by the
[`helper_scripts/allow_concurrent/_fe_2sls_.py`](../data_analysis/helper_scripts/allow_concurrent/_fe_2sls_.py)
script. We have also included "vanilla" correlated random-effects (CRE) and
fixed-effects (FE) models, run by
[`helper_scripts/allow_concurrent/_cre_.py`](../data_analysis/helper_scripts/allow_concurrent/_cre_.py)
and
[`helper_scripts/allow_concurrent/_fe_.py`](../data_analysis/helper_scripts/allow_concurrent/_fe_.py),
to determine which variables are relevant and to demonstrate the need for an
instrumental variable. All helper scripts are called and run by the main
executable of the associated directory, [`main.py`](../data_analysis/main.py).

Our decision to integrate a panel data model with 2SLS, clearly, arose from the
factors described above in our **Literature Review**, as the inclusion of
*TaxBaseCapita* in the model creates simultaneity bias if unaddressed. Our
ultimate choice of FE over CRE for the base panel OLS was motivated by [TODO:
Elaborate]

It is worth noting that we chose not to use non-linear functional
forms&#x2014;with the most obvious candidate for a study in this particular
real-world context being log transformation&#x2014;as summary statistics
indicate that both the *AvgTaxRate* data and explanatory variables are fairly
normally distributed and do not exhibit significant skewness. (Although many
economic parameters such as income and GDP indeed exhibit right-skewed
distributions&#x2014;hence the popularity of the log transformation&#x2014;we
found that our particular variables of interest do not.)

Finally, we also estimate tax base elasticity by [TODO: Elaborate]

We now turn to describing our instrument-free CRE and FE analyses, then proceed
to more thoroughly delineate our final FE-2SLS regression model.

### Correlated Random-Effects (CRE)

[TODO: Elaborate]

### Fixed-Effects (FE)

After deeming the potential benefits of including the policing provider
indicators directly (not in interaction terms) insufficient to warrant [TODO:
Elaborate]

### Fixed-Effects Two-Stage Least Squares (FE-2SLS)

Finally, we decided on [TODO: Elaborate]

#### Stage 1

We begin by estimating *MedHouseInc* data for the years missing from the
Statistics Canada census data, which we do using simple linear interpolation.
(As this project continues to develop, we may investigate more sophisticated
approximation approaches, but this shall do for now.) After this is done, we
perform an ordinary least squares regression of *TaxBaseCapita* on
*MedHouseInc* to obtain

$$\begin{aligned}
TaxBaseCapita_{it} = \alpha_0 + \alpha_1MedHouseInc_{it} + v_{it}.
\end{aligned}$$

By performing this regression before proceeding to a fixed-effects model, we
manage to reduce simultaneity bias, as *MedHouseInc* is correlated with
*TaxBaseCapita* but not with *AvgTaxRate*. We use these predicted
$\widehat{TaxBaseCapita}_{it} = TaxBaseCapita_{it} - v_{it}$ values in the
second-stage regression, where we demean all variables over municipality.

#### Stage 2

Our primary fixed-effects regression model is now given by
$$\begin{aligned}
\ddot{AvgTaxRate}_{it} & = \beta_1\ddot{PolExpCapita}_{it} + \beta_2\ddot{OtherExpCapita} + \beta_3\ddot{OtherRevCapita} \\
& + \beta_4\ddot{\widehat{TaxBaseCapita}}_{it} + \beta_5\ddot{PolExpCapita}_{it} \mathord{*} Provider\_MPSA_{it} \\
& + \beta_6\ddot{PolExpCapita}_{it} \mathord{*} Provider\_Muni_{it} + \ddot{u}_{it},
\end{aligned}$$

where we use the notation $\ddot{X}_{it} \coloneqq X_{it} - \bar{X}_i$ to
denote the difference between the value of $X$ for municipality $i$ in year $t$
and the mean value of $X$ for municipality $i$ over all years. (Note that
$\ddot{\widehat{TaxBaseCapita}}_{it}$ is not the demeaning of $TaxBaseCapita_{it}$
itself but rather the demeaned prediction from our first-stage regression.)

Our covariance estimator in this model is clustered by municipality, as [TODO:
Elaborate]

## Tax Base Elasticity Estimates

Given these results, we now approximate tax base elasticity with respect to tax
rates by multiplying our obtained coefficient on **PolExpCapita**&#x2014;one of
the most exogenous expenditure categories, as previously discussed&#x2014;by
*TaxBaseCapita*. First, we set up the following notation:

- $E$ &nbsp;for government expenditure,
- $A$ &nbsp;for tax base assessed for rate,
- $t$&nbsp;&nbsp;&nbsp;&nbsp;for tax rate,
- $\beta \coloneqq \frac{\mathrm{d}t}{\mathrm{d}E}$&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for the effect of expenditure on tax rate, and
- $\eta \coloneqq \frac{t}{A}\frac{\mathrm{d}A}{\mathrm{d}t}$&nbsp;&nbsp;for tax base elasticity w.r.t. tax rate.

Given small deficits/surpluses, expenditure is approximately $E \approx tA$;
hence, assuming exogeneity of the expenditure variable so that $\beta$ is
(relatively) free of simultaneity bias, we obtain the following:

$$\begin{aligned}
\frac{\mathrm{d}E}{\mathrm{d}t} & \approx A + t\frac{\mathrm{d}A}{\mathrm{d}t} = A + A\eta = A(1 + \eta) \\
\mathrel{\therefore} 1 + \eta & \approx \frac{1}{A}\frac{\mathrm{d}E}{\mathrm{d}t} \\
\mathrel{\therefore} \frac{1}{1 + \eta} & \approx A\frac{\mathrm{d}t}{\mathrm{d}E} = A\beta \\
\mathrel{\therefore} \eta & \approx \frac{1}{A\beta} - 1
\end{aligned}$$

Clearly, the assumption of exogenous expenditure is vital to this calculus;
many types of expenditure are endogenously influenced by taxation, so the
(relative) exogeneity of police expenditure via the PPSA is a key factor in our
approximation. Using $\hat{\beta}$ to represent the coefficient on
*PolExpCapita* in our FE-2SLS regression model and $TBC$ as shorthand for
*TaxBaseCapita*, it therefore follows that for the $i^{th}$ municipality,

$$\begin{aligned}
A_i\beta \approx \overline{TBC}_{i} \cdot \hat{\beta},
\end{aligned}$$

since the per-capita transformations on tax base (averaged over time) and
police spending cancel out. Hence, we obtain the tax base elasticity estimate

$$\begin{aligned}
\hat{\eta}_i \coloneqq \frac{1}{\overline{TBC}_{i} \cdot \hat{\beta}} - 1,
\end{aligned}$$

where $\hat{\eta}_i$ the estimated tax base elasticity for municipality $i$
over the period 2000&#x2013;2018. [TODO: Add time effects here?]

# Results

[TODO: Elaborate]

## Correlated Random-Effects (CRE)

[TODO: Discuss CRE results]

## Fixed-Effects (FE)

[TODO: Discuss vanilla FE results]

## Fixed-Effects Two-Stage Least Squares (FE-2SLS)

We now turn to consideration of *MedHouseInc* as a potential instrumental
variable to address endogeneity of *TaxBaseCapita*. As seen in the **Appendix**
below, the first-stage OLS regression of *TaxBaseCapita* on *MedHouseInc*
yields the results
$$\begin{aligned}
TaxBaseCapita_{it} = \underset{(0.020)}{0.668} - \underset{(2.455)}{11.2497MedHouseInc_{it}} + v_{it}, \quad\quad R^2 = 0.011, \, F_{1,1816} = 20.99,
\end{aligned}$$

where the $F$-statistic of $20.99$ is far above the threshold of $10$ for
viable instruments. Therefore, we can safely integrate these results into the
second-stage fixed-effects regression, using the (demeaned) fitted values of
$\widehat{TaxBaseCapita}$ from this stage. (Note that the low $R^2$ of $0.011$
is irrelevant&#x2014;we are concerned primarily with the correlation between
the instrumental and endogenous variables, not with goodness-of-fit.)

Running a fixed-effects regression on the demeaned data and clustering by
municipality, we obtain the following results (with full computer output once
again available in the **Appendix**):
$$\begin{aligned}
\ddot{AvgTaxRate}_{it} & = \underset{(0.1371)}{0.5188\ddot{PolExpCapita}_{it}} + \underset{(0.0255)}{0.0301\ddot{OtherExpCapita}} + \underset{(0.0644)}{0.1025\ddot{OtherRevCapita}} \\
& + \underset{(0.0068)}{0.0225\ddot{\widehat{TaxBaseCapita}}_{it}} + \underset{(0.1941)}{0.0955\ddot{PolExpCapita}_{it} \mathord{*} Provider\_MPSA_{it}} \\
& - \underset{(0.1821)}{0.2542\ddot{PolExpCapita}_{it} \mathord{*} Provider\_Muni_{it}} + \ddot{u}_{it}, \quad\quad R^2 = 0.4290, \, F_{6,1708} = 27.629.
\end{aligned}$$

(Note that the $F$-statistic provided here is robust to clustering.) [TODO:
Elaborate further on this before providing visualization]

## Visualization

*[Figure 1 will appear here in the PDF.]*

<!-- ```{=latex}
\input{figure1.tex}
``` -->

[TODO: Add explanation of the above figure]

*[Figure 2 will appear here in the PDF.]*

<!-- ```{=latex}
\input{figure2.tex}
``` -->

[TODO: Add explanation of the above figure]

# Discussion

[TODO: Elaborate]

# Conclusion

[TODO: Elaborate]

# Appendix

We herein present raw computer output from our regression models. The first two
sections pertain to our vanilla CRE and FE models without an instrument, and
the last section presents the results of our final FE-2SLS model. (This data is
also available directly in both `.txt` and `.tex` format in the
[`data_analysis/`](../data_analysis/) directory of our GitHub repository.)

## Correlated Random-Effects (CRE)

[TODO: Add CRE output]

## Fixed-Effects (FE)

*[The fixed-effects regression results will appear here in the PDF.]*

<!-- ```{=latex}
\begingroup
\footnotesize
\input{../data_analysis/fe/summary.tex}
\endgroup
``` -->

## Fixed-Effects Two-Stage Least Squares (FE-2SLS)

### Stage 1

*[The stage 1 FE-2SLS regression results will appear here in the PDF.]*

<!-- ```{=latex}
\begingroup
\small
\input{../data_analysis/fe_2sls/stage1_summary.tex}
\endgroup
``` -->

### Stage 2

*[The stage 2 FE-2SLS regression results will appear here in the PDF.]*

<!-- ```{=latex}
\begingroup
\footnotesize
\input{../data_analysis/fe_2sls/stage2_summary.tex}
\endgroup
``` -->

[^1]: Department of Mathematics & Computer Science, Mount Allison University, Sackville, NB&nbsp;&nbsp;E4L 1E6
[^2]: Department of Politics & International Relations, Mount Allison University, Sackville, NB&nbsp;&nbsp;E4L 1A7
[^3]: Department of Economics, Mount Allison University, Sackville, NB&nbsp;&nbsp;E4L 1A7
