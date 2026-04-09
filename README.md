# 🛡️ NoVA Defense Contract Pulse

A lightweight intelligence dashboard surfacing DoD contract award activity across the Northern Virginia defense corridor — built to answer a simple question: **who is getting paid, how much, and where?**

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square)
![Data](https://img.shields.io/badge/Data-USASpending.gov-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)

---

## Why I Built This

I work at a private equity real estate firm focused on defense-sector office assets, where a dense cluster of cleared defense contractors occupy SCIF-capable buildings.

Understanding contract activity at the submarket level is directly relevant to real estate investment decisions: which tenants are growing, which agencies are awarding work in this corridor, and how obligation volume has trended over time. I built this tool to make that data fast to access without manually digging through USASpending.gov every time.

As a former Army EOD officer, I also understand firsthand what the data represents.

---

## What It Does

- **Top Contractors by Obligation** — ranks the 15 largest DoD contract recipients by place-of-performance county, filterable by fiscal year and awarding agency
- **Multi-Year Trend Chart** — FY2020–FY2024 obligation trend for the selected submarket
- **NAICS Sector Breakdown** — which industries (IT, engineering, R&D, logistics) are capturing defense spend in the area
- **KPI Cards** — total obligations, top contractor name, YoY change at a glance

---

## Submarkets Covered

| Submarket | County | FIPS |
|---|---|---|
| Westfields / Chantilly | Fairfax County | 059 |
| Dulles Corridor | Loudoun County | 107 |
| Manassas / Quantico Corridor | Prince William County | 153 |
| Rosslyn-Ballston | Arlington County | 013 |
| Old Town / Mark Center | Alexandria City | 510 |

---

## Data Source

All data is pulled live from the [USASpending.gov](https://usaspending.gov) public API — no API key required, no authentication, no cost.

- **Endpoint**: `POST /api/v2/search/spending_by_category/`
- **Award types**: Contracts only (type codes A, B, C, D)
- **Geography filter**: Place of performance by county FIPS code
- **Refresh**: Cached 1 hour per session

---

## Running Locally

```bash
git clone https://github.com/ALLGORM/NoVa-Defense-Pulse.git
cd nova-defense-pulse
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## Stack

- **Python 3.11+**
- **Streamlit** — UI framework
- **Plotly** — interactive charts
- **Pandas** — data handling
- **Requests** — API calls to USASpending.gov

---

## Background

I work at the intersection of private equity real estate and the defense contracting ecosystem. This tool is a stripped-down version of the contract intelligence layer I've been developing to inform acquisition decisions.

The core concept mirrors what Palantir Foundry does at enterprise scale: pipe messy government data through a structured interface so analysts can make faster, better-informed decisions. This is a 150-line version of that idea.

---

## Future Improvements

- [ ] Map view with county-level choropleth (Plotly Mapbox)
- [ ] SCIF-density overlay for specific zip codes
- [ ] Contractor-level drill-down (award history, agency mix)
- [ ] Export to CSV / PDF
- [ ] Cloud deployment
