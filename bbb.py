import streamlit as st
import pandas as pd
import plotly.express as px

# Load sample data
df = px.data.gapminder()

# Sidebar filter
year = st.sidebar.slider('piuck a year', 1952, 2007, step = 5)
# Filtered data
df_year = df[df["year"] == year]

# Title
st.title("Life Expectancy vs GDP per Capita")

# Chart
fig = px.scatter(df_year, x="gdpPercap", y="lifeExp",
                 size="pop", color="continent",
                 hover_name="country", log_x=True)
st.plotly_chart(fig)
