import streamlit as st
import pandas as pd
from pages.graphs import build_franchise_graphs, load_datasets

st.set_page_config(layout="wide")
st.title("🏋️ Florida Gyms Franchise Analysis")

df_b, _, _ = load_datasets()

franchise_counts = df_b["name"].value_counts()
franchises = franchise_counts[franchise_counts >= 3].index.tolist()

selected_gym = st.selectbox("Choose a franchise", franchises)

graphs = build_franchise_graphs(selected_gym)

st.plotly_chart(graphs["locations_map"], use_container_width=True)
st.plotly_chart(graphs["scale_vs_quality"], use_container_width=True)
st.plotly_chart(graphs["average_star"], use_container_width=True)
st.plotly_chart(graphs["ratings_over_time"], use_container_width=True)
st.plotly_chart(graphs["feature_profile"], use_container_width=True)
