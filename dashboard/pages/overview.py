import streamlit as st
from streamlit_folium import st_folium
import folium
from pages.graphs import build_graphs

st.set_page_config(layout="wide")
st.header("📊 Overview")

graphs = build_graphs()

def style_plotly(fig, bgcolor="#262730", font_color="white"):
    fig.update_layout(
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        font_color=font_color,
        title_font_color=font_color,
        legend_font_color=font_color,
        xaxis=dict(
            color=font_color,
            gridcolor="#444444"  # optional, dark grid lines
        ),
        yaxis=dict(
            color=font_color,
            gridcolor="#444444"
        )
    )
    return fig

def show_graphs(graphs):
    for i, fig in enumerate(graphs):

        col1, col2 = st.columns(2, gap="large")

        target_col = col1 if i % 2 == 0 else col2

        with target_col:
            if isinstance(fig, folium.Map):
                st_folium(fig, width=700, height=500)
            else:
                st.plotly_chart(style_plotly(fig), use_container_width=True, key=f"plotly_{i}")

show_graphs(graphs)
            
