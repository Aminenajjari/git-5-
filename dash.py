# app.py — v3
import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Page setup ----
st.set_page_config(page_title="Gapminder Explorer v3", page_icon="📊", layout="wide")
st.title("📊 Gapminder Explorer — v3")

# ---- Data (cached) ----
@st.cache_data
def load_data():
    return px.data.gapminder()

df = load_data()

# ---- Sidebar filters ----
st.sidebar.header("Filters")

# Year slider
year = st.sidebar.slider(
    "Year",
    int(df["year"].min()),
    int(df["year"].max()),
    value=2007,
    step=5
)

# Filter by year first
df_year = df[df["year"] == year]

# Continent multiselect
all_conts = sorted(df_year["continent"].unique().tolist())
continents = st.sidebar.multiselect(
    "Continent(s)",
    options=all_conts,
    default=all_conts
)
df_year = df_year[df_year["continent"].isin(continents)]

# Country multiselect (depends on chosen continents)
all_countries = sorted(df_year["country"].unique().tolist())
countries = st.sidebar.multiselect(
    "Country(ies)",
    options=all_countries,
    default=all_countries
)

# Final filtered frame
df_filt = df_year[df_year["country"].isin(countries)]

# ---- KPIs ----
k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Countries", df_filt["country"].nunique())
with k2:
    st.metric("Median life expectancy", f"{df_filt['lifeExp'].median():.1f} yrs")
with k3:
    st.metric("Total population", f"{int(df_filt['pop'].sum()):,}")

st.divider()

# ---- Tabs: Chart / Table ----
tab_chart, tab_table = st.tabs(["📈 Chart", "📋 Table"])

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
