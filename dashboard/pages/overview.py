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
            gridcolor="#444444"
        ),
        yaxis=dict(
            color=font_color,
            gridcolor="#444444"
        )
    )
    return fig

# def show_graphs(graphs):
#     folium_names = ["📍 Gym Locations in Florida by Star Rating", "⭐️ Clustered Gym Locations by Reviews and Ratings",
#                     "🔥 Heatmap of Gym Density in Florida", "💬 Distribution of Reviews Across Gyms"]
#     folium_maps = [g for g in graphs if isinstance(g, folium.Map)]
#     for i, m in enumerate(folium_maps):
#         st.subheader(folium_names[i])
#         st_folium(m, width=None, height=600, use_container_width=True, key=f"map_{i}")
#         st.markdown("---")
#     plotly_charts = [g for g in graphs if not isinstance(g, folium.Map)]
#     col1, col2 = st.columns(2)
#     for i, chart in enumerate(plotly_charts):
#         chart = style_plotly(chart)
#         target_col = col1 if i % 2 == 0 else col2
#         with target_col:
#             st.plotly_chart(chart, use_container_width=True, key=f"plot_{i}")

def show_graphs(graphs):
    folium_names = [
        "📍 Gym Locations in Florida by Star Rating",
        "⭐️ Clustered Gym Locations by Reviews and Ratings",
        "🔥 Heatmap of Gym Density in Florida",
        "🗺️ Gym Locations in Florida by Number of Reviews"
    ]
    folium_maps = [g for g in graphs if isinstance(g, folium.Map)]
    for i, m in enumerate(folium_maps):
        st.subheader(folium_names[i])
        st_folium(m, width=None, height=600, use_container_width=True, key=f"map_{i}")
        st.markdown("---")

    plotly_charts = [g for g in graphs if not isinstance(g, folium.Map)]

    chart_texts = [
        "Gyms with mid-range ratings (2.5–3 stars) have the widest variation in review counts, while 5-star gyms tend to have fewer reviews overall, with only a few highly popular outliers.",
        "Most gyms have ratings above 3 stars, with 5-star ratings being the most common.",
        "",
        "Credit card payments and bike parking are the most common features among gyms.", 
        "Gyms open earlier and close later on weekdays, with reduced hours on weekends.",
        "Most gyms operate between 70–100 hours weekly, regardless of their rating.",
        "Reviews are mostly polarized, with many 1-star and 5-star ratings.",
        "Star ratings are slightly negatively correlated with review usefulness, while engagement metrics (useful, funny, cool) are strongly related to each other.",
        "Tips peaked around 2012 when Yelp went public, then declined sharply after COVID-19 began.",
        "Average ratings stayed stable for years but dropped slightly after 2020.",
        "Gyms allowing dogs or requiring appointments tend to have the highest ratings.",
        "Gyms with very high weekly hours don’t always get more reviews, but some outliers stand out in popularity."
    ]

    CHART_HEIGHT = 520

    def vcenter_text(text, height=CHART_HEIGHT, font_size=34):
        return f"""
            <div style="
                display:flex;
                align-items:center;
                justify-content:center;
                min-height:{height}px;
                text-align:center;
            ">
                <div style="font-size:{font_size}px; line-height:1.3; margin:0;">
                    {text}
                </div>
            </div>
        """

    for i, chart in enumerate(plotly_charts):
        chart = style_plotly(chart)
        chart.update_layout(height=CHART_HEIGHT)
        col1, col2 = st.columns(2)

        text_block = vcenter_text(chart_texts[i] if i < len(chart_texts) else "")

        if i % 2 == 0:
            with col1:
                st.plotly_chart(chart, use_container_width=True, key=f"plot_{i}")
            with col2:
                st.markdown(text_block, unsafe_allow_html=True)
        else:      
            with col1:
                st.markdown(text_block, unsafe_allow_html=True)
            with col2:
                st.plotly_chart(chart, use_container_width=True, key=f"plot_{i}")

        st.markdown("---")

        
show_graphs(graphs)
