# ⚡ Streamlit Dashboard v5 — Performance & Scale

This version of the dashboard demonstrates **scalable data exploration** in Python with **Streamlit** and **DuckDB**.  
It is designed to handle **large datasets (millions of rows)** while staying responsive.

---

## 🚀 Features
- **Offline-safe demo data**  
  Uses Plotly’s built-in Gapminder dataset, scaled up to **1M+ rows** with jitter for realism.
- **File upload support**  
  Upload your own **CSV** or **Parquet** file, processed server-side in DuckDB.
- **Server-side filtering & pagination**  
  No need to load everything into memory—DuckDB executes efficient SQL queries on demand.
- **Performance caching**  
  Streamlit’s `@st.cache_data` ensures queries and uploads don’t rerun unnecessarily.
- **WebGL plotting**  
  Large scatterplots are smooth with Plotly’s `render_mode="webgl"`.
- **Virtualized tables**  
  Supports [AgGrid](https://github.com/PablocFonseca/streamlit-aggrid) for fast scrolling, with a fallback to `st.dataframe`.
- **Download support**  
  Export the currently visible page of data as CSV.

---

## 📦 Requirements
Install dependencies:

```bash
pip install streamlit plotly duckdb pyarrow streamlit-aggrid pandas
