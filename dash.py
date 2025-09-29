import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gapminder Explorer", page_icon="📈", layout="wide")

@st.cache_data
def load_data():
    return px.data.gapminder()

df = load_data()

st.title("📈 Gapminder Explorer")

# ===== Sidebar filters =====
year = st.sidebar.slider("Year", int(df.year.min()), int(df.year.max()), 2007, step=5)

all_conts = sorted(df["continent"].unique())
continents = st.sidebar.multiselect("Continent(s)", all_conts, default=all_conts)

df_year = df.query("year == @year and continent in @continents")

# Country filter depends on continent choice
all_countries = sorted(df_year["country"].unique())
countries = st.sidebar.multiselect("Country(ies)", all_countries, default=all_countries)

df_filt = df_year.query("country in @countries")

# ===== KPIs =====
left, mid, right = st.columns(3)
with left:
    st.metric("Countries", df_filt["country"].nunique())
with mid:
    st.metric("Median life expectancy", f"{df_filt['lifeExp'].median():.1f} yrs")
with right:
    st.metric("Total population", f"{int(df_filt['pop'].sum()):,}")

# ===== Tabs: Chart / Table =====
tab_chart, tab_table = st.tabs(["Chart", "Table"])

with tab_chart:
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
        height=420,
    )
    st.download_button(
        "Download filtered data (CSV)",
        df_filt.to_csv(index=False).encode("utf-8"),
        file_name=f"gapminder_{year}.csv",
        mime="text/csv",
    )
