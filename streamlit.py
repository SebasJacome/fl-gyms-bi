import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

df_b = pd.read_parquet("./data/business.parquet")
db_r = pd.read_parquet("./data/review.parquet")
db_u = pd.read_parquet("./data/tip.parquet")

franchise_counts = df_b["name"].value_counts()
franchises = franchise_counts[franchise_counts >= 3].index.tolist()

selected_gym = st.selectbox("Choose a franchise", franchises)
franchise_locations = df_b[df_b["name"] == selected_gym]

fig = go.Figure()

fig.add_trace(go.Scattermapbox(
    lat = franchise_locations["latitude"],
    lon = franchise_locations["longitude"],
    mode = "markers",
    marker = dict(size = 12, color = franchise_locations["stars"], colorscale = "Viridis", showscale = True),
    text = franchise_locations["address"],
    hoverinfo = "text+lat+lon",
    name = selected_gym
))

fig.add_trace(go.Scattermapbox(
    lat = franchise_locations["latitude"],
    lon = franchise_locations["longitude"],
    mode = "lines",
    line = dict(width = 2, color = "blue"),
    name = "Connections"
))

fig.update_layout(
    mapbox = dict(
        style = "carto-positron",
        center = dict(lat = 27.994402, lon = -81.760254),
        zoom = 6
    ),
    margin = dict(r = 0, t = 30, l = 0, b = 0),
    title = f"Distribution of {selected_gym} Locations in Florida"
)

st.plotly_chart(fig, use_container_width = True)
