"""Project settings: paths, study window, source series and sample rules.

The scripts read their years, thresholds and paths from here. The study is
built for one fixed data snapshot (retrieved 21 October 2026) and one fixed
window (2015-2024). The report text, chart scales and the reviewed-case
register in audit/ were written for that snapshot, so changing a value here
or analysing a new data vintage also requires reviewing those files.
"""

from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]

DATA_RAW = ROOT / "data" / "raw"            # the published snapshot: never overwritten
SNAPSHOTS = ROOT / "data" / "snapshots"     # new downloads go here, one folder per date
DATA_PROCESSED = ROOT / "data" / "processed"
SNAPSHOT_MANIFEST = ROOT / "data" / "snapshot_manifest.json"
DB_PATH = DATA_PROCESSED / "fiscal.sqlite"
PANEL_CSV = DATA_PROCESSED / "panel.csv"
SQL_DIR = ROOT / "sql"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
AUDIT = ROOT / "audit"
REVIEWED_CASES = AUDIT / "reviewed_cases.csv"
REPORT = ROOT / "report"
FONTS = ROOT / "assets" / "fonts"

REQUIRED_RAW_FILES = ["imf_datamapper.csv", "wb_wdi.csv", "wb_countries.csv", "retrieval_log.json"]

# Links in the PDF point to the public repository, not to local files.
REPO_URL = "https://github.com/saidjsidali/public-debt-interest-burden"
REPO_LINK_REF = "main"

# --- Study window -----------------------------------------------------------
# Years up to 2024 are treated as past data. The IMF may still use staff
# estimates for some of these years in some countries; the API does not say
# which. 2025 values are mostly estimates and 2026-27 are IMF projections.
# Projections are only shown as context.
START_YEAR = 2015
BREAK_YEAR = 2021  # last year before the 2022-23 rise in policy interest rates
END_YEAR = 2024
ESTIMATE_YEAR = 2025
FORECAST_END = 2027

# --- Sample rules -------------------------------------------------------------
# A country enters the sample if it has revenue, gross debt, primary balance
# and overall balance for every year START_YEAR..END_YEAR, and its net
# interest is not exactly zero in half or more of those years. Repeated
# exact zeros are a review flag: they may mean that interest is not recorded
# separately, but this has not been confirmed for every case.
MAX_ZERO_INTEREST_YEARS = 4
SMALL_STATE_POPULATION = 1.5e6  # World Bank's small-states cut-off, robustness only
HIGH_BURDEN_THRESHOLD = 20.0    # descriptive cut-off (one-fifth of revenue), not a risk threshold
NEAR_ZERO_BURDEN = 0.1          # % of revenue; positive values below this distort log regressions

# --- Sources ----------------------------------------------------------------
IMF_API = "https://www.imf.org/external/datamapper/api/v1"
WB_API = "https://api.worldbank.org/v2"
WB_FIRST_YEAR = 2010
WB_LAST_YEAR = 2025
IMF_FIRST_YEAR = 2010

# code -> (source, label, unit)
IMF_SERIES = {
    "GGR_G01_GDP_PT": ("IMF Fiscal Monitor", "General government revenue", "% of GDP"),
    "G_XWDG_G01_GDP_PT": ("IMF Fiscal Monitor", "General government gross debt", "% of GDP"),
    "GGXONLB_G01_GDP_PT": ("IMF Fiscal Monitor", "General government primary balance", "% of GDP"),
    "GGXCNL_G01_GDP_PT": ("IMF Fiscal Monitor", "General government overall balance", "% of GDP"),
    "NGDPD": ("IMF World Economic Outlook", "GDP, current prices", "US$ billions"),
    "ie": ("IMF Public Finances in Modern History", "Interest paid on public debt (gross)", "% of GDP"),
    "rev": ("IMF Public Finances in Modern History", "Government revenue", "% of GDP"),
}

WB_SERIES = {
    "GC.XPN.INTP.RV.ZS": ("World Bank WDI", "Interest payments, central government", "% of revenue"),
    "SH.XPD.GHED.GD.ZS": ("World Bank WDI", "Domestic general government health expenditure", "% of GDP"),
    "SE.XPD.TOTL.GD.ZS": ("World Bank WDI", "Government expenditure on education", "% of GDP"),
    "SP.POP.TOTL": ("World Bank WDI", "Population, total", "persons"),
}

# The IMF and the World Bank use different codes for two economies.
IMF_TO_WB_ISO = {"UVK": "XKX", "WBG": "PSE"}

INCOME_ORDER = ["High income", "Upper middle income", "Lower middle income", "Low income"]
