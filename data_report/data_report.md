---
title: "Data Report"
author:
  - "Luis M. B. Varona[^1][^2]"
  - "Otoha Hanatani[^3]"
date: April 16, 2025
output: github_document
bibliography: references.bib
---
# Introduction

In collaboration with the Union of Municipalities of New Brunswick and Dr. Craig
Brett of Mount Allison University, we conduct a fixed-effects two-stage least
squares (or FE-2SLS) regression analysis of average tax rates on police spending
in New Brunswick municipalities, using median household income as an
instrumental variable to reduce simultaneity bias. We herein investigate whether
police spending is a significant predictor of municipal tax rates and, if so,
how specific policing providers play into this correlation. Moreover, we
leverage the fact that police expenditure (as per the Provincial Police Service
Agreement [PPSA] with the Royal Canadian Mounted Police [RCMP]) is largely an
exogenous bill outside of municipal control to use this to approximate tax base
elasticity with respect to tax rates. In addition, we consider the relationship
between population and this estimated elasticity, observing that smaller
municipalities tend to exhibit higher tax base elasticity than larger ones due
to a variety of mobility factors.

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
PPSA&#x2014;a contract between the Government of New Brunswick [GNB] and the
RCMP to provide smaller municipalities with policing services. As the RCMP
provides the province with a single combined bill, the GNB charges different
municipalities based on population, safety levels, and other factors, with this
formula acting as an exogenous factor in the cost of policing services.

On the other hand, it is common for larger municipalities have their own direct
contracts with the RCMP, further obscuring the relationship between municipal
spending patterns and taxation. For instance, the Codiac Regional Policing
Authority serves the municipalities of Dieppe, Moncton, and Riverview, none of
which pay additional fees to the GNB under the PPSA. Others still maintain their
own independent police forces like the Bathurst Police Force (although there
remains a minor RCMP presence in Bathurst).

The Union of Municipalities of New Brunswick has provided us with data on
municipal policing providers as of 2024 to aid in our analysis. Confounding
this, however, is the 2023 New Brunswick local governance reform, which redrew a
large swath of municipal boundaries, partly driven by the desire to cut down on
"redundant" local service districts. Not only were several municipalities and
districts merged together, but in many cases, entirely new municipalities with
original names were created [@GNB24].

To make matters worse, although this was certainly the most significant reform
in New Brunswick municipal governance in decades, it was not the
first&#x2014;our panel data reveals municipal recombination on a smaller scale
transpired multiple times over the 2000&#x2013;2018 period as well. Regardless,
we have found a reliable way to map the 2024 data backwards to past municipal
jurisdictions (this is further described in the **Methodology** section),
allowing us to integrate time-invariant provider indicators into our model. In
future extensions of this project, we may utilize more recent data to study the
current policing system situation while collaborating with the UMNB.

Overall, this setup is of interest insofar that it allows us to study the
effects of different expenditure categories with different levels of exogeneity
on tax rate, as well as approximate tax base elasticity given the exogenous
nature of police spending under the PPSA. The coefficient on police spending per
capita shall reveal how much of a burden municipal residents bear as PPSA bills
increase, while our elasticity estimates may provide insight into the
revenue-raising capabilities of municipalities and justify policy changes to the
current policing system in New Brunswick.

As such, we herein construct a fixed-effects two-stage least squares (FE-2SLS)
regression model of the relationships described above. The *fixed-effects* (FE)
aspect allows us to address time-invariant biases, controlling for unobserved
heterogeneity across municipalities. However, this neglects the simultaneity
bias arising from the bidirectional relationship between average tax rate (our
response variable) and tax base per capita (one of our explanatory variables).

Hence, the *two-stage least squares* (2SLS) part of our model utilizes the fact
that median household income (our instrumental variable) is correlated with tax
base per capita but not with average tax rate. Regressing tax base on median
income and using our predicted values in the second-stage fixed-effects
regression allows us to isolate (to some extent) the effect of tax base on tax
rate from the effect of tax rate on tax base. Both aspects of our combined
FE-2SLS model are common approaches in econometrics, and we outline both more
thoroughly in the **Methodology** section.

# Literature Review

First off, @CP03 investigate the "determinants of municipal tax rates in British
Columbia," considering population, distance from major metropolitan centers
(namely Vancouver), income, and several other factors as determinants of tax
rates. They do not particularly emphasize spending patterns as a potential
factor in municipal taxation, but the methodology presented in their paper
provide a useful framework on which to build for our project.

In a similar vein, we consider studies of how increased provincial suppoort for
municipal budgets affected tax rates in New Brunswick. One of our more
surprising takeaways was the finding that, in a generalized method of moments
(GMM) three-stage least squares (3SLS) model with even more sophisticated
instrumentation than ours, the coefficient on tax base when predicting tax
rate was positive [@CT08, pp. 448--49]. This concurs with findings we shall
present in the **Results** section&#x2014;seemingly a weird counteintuitive
quirk of the NB economic system in particular. (Indeed, the methodology used in
@CT08 is quite similar to our own, with several refinements, and may inspire
improvements on our statistical models as this project continues to develop.)

We find also from @SSG12 [p. 29] that when tax rates change, individuals and
businesses often relocate when possible, in turn affecting the tax base. This
highlights the fact that the higher mobility associated with smaller localities
allows for greater elasticity of the tax base with respect to tax rates. Indeed,
this is a well-known phenomenon in the literature, proving key to our project's
hypothesis that smaller municipalities may show higher elasticity, preventing
local governments from raising tax rates to cover ever-growing PPSA bills
without the erosion of their tax base.

@Dah24 [p. 1] further supports this hypothesis, finding that&#x2014;particularly
in recent years&#x2014;climbing tax rates in Newfoundland and Labrador, Ontario,
and British Columbia have resulted in altered "volume and allocation of land,
labour, and capital in the economy, reducing our income and consumption
opportunities." This is a clear indication that tax hikes are not a sustainably
viable solution to covering rising municipal bills, as they oftentimes lead to
a significant loss of tax base. Our own findings in the **Results** and
**Discussion** sections below support the hypothesis that this applies in a New
runswick context as well, especially when it comes to smaller municipalities.

Finally, a review of previous studies of tax rate both as a response variable
[@Bue03, p. 116] and as an explanatory one [@Fer19, p. 8] reveals that the
inclusion of tax base on the other side of the equation is well-known to cause
simultaneity bias. While our other explanatory variables (expenditure, revenue,
etc.) are fairly *exogenous* in that they are determined outside of the model,
tax base per capita is an *endogenous* variable highly bicorrelated with (and
thus determined by) tax rate, which creates bias in regression estimates.
Findings from @AC99 [p. 689] indicate that household income is viable as an
instrument to reduce this bias, being correlated with tax base (since higher
income indirectly yields more taxable property) but not tax rate (since income
is not an *explicit* determinant of property base). This validates the overall
structure of our FE-2SLS model described in the **Methodology** section below.

# Methodology

We now delineate our data collection process, data organization methods, and
statistical models. We use Python&#x2014;namely the polars and linearmodels
ecosystems&#x2014;to parse and clean data from Statistics Canada and the GNB.
(We also use matplotlib and seaborn to visualize our results later on.)
Subsequently, we run several fixed-effects regressions on the resulting data in
combination with median household income as an instrumental variable to account
for simultaneity bias.

## Data Collection and Sources

We use an unbalanced panel of annual data from 2000&#x2013;2018 on New Brunswick
municipalities, received via personal correspondence with the GNB and Dr. Craig
Brett of Mount Allison University; however, this data is also publicly available
at [@GNB00to18], albeit in a less structured format. (The year 2005 is excluded
due to missing/improperly formatted tokens, but we may coordinate further with
the GNB to obtain this data in the future.) Each set of annual data contains 95
to 103 municipalities, with a total of 104 unique municipalities over all years.

This is supplemented by 2024 data on municipal policing provider agreements
[@And25]. We map this data backwards to municipal jurisdictions and boundaries
from previous years and integrate indicators into interaction terms in our panel
as described below.

Finally, the instrumental variable in the first stage of our 2SLS regression is
median household income, given in census data from Statistics Canada [StatsCan].
Data is only available from 2000 [@SC01], 2005 [@SC06], 2015 [@SC16], and 2020
[@SC21]; hence, linear interpolation is applied for the intervening years. The
resulting income data (typically correlated with tax base but not with tax rate)
is then used to reduce simultaneity bias in our fixed-effects model.

## Data Cleaning and Organization

### Primary Data

Primary data is cleaned in the [`data_pipeline/`](../data_pipeline/) directory.
The original Excel files extracted from `.zip` archives provided by the GNB and
the UMNB are contained in the [`data_raw/`](../data_pipeline/data_raw/)
subdirectory. These contain annual data from 2000&#x2013;2022 on New Brunswick
municipalities, as well as 2024 data on municipal policing providers. Given that
some of these files are `.xls` and `.xlw` workbooks, we copy and convert them
all to `.xlsx` format in the [`data_xlsx/`](../data_pipeline/data_xlsx/)
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
workbook. (The new municipal naming convention is also used to map provider data
on newer, reformed 2024 municipalities and districts to past jurisdictions all
the way back to 2000.)

All scripts are called and run by the main executable of the associated
directory, [`main.py`](../data_pipeline/main.py).

### Instrumental Variable Data

Data on the instrumental income data is stored and processed in the
[`data_iv/`](../data_iv/) directory. There is one folder each for 2001, 2006,
2016, and 2021 (the years in which the census data were released) containing the
original files downloaded from the StatsCan website. For 2016 and 2021, the
downloads are straightforward, nicely formatted `.csv` files requiring no
further processing. For 2001 and 2006, however, full data is only available in
`.ivt` and `.xml` format; no schemas are available to parse the XML data, so we
use the Government of Canada's Beyond 20/20 Browser to extract and download the
data in `.csv` format. (Unfortunately, this process is not easily documentable,
as the browser requires manual processing.)

With CSV files for all four years, the [`main.py`](../data_iv/main.py)
executable script is finally used to clean and combine the relevant columns and
rows into a single polars DataFrame. This is then saved as an `.xlsx` file in
the [`results/`](../data_iv/results/) subdirectory for immediate usage in the
data analysis stage. (The aforementioned data interpolation&#x2014;performed
using Python's numpy library&#x2014;is not applied until this stage and is thus
not considered part of the data cleaning and organization pipeline.)

It is worth noting that although household income data from Canada censuses is
publicly accessible for municipal-level geographic localities in 2000, 2005,
2015, and 2020, the only available source for 2010 is aggregated data from the
2011 National Household Survey. This survey refrained from providing
disaggregated data at lower levels of geography, so we are unable to map it to
most of the 104 municipalities in our dataset. Hence, linear interpolation is
used to estimate the missing data for 2010, just as for all the other missing
years. In the future, we may collaborate further with StatsCan to obtain the
geographically disaggregated data, if it remains in their records.

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

Our response variable is *AvgTaxRate*, which is calculated as a weighted average
of the residential and non-residential tax rates in a municipal jurisdiction.
(That is&#x2014;as per government formulae, non-residential rates are multiplied
by a factor of $1.5$ before being integrated into the calculated average. Said
averages are already available in the raw data [@GNB00to18], not calculated by
us; we take note of the process simply to clarify the layout of our data.) Our
exogenous explanatory variables are *PolExpCapita*, *OtherExpCapita*,
*OtherRevCapita*, *PolExpCapita*&#x2217;*Provider_MPSA*, and
*PolExpCapita*&#x2217;*Provider_Muni*. Our sole endogenous explanatory variable
is *TaxBaseCapita*, for which we control simultaneity bias using *MedHouseInc*
as an instrumental variable.

Each of these variables is used throughout our FE-2SLS regression model, carried
out by the
[`helper_scripts/allow_concurrent/_fe_2sls_.py`](../data_analysis/helper_scripts/allow_concurrent/_fe_2sls_.py)
script. We have also included our "vanilla" fixed-effects (FE) model, run by
[`helper_scripts/allow_concurrent/_fe_.py`](../data_analysis/helper_scripts/allow_concurrent/_fe_.py),
to determine which variables are relevant and to demonstrate the need for an
instrumental variable. In each model, we opt to cluster our covariance estimator
by municipality&#x2014;a common approach to account for unobserved heterogeneity
in panel data. All helper scripts are called and run by the main executable of
the associated directory, [`main.py`](../data_analysis/main.py).

Our decision to integrate a panel data model with 2SLS, clearly, arose from the
factors described above in our **Literature Review**, as the inclusion of
*TaxBaseCapita* in the model creates simultaneity bias if unaddressed. The
construction of a vanilla FE model was never intended as a viable alternative to
our main FE-2SLS model, but rather to act as a baseline for comparison, examing
how the integration of an instrument affects our results.

It is also worth noting that we chose not to use non-linear functional
forms&#x2014;with the most obvious candidate for a study in this particular
real-world context being log transformation&#x2014;as summary statistics
indicate that both the *AvgTaxRate* data and explanatory variables are fairly
normally distributed and do not exhibit significant skewness. (Although many
economic parameters such as income and GDP indeed exhibit right-skewed
distributions&#x2014;hence the popularity of the log transformation&#x2014;we
find that our particular variables of interest do not.)

Finally, we also approximate tax base elasticity by multiplying the coefficient
on *PolExpCapita* by the average *TaxBaseCapita* for each municipality,
subsequently performing some basic algebraic manipulations. This allows us to
obtain a rough estimate of how sensitive taxable income and property in a
municipality is to tax hikes given increases in PPSA bils, providing key insight
into potential policy changes to the current New Brunswick policing system.

We now turn to describing our instrument-free FE analysis, then proceed to more
thoroughly delineate our final FE-2SLS regression model.

<!-- ### Correlated Random-Effects (CRE)

$$\begin{aligned}
AvgTaxRate_{it} & = \beta_0 + \beta_1PolExpCapita_{it} + \beta_2OtherExpCapita_{it} + \beta_3OtherRevCapita_{it} \\
& \phantom{+} + \beta_4TaxBaseCapita_{it} + \beta_5PolExpCapita_{it} \mathord{*} Provider\_MPSA_{it} \\
& \phantom{+} + \beta_6PolExpCapita_{it} \mathord{*} Provider\_Muni_{it} \\
& + \gamma_1Provider\_MPSA_{it} + \gamma_2Provider\_Muni_{it} \\
& + \delta_1\overline{PolExpCapita}_i + \delta_2\overline{OtherExpCapita}_i + \delta_3\overline{OtherRevCapita}_i \\
& \phantom{+} + \delta_4\overline{TaxBaseCapita}_i + \delta_5\overline{PolExpCapita}_i \mathord{*} Provider\_MPSA_{it} \\
& \phantom{+} + \delta_6\overline{PolExpCapita}_i \mathord{*} Provider\_Muni_{it} + \underbrace{\ \ \varepsilon_{it}\ \ }_{\alpha_i + u_{it}}.
\end{aligned}$$

Here the $\beta$ coefficients's are associated with our time-variant variables,
the $\gamma$'s are associated with our time-invariant variables, and the
$\delta$'s are associated with the means (taken for each municipality over time)
of our time-variant variables. The $\alpha_i$'s are the unobserved individual
effects associated with each municipality (independent of time), and the
$u_{it}$'s are the usual error terms; we sum these to create the combined
$\varepsilon_{it}$ terms, which include both unobserved heterogeneity and
idiosyncratic errors. -->

### Fixed-Effects (FE)

Our fixed-effects model is given by

$$\begin{aligned}
\ddot{AvgTaxRate}_{it} & = \beta_1\ddot{PolExpCapita}_{it} + \beta_2\ddot{OtherExpCapita} + \beta_3\ddot{OtherRevCapita} \\
& \phantom{+} + \beta_4\ddot{TaxBaseCapita}_{it} + \beta_5\ddot{PolExpCapita}_{it} \mathord{*} Provider\_MPSA_{it} \\
& \phantom{+} + \beta_6\ddot{PolExpCapita}_{it} \mathord{*} Provider\_Muni_{it} + \ddot{u}_{it}.
\end{aligned}$$

This is not meant to be a viable alternative to our FE-2SLS model, but rather
serves to demonstrate the need for an instrumental variable and determine how it
affects our coefficients.

### Fixed-Effects Two-Stage Least Squares (FE-2SLS)

Here we present the setup of our main FE-2SLS model.

#### Stage 1

We begin by estimating *MedHouseInc* data for the years missing from the
StatsCan census data, which we do using simple linear interpolation. (As this
project continues to develop, we may investigate more sophisticated
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
& \phantom{+} + \beta_4\ddot{\widehat{TaxBaseCapita}}_{it} + \beta_5\ddot{PolExpCapita}_{it} \mathord{*} Provider\_MPSA_{it} \\
& \phantom{+} + \beta_6\ddot{PolExpCapita}_{it} \mathord{*} Provider\_Muni_{it} + \ddot{u}_{it},
\end{aligned}$$

where we use the notation $\ddot{X}_{it} \coloneqq X_{it} - \bar{X}_i$ to denote
the difference between the value of $X$ for municipality $i$ in year $t$ and the
mean value of $X$ for municipality $i$ over all years. (Note that
$\ddot{\widehat{TaxBaseCapita}}_{it}$ is not the demeaning of
$TaxBaseCapita_{it}$ itself but rather the demeaned prediction from our
first-stage regression.)

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

Clearly, the assumption of exogenous expenditure is vital to this calculus; many
types of expenditure are endogenously influenced by taxation, so the (relative)
exogeneity of police expenditure via the PPSA is a key factor in our
approximation. Using $\hat{\beta}$ to represent the coefficient on
*PolExpCapita* in our FE-2SLS regression model and $TBC$ as shorthand for
*TaxBaseCapita*, it therefore follows that for the $i^{th}$ municipality,

$$\begin{aligned}
A_i\beta \approx \overline{TBC}_{i} \cdot \hat{\beta},
\end{aligned}$$

since the per-capita transformations on tax base (averaged over time) and police
spending cancel out. Hence, we obtain the tax base elasticity estimate

$$\begin{aligned}
\hat{\eta}_i \coloneqq \frac{1}{\overline{TBC}_{i} \cdot \hat{\beta}} - 1,
\end{aligned}$$

where $\hat{\eta}_i$ the estimated tax base elasticity for municipality $i$ over
the period 2000&#x2013;2018. Once finally calculated, this estimate serves as a
decent (if rough) approximation of how sensitive the tax base is to changes in
tax rate, given the exogenous nature of police expenditure in NB municipalities
covered by the PPSA. In the future, we may also experiment with estimating the
tax base elasticity by

$$\begin{aligned}
\tilde{\eta}_i \coloneqq \widehat{\frac{1}{TBC_{i} \cdot \hat{\beta}}} - 1
\end{aligned}$$

(taking the mean after the algebraic manipulation), but for now, the data
visualization in the **Discussion** section is derived solely from our
$\hat{\eta}$ estimator.

# Results

We herein present the numerical results of our statistical models. A more
thorough discussion of the real-world implications of these findings is provided
in the **Discussion** section, and raw computer output from Python's
linearmodels library is available in the **Appendix**.

<!-- ## Correlated Random-Effects (CRE)

Our CRE model yielded the following results: -->

## Fixed-Effects (FE)

Our instrument-free FE model yielded the following results:

$$\begin{aligned}
\ddot{AvgTaxRate}_{it} & = \underset{(0.0990)}{1.3092\ddot{PolExpCapita}_{it}} + \underset{(0.0914)}{0.9665\ddot{OtherExpCapita}} - \underset{(0.0991)}{0.8964\ddot{OtherRevCapita}} \\
& \phantom{+} - \underset{(0.0012)}{0.0122\ddot{TaxBaseCapita}_{it}} - \underset{(0.1951)}{0.5551\ddot{PolExpCapita}_{it} \mathord{*} Provider\_MPSA_{it}} \\
& \phantom{+} - \underset{(0.1377)}{0.6083\ddot{PolExpCapita}_{it} \mathord{*} Provider\_Muni_{it}} + \ddot{u}_{it}, \quad R^2 = 0.7216, \, F_{6,1708} = 66.473.
\end{aligned}$$

(Note that the $F$-statistic reported here is robust to clustering.) On their
own, these numbers are not particularly insightful&#x2014;they simply serve as a
baseline to which we can compare our FE-2SLS results, investigating how (the
lack of) instrumentation affects our coefficients.

## Fixed-Effects Two-Stage Least Squares (FE-2SLS)

We now turn to consideration of *MedHouseInc* as a potential instrumental
variable to address endogeneity of *TaxBaseCapita* before re-running our
fixed-effects regression.

### Stage 1

As seen in the **Appendix** below, a first-stage OLS regression of
*TaxBaseCapita* on *MedHouseInc* produced the regression results
$$\begin{aligned}
TaxBaseCapita_{it} = \underset{(0.0194)}{0.6668} - \underset{(2.4347)}{11.250MedHouseInc_{it}} + v_{it}, \quad R^2 = 0.0114, \, F_{1,1816} = 21.350,
\end{aligned}$$

where the $F$-statistic of $21.350$ is far above the threshold of $10$ for
viable instruments. (Our standard errors here are adjusted by the Huber&#x2013;White sandwich estimator to account for heteroscedasticity, as samples of higher-income municipalities may tend to
exhibit greater variance due to factors like a wider range of income levels,
property values, industry types, etc. Either way, this does not affect our stage
2 regression, as the coefficients themselves remain unchanged.) Therefore, we can
safely integrate these results into the second-stage fixed-effects regression,
using the (demeaned) fitted values of $\widehat{TaxBaseCapita}$ from this stage.
(Note that the low $R^2$ of $0.0114$ is irrelevant&#x2014;we are concerned,
first and foremost, with the strength of the correlation between the instrument
and the endogenous variable, not with the overall fit of the model.)

### Stage 2

Running a fixed-effects regression on the demeaned data and clustering by
municipality, we obtain the following results (with full computer output once
again available in the **Appendix**):
$$\begin{aligned}
\ddot{AvgTaxRate}_{it} & = \underset{(0.1371)}{0.5188\ddot{PolExpCapita}_{it}} + \underset{(0.0255)}{0.0301\ddot{OtherExpCapita}} + \underset{(0.0644)}{0.1025\ddot{OtherRevCapita}} \\
& \phantom{+} + \underset{(0.0068)}{0.0225\ddot{\widehat{TaxBaseCapita}}_{it}} + \underset{(0.1941)}{0.0955\ddot{PolExpCapita}_{it} \mathord{*} Provider\_MPSA_{it}} \\
& \phantom{+} - \underset{(0.1821)}{0.2542\ddot{PolExpCapita}_{it} \mathord{*} Provider\_Muni_{it}} + \ddot{u}_{it}, \quad R^2 = 0.4290, \, F_{6,1708} = 27.629.
\end{aligned}$$

(Again, the $F$-statistic here is robust to clustering.) As expected, our
coefficient on *PolExpCapita* goes down&#x2014;considering our first-stage
regression, as the error term predicting *TaxBaseCapita* experiences unexpected
increases, police spending rises, and so does tax rate. Controlling for these
short-term fluctuations in tax base washes out this effect, reducing our
coefficient on *PolExpCapita* (but still leaving it significant). We also note
that other types of expenditure and revenue no longer appear significant in
this model.

Another thing to note is that the coefficient on *TaxBaseCapita*is now positive,
which is unexpected in a general context even with instrumentation, given that
more taxable property typically implies lower tax rates. As we found in our
**Literature Review**, however, there is precedent for this finding in @CT08,
who conclude that it is likely just a quirk of the New Brunswick economy.

In the following section, we proffer a more thorough discussion of our results
and their real-world implications.

## Tax Base Elasticity Estimates

We visualize our results on tax base elasticity in the following **Discussion**.

# Discussion

We now tackle the real-world implications of our findings, beginning with the
results of our primary FE-2SLS regression model. Disaggregating by policing
provider (PPSA, MPSA, or municipal force), we adjust the data for our control
variables (i.e., subtract the predicted effect of our control variables from
each data point) to obtain the following figure:

*[Figure 1 will appear here in the PDF.]*

<!-- ```{=latex}
\begin{figure}[H]
    \centering
    \includegraphics[width=6in]{../data_visualization/fe_2sls.png}
    \\[-0.5cm]
    \caption{Lines of best fit from our FE-2SLS regression model, disaggregated
    by policing provider.}
\end{figure}
``` -->

We see here that municipalities with a municipal police force (green line) tend
to have a much lower *PolExpCapita* coefficient than those with PPSA/MPSA
contracts, as is expected given the lower levels of exogeneity (of police
expenditure) associated with these government units. We now consider what
holding *PolExpCapita* constant at levels from the year 2000 would look like:

*[Figure 2 will appear here in the PDF.]*

<!-- ```{=latex}
\begin{figure}[H]
    \centering
    \includegraphics[width=6in]{../data_visualization/alt_tax_rates.png}
    \\[-0.5cm]
    \caption{Counterfactual predictions of tax rates, holding police spending
    constant at 2000 levels.}
\end{figure}
``` -->

Using our FE-2SLS model, we can see that if police spending were held constant
at 2000 levels, the average tax rate would be approximately $0.075$% lower than
it is in actuality, leading homeowners of $200,000$ houses to pay CAD150 less
each year. This is quite a bit more than the approximate CAD105 increase in
police expenditure per capita over the years, indicating that the burden has
shifted from the government to the taxpayer. Certainly, rising police
expenditure in recent years was unavoidable&#x2014;especially given certain
strikes and instability in the RCMP as of late&#x2014;but provincial bailouts
and other equalization measures could have been used to offset this
disproportionate burden. Now, we consider some implications of higher asset
mobility in smaller municipalities:

*[Figure 3 will appear here in the PDF.]*

<!-- ```{=latex}
\begin{figure}[H]
    \centering
    \includegraphics[width=6in]{../data_visualization/elasticity.png}
    \\[-0.5cm]
    \caption{Tax base elasticity estimates. Smaller municipalities tend to
    exhibit higher asset mobility.}
\end{figure}
``` -->

It is clear here that smaller municipalities tend to exhibit higher tax base
elasticity with respect to rate, due to a number of factors (most prominently
higher asset mobility and less need for further infrastructure and development).
This indicates that smaller municipalities&#x2014;also more likely to be covered
by the PPSA rather than form direct contracts with the RCMP (through the MPSA)
or maintain their own municipal forces&#x2014;have less revenue-raising power.
As tax rates inevitably rise in response to increasing police expenditure, tax
base will fall, resulting in a catch-22. This is one of the key findings of our
report, giving rise to several potential policy proposals and changes.

# Conclusion

In this report, we have demonstrated that police spending under the PPSA
significantly affects municipal tax rates in New Brunswick in such a way that
limits municipalities' revenue-raising power and places an undue burden on
taxpayers. By exploiting the exogeneity of PPSA bills and employing a FE-2SLS
framework, we isolated the causal impact of *PolExpCapita* on *AvgTaxRate*, also
accounting for simultaneity bias through median household income as an
instrument variable. Our estimates reveal that a CAD100 increase in police
expenditure per capita raises the average tax rate by approximately 0.53%.

Our tax base elasticity estimates indicate that smaller
municipalities&#x2014;which are typically those relying on PPSA
coverage&#x2014;are subject to higher elasticity, implying greater sensitivity
of their tax base to rate adjustments. This dynamic generates a public policy
conundrum&#x2014;as smaller jurisdictions bear are subject to rising PPSA bills
(especially in recent years) they are also more prone to base erosion,
undermining fiscal independence. This is, of course, a clear indication that
provincial funding formulas and policing governance structures need to be
reassessed&#x2014;one alternative is a flat surtax decided on by Fredericton on
all municipalities covered by the PPSA, which would give rise to less asset
mobility between municipalities as rates rise.

Looking forward, several avenues warrant further exploration. We plan to replace
our fixed-effects models with correlated random-effects (CRE) instead, allowing
us to account for time-invariant unobserved heterogeneity (that is, the policing
provider themselves isolated from interaction with expenditure). (Indeed, we
have already included some preliminary results from such models in the
**Appendix**.) Alternative elasticity estimation methods, such as a different
order of demeaning and a direct regression, also merit consideration. Finally,
we intend to refine our instrumentation approach from a two-stage system to a
three-stage one, resulting in a CRE-3SLS model more sophisticated than our
current analysis.

<!-- ```{=latex}
\newpage
``` -->

# Appendix

We herein present raw computer output from our CRE, CRE-2SLS, FE, and FE-2SLS
regression models. (The original `.tex` output files are available in the
[`data_analysis/`](../data_analysis/) directory of our GitHub repository.) Do
note that the CRE and CRE-2SLS models are not mentioned in the current report,
as we have decided to focus on the FE-2SLS model for the time being. However,
we ultimately plan to switch to a CRE-3SLS (correlated random-effects in
combination with three-stage least squares) model in the future, with the CRE
and CRE-2SLS results presented below serving as a stepping stone to that goal.

## Correlated Random-Effects (CRE)

*[The correlated random-effects results will appear here in the PDF.]*

<!-- ```{=latex}
\begingroup
\scriptsize
\input{../data_analysis/cre/summary.tex}
\endgroup
``` -->

## Correlated Random-Effects Two-Stage Least Squares (CRE-2SLS)

### Stage 1

*[The stage 1 CRE-2SLS regression results will appear here in the PDF.]*

<!-- ```{=latex}
\begingroup
\small
\input{../data_analysis/cre_2sls/stage1_summary.tex}
\endgroup
``` -->

### Stage 2

*[The stage 2 CRE-2SLS regression results will appear here in the PDF.]*

<!-- ```{=latex}
\begingroup
\scriptsize
\input{../data_analysis/cre_2sls/stage2_summary.tex}
\endgroup
``` -->

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

The stage 1 FE-2SLS regression results are identical to those of the CRE-2SLS
model, as the first stage is the same in both cases. As such, we refrain from
repeating them here.

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
