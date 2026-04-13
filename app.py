import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="NoVA Defense Contract Pulse",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    .metric-card { background: #0d1117; border: 1px solid #21262d; border-radius: 6px; padding: 1rem 1.2rem; margin-bottom: 0.5rem; min-height: 90px; display: flex; flex-direction: column; justify-content: center; }
    .metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.4rem; font-weight: 600; color: #58a6ff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .metric-label { font-size: 0.7rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
    .submarket-tag { display: inline-block; background: #161b22; border: 1px solid #30363d; border-radius: 3px; padding: 2px 8px; font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #79c0ff; margin: 2px; }
    h1 { font-family: 'IBM Plex Mono', monospace !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="collapsedControl"] {display: block !important; visibility: visible !important;}
</style>
""", unsafe_allow_html=True)

NOVA_COUNTIES = {
    "Fairfax County (Westfields / Chantilly)": "059",
    "Loudoun County (Dulles Corridor)": "107",
    "Prince William County": "153",
    "Arlington County": "013",
    "Alexandria City": "510",
}

DEFENSE_AGENCIES = {
    "All DoD": None,
    "Department of the Air Force": "057",
    "Department of the Army": "021",
    "Department of the Navy": "017",
    "Defense Intelligence Agency": "089",
    "National Geospatial-Intelligence Agency": "507",
}

FISCAL_YEARS = list(range(2024, 2019, -1))
BASE_URL = "https://api.usaspending.gov/api/v2"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_top_contractors(county_fips, fiscal_year, agency_id):
    filters = {
        "time_period": [{"start_date": f"{fiscal_year - 1}-10-01", "end_date": f"{fiscal_year}-09-30"}],
        "award_type_codes": ["A", "B", "C", "D"],
        "place_of_performance_locations": [{"country": "USA", "state": "VA", "county": county_fips}],
    }
    if agency_id:
        filters["agencies"] = [{"type": "awarding", "tier": "toptier", "toptier_code": agency_id}]
    payload = {"filters": filters, "limit": 15, "page": 1}
    try:
        r = requests.post(f"{BASE_URL}/search/spending_by_category/recipient_duns/", json=payload, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return pd.DataFrame()
        df = pd.DataFrame(results)
        df = df.rename(columns={"name": "Contractor", "amount": "Obligations ($)"})
        df["Obligations ($)"] = df["Obligations ($)"].round(0).astype(int)
        df["Rank"] = range(1, len(df) + 1)
        return df[["Rank", "Contractor", "Obligations ($)"]].head(15)
    except Exception as e:
        st.error(f"API error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_award_trend(county_fips, agency_id):
    rows = []
    for fy in range(2020, 2025):
        filters = {
            "time_period": [{"start_date": f"{fy - 1}-10-01", "end_date": f"{fy}-09-30"}],
            "award_type_codes": ["A", "B", "C", "D"],
            "place_of_performance_locations": [{"country": "USA", "state": "VA", "county": county_fips}],
        }
        if agency_id:
            filters["agencies"] = [{"type": "awarding", "tier": "toptier", "toptier_code": agency_id}]
        payload = {"filters": filters, "limit": 50, "page": 1}
        try:
            r = requests.post(f"{BASE_URL}/search/spending_by_category/recipient_duns/", json=payload, timeout=15)
            r.raise_for_status()
            results = r.json().get("results", [])
            total = sum(x.get("amount", 0) for x in results)
            rows.append({"FY": f"FY{fy}", "Obligations ($B)": round(total / 1e9, 2)})
        except Exception:
            rows.append({"FY": f"FY{fy}", "Obligations ($B)": 0})
    return pd.DataFrame(rows)

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_naics_breakdown(county_fips, fiscal_year, agency_id):
    filters = {
        "time_period": [{"start_date": f"{fiscal_year - 1}-10-01", "end_date": f"{fiscal_year}-09-30"}],
        "award_type_codes": ["A", "B", "C", "D"],
        "place_of_performance_locations": [{"country": "USA", "state": "VA", "county": county_fips}],
    }
    if agency_id:
        filters["agencies"] = [{"type": "awarding", "tier": "toptier", "toptier_code": agency_id}]
    payload = {"filters": filters, "limit": 8, "page": 1}
    try:
        r = requests.post(f"{BASE_URL}/search/spending_by_category/naics/", json=payload, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return pd.DataFrame()
        df = pd.DataFrame(results)
        df = df.rename(columns={"name": "NAICS Sector", "amount": "Obligations ($)"})
        df["Obligations ($)"] = df["Obligations ($)"].round(0).astype(int)
        return df[["NAICS Sector", "Obligations ($)"]].head(8)
    except Exception:
        return pd.DataFrame()

# ── Sidebar
with st.sidebar:
    st.markdown("### 🛡️ **NoVA Defense Pulse**")
    st.markdown("<span class='submarket-tag'>WESTFIELDS</span> <span class='submarket-tag'>ROUTE 28</span> <span class='submarket-tag'>CHANTILLY</span>", unsafe_allow_html=True)
    st.markdown("---")
    county_label = st.selectbox("Submarket / County", list(NOVA_COUNTIES.keys()), index=0)
    county_fips = NOVA_COUNTIES[county_label]
    agency_label = st.selectbox("Awarding Agency", list(DEFENSE_AGENCIES.keys()), index=0)
    agency_id = DEFENSE_AGENCIES[agency_label]
    fiscal_year = st.selectbox("Fiscal Year", FISCAL_YEARS, index=0)
    st.markdown("---")
    st.markdown("<div style='font-size:0.72rem; color:#484f58; line-height:1.6;'>Data via <b>USASpending.gov</b> public API.<br>Contracts only (award types A–D).<br>Place of performance = county FIPS.</div>", unsafe_allow_html=True)

# ── Header
st.markdown("# NoVA Defense Contract Pulse")
st.markdown(f"**{county_label}** · **{agency_label}** · **FY{fiscal_year}**")
st.markdown("Real-time DoD contract intelligence for the Northern Virginia defense corridor.")
st.markdown("---")

# ── Fetch
with st.spinner("Pulling data from USASpending.gov..."):
    df_contractors = fetch_top_contractors(county_fips, fiscal_year, agency_id)
    df_trend = fetch_award_trend(county_fips, agency_id)
    df_naics = fetch_naics_breakdown(county_fips, fiscal_year, agency_id)

# ── KPIs
col1, col2, col3, col4 = st.columns(4)
if not df_contractors.empty:
    total_obligations = df_contractors["Obligations ($)"].sum()
    top_contractor = df_contractors.iloc[0]["Contractor"]
    num_contractors = len(df_contractors)
    trend_delta = ""
    if len(df_trend) >= 2:
        latest = df_trend.iloc[-1]["Obligations ($B)"]
        prior = df_trend.iloc[-2]["Obligations ($B)"]
        if prior > 0:
            pct = ((latest - prior) / prior) * 100
            trend_delta = f"{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}% YoY"
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Top-15 Obligations (FY{fiscal_year})</div><div class='metric-value'>${total_obligations/1e9:.2f}B</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Top Contractor</div><div class='metric-value'>{top_contractor[:22]}{'…' if len(top_contractor)>22 else ''}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Contractors Ranked</div><div class='metric-value'>{num_contractors}</div></div>", unsafe_allow_html=True)
    with col4:
        color = "#3fb950" if "▲" in trend_delta else "#f85149"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>YoY Trend (top-50)</div><div class='metric-value' style='color:{color}'>{trend_delta or '—'}</div></div>", unsafe_allow_html=True)
else:
    st.warning("No contract data returned for this filter. Try broadening your selection.")

st.markdown("")

# ── Row 1: Bar chart + Trend line
st.markdown("#### Top Contractors by DoD Obligation")
if not df_contractors.empty:
    fig = px.bar(
        df_contractors.head(10), x="Obligations ($)", y="Contractor", orientation="h",
        color="Obligations ($)", color_continuous_scale=["#1f2937", "#1d4ed8", "#58a6ff"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#c9d1d9",
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#21262d", tickformat="$,.0f"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", autorange="reversed", tickfont=dict(size=11)),
        margin=dict(l=0, r=10, t=10, b=30), height=400,
    )
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("View raw table"):
        st.dataframe(df_contractors.style.format({"Obligations ($)": "${:,.0f}"}), use_container_width=True, hide_index=True)
else:
    st.info("No contractor data available.")

st.markdown("")

# ── Row 2: Trend + NAICS side by side
col_trend, col_naics = st.columns(2)

with col_trend:
    st.markdown("#### Multi-Year Obligation Trend")
    if not df_trend.empty and df_trend["Obligations ($B)"].sum() > 0:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_trend["FY"], y=df_trend["Obligations ($B)"], mode="lines+markers",
            line=dict(color="#58a6ff", width=2.5), marker=dict(size=7, color="#58a6ff"),
            fill="tozeroy", fillcolor="rgba(88,166,255,0.08)",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#c9d1d9",
            xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d", tickprefix="$", ticksuffix="B"),
            margin=dict(l=0, r=10, t=10, b=10), height=360, showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Trend data unavailable.")

with col_naics:
    st.markdown("#### Top NAICS Sectors")
    if not df_naics.empty:
        fig3 = px.pie(
            df_naics, names="NAICS Sector", values="Obligations ($)", hole=0.55,
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#c9d1d9",
            legend=dict(font=dict(size=8), orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5),
            margin=dict(l=0, r=0, t=10, b=80), height=360, showlegend=True,
        )
        fig3.update_traces(textinfo="none")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("NAICS data unavailable.")

st.markdown("---")
st.markdown("<div style='font-size:0.72rem; color:#484f58; text-align:center;'>Data sourced from <a href='https://usaspending.gov' style='color:#58a6ff;'>USASpending.gov</a> public API · Contracts only (PSC A–D) · Refreshes hourly · Not affiliated with any federal agency</div>", unsafe_allow_html=True)
