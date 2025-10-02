# app.py — v4 (advanced)
# Features:
# - Caching with TTL
# - URL query params (share/shareable state)
# - Session-state "Saved Views"
# - Extra range filters (GDP per capita, Life Expectancy)
# - KPIs computed via cached helpers
# - Compare-over-time chart for selected countries
# - Graceful empty-state handling

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- Page setup ----------------
st.set_page_config(page_title="Gapminder Explorer v4", page_icon="🧭", layout="wide")
st.title("🧭 Gapminder Explorer — v4 (advanced)")

# ---------------- Data (cached) ----------------
@st.cache_data(ttl=600)  # refresh if 10 minutes old
def load_data():
    return px.data.gapminder()

df = load_data()

# ---------- Helpers: query params <-> state ----------
def read_query_params():
    """Read URL query params into a dict of simple Python types/lists."""
    try:
        qp = st.query_params  # Streamlit >= 1.32
    except Exception:
        # Fallback for older versions
        qp = st.experimental_get_query_params()
    # Normalize scalars/lists and types
    result = {}
    def _get_list(key):
        v = qp.get(key, [])
        if isinstance(v, list):
            return v
        return [v]
    # Year
    if "year" in qp:
        try:
            result["year"] = int(qp.get("year", 2007))
        except Exception:
            pass
    # Continents
    if "continents" in qp:
        result["continents"] = _get_list("continents")
    # Countries
    if "countries" in qp:
        result["countries"] = _get_list("countries")
    # Ranges
    if "gdp_min" in qp: result["gdp_min"] = float(qp.get("gdp_min"))
    if "gdp_max" in qp: result["gdp_max"] = float(qp.get("gdp_max"))
    if "lex_min" in qp: result["lex_min"] = float(qp.get("lex_min"))
    if "lex_max" in qp: result["lex_max"] = float(qp.get("lex_max"))
    return result

def write_query_params(**kwargs):
    """Push current filters to the URL."""
    # Filter out None
    clean = {k:v for k,v in kwargs.items() if v is not None}
    # Flatten lists are fine; Streamlit will serialize
    try:
        st.query_params.update(clean)  # Streamlit >= 1.32
    except Exception:
        st.experimental_set_query_params(**clean)

# ---------------- Defaults from data ----------------
year_min, year_max = int(df["year"].min()), int(df["year"].max())
gdp_min, gdp_max = float(df["gdpPercap"].min()), float(df["gdpPercap"].max())
lex_min, lex_max = float(df["lifeExp"].min()), float(df["lifeExp"].max())
all_conts_all = sorted(df["continent"].unique().tolist())

# ---------------- Initialize session state ----------------
if "saved_views" not in st.session_state:
    st.session_state.saved_views = {}  # name -> dict(filters)

# Preload from URL (once)
if "hydrated_from_url" not in st.session_state:
    qp = read_query_params()
    st.session_state.hydrated_from_url = True
else:
    qp = {}

# ---------------- Sidebar: Filters & Saved Views ----------------
st.sidebar.header("Filters")

# Year
year_init = qp.get("year", 2007)
year = st.sidebar.slider("Year", year_min, year_max, value=year_init, step=5)

# Continents
conts_init = qp.get("continents", all_conts_all)
all_conts_year = sorted(df.query("year == @year")["continent"].unique().tolist())
# Keep only valid ones for this year
conts_init = [c for c in conts_init if c in all_conts_year] or all_conts_year
continents = st.sidebar.multiselect("Continent(s)", options=all_conts_year, default=conts_init)

# Year + continent subset
df_year = df.query("year == @year and continent in @continents")

# Countries (dependent)
countries_all = sorted(df_year["country"].unique().tolist())
countries_init = qp.get("countries", countries_all)
countries_init = [c for c in countries_init if c in countries_all] or countries_all
countries = st.sidebar.multiselect("Country(ies)", options=countries_all, default=countries_init)

# Extra range filters
st.sidebar.subheader("Advanced filters")
gdp_range = st.sidebar.slider(
    "GDP per capita (log-scale on chart, filter is linear)",
    min_value=round(gdp_min, 2),
    max_value=round(gdp_max, 2),
    value=(
        float(qp.get("gdp_min", max(gdp_min, 500.0))),
        float(qp.get("gdp_max", min(gdp_max, 60000.0)))
    )
)
lex_range = st.sidebar.slider(
    "Life expectancy (years)",
    min_value=round(lex_min, 1),
    max_value=round(lex_max, 1),
    value=(
        float(qp.get("lex_min", 40.0)),
        float(qp.get("lex_max", 85.0))
    )
)

# Apply filters
df_filt = df_year[
    (df_year["country"].isin(countries)) &
    (df_year["gdpPercap"].between(gdp_range[0], gdp_range[1])) &
    (df_year["lifeExp"].between(lex_range[0], lex_range[1]))
]

# Sync URL with current filters (on every run keeps link shareable)
write_query_params(
    year=year,
    continents=continents,
    countries=countries,
    gdp_min=f"{gdp_range[0]:.2f}",
    gdp_max=f"{gdp_range[1]:.2f}",
    lex_min=f"{lex_range[0]:.1f}",
    lex_max=f"{lex_range[1]:.1f}",
)

# ---------------- Saved Views ----------------
st.sidebar.subheader("Saved views")
new_name = st.sidebar.text_input("Name this view", placeholder="e.g., Asia-TopGDP-2007")
col_sv1, col_sv2 = st.sidebar.columns([1,1])
with col_sv1:
    if st.button("Save current"):
        if new_name.strip():
            st.session_state.saved_views[new_name.strip()] = dict(
                year=year, continents=continents, countries=countries,
                gdp_min=gdp_range[0], gdp_max=gdp_range[1],
                lex_min=lex_range[0], lex_max=lex_range[1],
            )
            st.success(f"Saved view: {new_name.strip()}")
        else:
            st.warning("Please enter a name before saving.")
with col_sv2:
    # Load a saved view
    if st.session_state.saved_views:
        to_load = st.selectbox("Load view", ["— select —"] + list(st.session_state.saved_views.keys()))
        if st.button("Load") and to_load != "— select —":
            v = st.session_state.saved_views[to_load]
            # Soft load via URL for simplicity
            write_query_params(
                year=v["year"],
                continents=v["continents"],
                countries=v["countries"],
                gdp_min=f"{v['gdp_min']:.2f}",
                gdp_max=f"{v['gdp_max']:.2f}",
                lex_min=f"{v['lex_min']:.1f}",
                lex_max=f"{v['lex_max']:.1f}",
            )
            st.rerun()

# ---------------- KPIs (cached computations) ----------------
@st.cache_data(show_spinner=False)
def compute_kpis(frame: pd.DataFrame):
    if frame.empty:
        return 0, float("nan"), 0
    return (
        frame["country"].nunique(),
        float(frame["lifeExp"].median()),
        int(frame["pop"].sum()),
    )

k_countries, k_med_life, k_total_pop = compute_kpis(df_filt)

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Countries", k_countries)
with k2:
    st.metric("Median life expectancy", f"{k_med_life:.1f} yrs" if k_countries else "—")
with k3:
    st.metric("Total population", f"{k_total_pop:,}" if k_countries else "—")

st.divider()

# ---------------- Tabs ----------------
tab_chart, tab_table, tab_compare = st.tabs(["📈 Chart", "📋 Table", "🕘 Compare over time"])

with tab_chart:
    if df_filt.empty:
        st.info("No data for the current filter selection.")
    else:
        fig = px.scatter(
            df_filt,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x=True,
            height=520
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_table:
    st.dataframe(
        df_filt.sort_values(["continent", "country"]),
        use_container_width=True,
        height=420
    )
    st.download_button(
        "Download filtered data (CSV)",
        df_filt.to_csv(index=False).encode("utf-8"),
        file_name=f"gapminder_{year}.csv",
        mime="text/csv",
    )

