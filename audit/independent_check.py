"""Recompute headline numbers from the raw snapshot without the project's SQL or modules.

    python audit/independent_check.py

Reads only data/raw/*.csv and outputs/key_numbers.json, rebuilds the measure,
the sample and a set of headline results with pandas and numpy, and compares
them with the pipeline's numbers. A second implementation can catch errors
that the pipeline's own tests would miss.
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).absolute().parents[1]
RAW = ROOT / "data" / "raw"

imf = pd.read_csv(RAW / "imf_datamapper.csv", keep_default_na=False)
imf["iso3"] = imf["iso3"].replace({"UVK": "XKX", "WBG": "PSE"})
wb = pd.read_csv(RAW / "wb_wdi.csv", keep_default_na=False)
countries = pd.read_csv(RAW / "wb_countries.csv", keep_default_na=False).apply(lambda s: s.str.strip())
wide = (pd.concat([imf, wb]).pivot_table(index=["iso3", "year"], columns="series_code", values="value")
        .reset_index())
wide = wide[wide["iso3"].isin(countries["iso3"])].merge(countries, on="iso3")
wide["ni"] = wide["GGXONLB_G01_GDP_PT"] - wide["GGXCNL_G01_GDP_PT"]
wide["burden"] = 100 * wide["ni"] / wide["GGR_G01_GDP_PT"]
wide["gross"] = 100 * wide["ie"] / wide["rev"]

window = wide[wide["year"].between(2015, 2024)]
g = window.groupby("iso3")
complete = (g["GGR_G01_GDP_PT"].count() == 10) & (g["G_XWDG_G01_GDP_PT"].count() == 10) & (g["ni"].count() == 10)
zeros = g["ni"].apply(lambda s: (s.abs() < 1e-9).sum())
sample = complete[complete & (zeros <= 4)].index
p = wide[wide["iso3"].isin(sample)]
e = p[p["year"] == 2024].set_index("iso3")
s = p[p["year"] == 2015].set_index("iso3")
b = p[p["year"] == 2021].set_index("iso3")

checks = {}
checks["sample size"] = (len(sample), "sample/countries")
checks["median burden 2015"] = (s["burden"].median(), "median_burden/All countries/2015")
checks["median burden 2024"] = (e["burden"].median(), "median_burden/All countries/2024")
checks["low-income median 2024"] = (e.loc[e["income_group"] == "Low income", "burden"].median(),
                                     "median_burden/Low income/2024")
checks["high-income gross median 2024"] = (e.loc[e["income_group"] == "High income", "gross"].median(),
                                            "median_burden_gross/High income/2024")
d = e.dropna(subset=["NGDPD"])
checks["total net interest / total revenue 2024"] = (
    100 * (d["ni"] * d["NGDPD"]).sum() / (d["GGR_G01_GDP_PT"] * d["NGDPD"]).sum(), "pooled_burden/All countries/2024")
checks["countries above 20% in 2024"] = (int((e["burden"] > 20).sum()), "high_burden/countries/2024")
checks["countries with a higher burden in 2024 than 2015"] = (int((e["burden"] > s["burden"]).sum()),
                                                              "change/countries_up_start_end")
rank_debt, rank_burden = e["G_XWDG_G01_GDP_PT"].rank(), e["burden"].rank()
checks["Spearman debt-burden 2024"] = (np.corrcoef(rank_debt, rank_burden)[0, 1], "correlation/All countries/spearman")
md, mb = e["G_XWDG_G01_GDP_PT"].median(), e["burden"].median()
diff_class = int((((e["G_XWDG_G01_GDP_PT"] >= md) & (e["burden"] < mb))
                  | ((e["G_XWDG_G01_GDP_PT"] < md) & (e["burden"] >= mb))).sum())
checks["countries classified differently"] = (diff_class, "quadrants/different_classification")
covered = e[e["gross"].notna()]
checks["net median on FPP countries"] = (covered["burden"].median(), "matched/1/median_burden_end")
checks["gross median on FPP countries"] = (covered["gross"].median(), "matched/2/median_burden_end")

pos = e[e["ni"] > 0]
X = np.column_stack([np.ones(len(pos)), np.log(pos["G_XWDG_G01_GDP_PT"])])
y = np.log(pos["burden"])
resid = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
checks["R2 log burden on log debt"] = (1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum(),
                                       "regression/debt_only/r_squared")

both = b.join(e, lsuffix="0", rsuffix="1")[["burden0", "burden1", "ni0", "ni1", "GGR_G01_GDP_PT0", "GGR_G01_GDP_PT1"]].dropna()
both = both[(both["burden0"] > 0) & (both["burden1"] > 0)]
L = (both["burden1"] - both["burden0"]) / np.log(both["burden1"] / both["burden0"])
checks["2021-24 mean contribution of net interest/GDP"] = (
    (L * np.log(both["ni1"] / both["ni0"])).mean(), "decomposition_two/All countries/2021-2024/mean_net_interest_gdp_effect")
checks["2021-24 mean contribution of revenue/GDP"] = (
    (-L * np.log(both["GGR_G01_GDP_PT1"] / both["GGR_G01_GDP_PT0"])).mean(),
    "decomposition_two/All countries/2021-2024/mean_revenue_effect")

ind = wide[(wide["iso3"] == "IND") & (wide["year"] == 2023)].iloc[0]
checks["India 2023 net interest, % of GDP"] = (ind["ni"], "country/IND/interest_gdp_health_year")
checks["India 2023 health spending, % of GDP"] = (ind["SH.XPD.GHED.GD.ZS"], "country/IND/health_gdp")

key = json.loads((ROOT / "outputs" / "key_numbers.json").read_text(encoding="utf-8"))


def lookup(path):
    node = key
    for part in path.split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


failures = 0
print(f"{'Check':52} {'Independent':>12} {'Pipeline':>12}  Result")
for name, (value, path) in checks.items():
    other = lookup(path)
    ok = math.isclose(float(value), float(other), rel_tol=1e-9, abs_tol=1e-9)
    failures += not ok
    print(f"{name:52} {float(value):12.4f} {float(other):12.4f}  {'match' if ok else 'DIFFERENT'}")
print(f"\n{len(checks) - failures} of {len(checks)} headline numbers match.")
raise SystemExit(1 if failures else 0)
