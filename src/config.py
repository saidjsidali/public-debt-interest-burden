"""Project settings: paths, study window, source series and sample rules.

Everything that a reader might want to change to re-run the study under
different assumptions lives here, so the analysis scripts contain no
hard-coded years or file paths.
"""

from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DB_PATH = DATA_PROCESSED / "fiscal.sqlite"
PANEL_CSV = DATA_PROCESSED / "panel.csv"
SQL_DIR = ROOT / "sql"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
AUDIT = ROOT / "audit"
REPORT = ROOT / "report"
FONTS = ROOT / "assets" / "fonts"

# --- Study window -----------------------------------------------------------
# 2024 is the last year for which the October 2026 Fiscal Monitor reports
# outturns for most countries; 2025 values are still partly estimates and
# 2026-27 are IMF projections. Projections are only ever shown as context.
START_YEAR = 2015
BREAK_YEAR = 2021  # last year before the 2022-23 global tightening cycle
END_YEAR = 2024
ESTIMATE_YEAR = 2025
FORECAST_END = 2027

# --- Sample rules -------------------------------------------------------------
# A country enters the analysis sample if it has revenue, gross debt, primary
# balance and overall balance for every year START_YEAR..END_YEAR, and its net
# interest is not reported as exactly zero in half or more of those years
# (an exact zero means interest is not separately identified in the source).
MAX_ZERO_INTEREST_YEARS = 4
SMALL_STATE_POPULATION = 1.5e6  # World Bank's small-states cut-off, robustness only
HIGH_BURDEN_THRESHOLD = 20.0    # descriptive cut-off: one-fifth of revenue

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
