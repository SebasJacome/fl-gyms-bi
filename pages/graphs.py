import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import folium
import branca.colormap as cm
from folium.plugins import MarkerCluster, HeatMap
import ast
from collections import Counter
import streamlit as st
import networkx as nx
from math import radians, sin, cos, sqrt, atan2


@st.cache_data
def load_datasets():
    df_b = pd.read_parquet("./data/business.parquet")
    db_r = pd.read_parquet("./data/review.parquet")
    db_u = pd.read_parquet("./data/tip.parquet")

    return df_b, db_r, db_u


def build_graphs():
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

    df_b, db_r, db_u = load_datasets()

    df = gpd.GeoDataFrame(
        df_b,
        geometry=gpd.points_from_xy(df_b.longitude, df_b.latitude)
    )

    def get_color(stars) -> str:
        if stars > 4: return "green"
        elif stars > 3: return "lightgreen"
        elif stars > 2: return "orange"
        elif stars > 1: return "red"
        return "purple"

    graphs = []


    m1 = folium.Map(location=[27.9011955, -82.5318599], zoom_start=9, tiles="cartodb positron")
    for idx, row in df_b.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            tooltip=row["name"],
            popup=folium.Popup(
                f"<b>{row['name']}</b><br>"
                f"Rating: {row['stars']} ⭐<br>",
                max_width=300
            ),
            icon=folium.Icon(color=get_color(row["stars"]), prefix="fa", icon="dumbbell")
        ).add_to(m1)
    graphs.append(m1)

    m2 = folium.Map(location=[27.9011955, -82.5318599], zoom_start=9, tiles="cartodb positron")
    tips_count = db_u.groupby("business_id").size().to_dict()
    marker_cluster = MarkerCluster().add_to(m2)
    for idx, row in df_b.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5 + row["review_count"]/50,
            color=get_color(row["stars"]),
            fill=True,
            fill_opacity=0.7,
            tooltip=f"{row['name']}<br>Stars: {row['stars']}<br>Reviews: {row['review_count']}<br>Tips: {tips_count.get(row['business_id'], 0)}"
        ).add_to(marker_cluster)
    graphs.append(m2)

    m3 = folium.Map(location=[27.9011955, -82.5318599], zoom_start=9, tiles="cartodb positron")
    data = df[["latitude", "longitude"]].values.tolist()
    HeatMap(data).add_to(m3)
    graphs.append(m3)

    m4 = folium.Map(location=[27.9011955, -82.5318599], zoom_start=9, tiles="cartodb positron")
    colormap = cm.linear.YlOrRd_09.scale(df_b["review_count"].min(), df_b["review_count"].max())
    colormap.caption = "Number of Reviews"
    for _, row in df_b.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(3, row["review_count"] ** 0.7),
            color=colormap(row["review_count"]),
            fill=True,
            fill_color=colormap(row["review_count"]),
            fill_opacity=0.6,
            tooltip=row["name"],
            popup=folium.Popup(
                f"<b>{row['name']}</b><br>"
                f"Reviews: {row['review_count']}<br>",
                max_width=300
            )
        ).add_to(m4)
    colormap.add_to(m4)
    graphs.append(m4)

    fig = px.box(
        df_b,
        x="stars",
        y="review_count",
        points=None,
        log_y=True,
        labels={"stars": "Stars", "review_count": "Review Count"},
        title="Review Count Distribution by Star Rating",
        color="stars",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_layout(showlegend=False)
    graphs.append(fig)

    fig = px.histogram(
        df_b,
        x="stars",
        nbins=10,
        labels={"stars": "Stars"},
        title="Distribution of Gym Ratings"
    )
    fig.update_traces(marker=dict(color="darkblue", line=dict(width=1, color="lightblue")))
    graphs.append(fig)

    # Scatter
    franchise_summary = df_b.groupby("name", as_index=False).agg(
        avg_stars=("stars", "mean"),
        num_locations=("business_id", "count"),
        total_reviews=("review_count", "sum")
    )

    bins = [0, 3, 6, 10, 20, 50]
    labels = ["1-3", "4-6", "7-10", "11-20", "21+"]

    franchise_summary["location_group"] = pd.cut(franchise_summary["num_locations"], bins=bins, labels=labels, right=True)

    top_franchises = franchise_summary.sort_values(by="num_locations", ascending=False).head(15)

    color_scale = [
        [0.0, "red"],
        [0.5, "yellow"],
        [1.0, "green"]
    ]

    fig = px.bar(
        top_franchises,
        x="num_locations",
        y="name",
        color="avg_stars",
        color_continuous_scale = color_scale,
        orientation="h",
        title="Top 15 Franchises by Number of Locations",
        labels={"num_locations": "Number of Locations", "name": "Franchise", "avg_stars": "Average Stars"}
    )


    graphs.append(fig)


    features_expanded = df_b["features"].dropna().apply(pd.Series)
    feature_counts = features_expanded.sum().sort_values(ascending=True)
    fig = px.bar(
        feature_counts,
        x=feature_counts.values,
        y=feature_counts.index,
        orientation="h",
        labels={"x": "Number of Gyms", "y": "Feature"},
        title="Gym Features Breakdown",
        color=feature_counts.values,
        color_continuous_scale="viridis"
    )
    fig.update_layout(showlegend=False)
    graphs.append(fig)

    working_expanded = (
        df_b["working_days"]
        .dropna()
        .apply(pd.Series)
        .melt(var_name="Day", value_name="Hours")
        .dropna()
    )
    working_expanded[["Open", "Close"]] = working_expanded["Hours"].apply(
        lambda x: pd.Series([x[0].hour, x[1].hour])
    )
    avg_hours = working_expanded.groupby("Day")[["Open", "Close"]].mean().reset_index()
    fig = px.imshow(
        avg_hours.set_index("Day"),
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale=px.colors.qualitative.Prism,
        labels=dict(color="Hour of Day"),
        title="Average Working Hours by Day"
    )
    graphs.append(fig)

    working_expanded = (
        df_b[["business_id", "stars", "working_days"]]
        .dropna(subset=["working_days"])
        .set_index("business_id")["working_days"]
        .apply(pd.Series)
        .melt(ignore_index=False, var_name="Day", value_name="Hours")
        .dropna()
        .reset_index()
    )
    working_expanded["Duration"] = working_expanded["Hours"].apply(
        lambda x: (x[1].hour + x[1].minute/60) - (x[0].hour + x[0].minute/60)
    )
    working_expanded.loc[working_expanded["Duration"] < 0, "Duration"] += 24
    weekly_hours = working_expanded.groupby("business_id")["Duration"].sum().reset_index()
    weekly_hours = weekly_hours.merge(df_b[["business_id", "stars"]], on="business_id")
    weekly_hours["stars_grouped"] = np.floor(weekly_hours["stars"]).astype(int)
    weekly_hours_clean = weekly_hours[weekly_hours["Duration"] > 0].copy()
    fig = px.histogram(
        weekly_hours_clean,
        x="Duration",
        color="stars_grouped",
        nbins=10,
        barmode="relative",
        opacity=0.6,
        labels={"Duration": "Total Weekly Hours", "stars_grouped": "Stars"},
        title="Distribution of Weekly Working Hours by Star Rating (Grouped, Cleaned)"
    )
    fig.update_layout(bargap=0.1)
    graphs.append(fig)

    fig = px.histogram(
        db_r,
        x="stars",
        title="Distribution of Review Ratings",
        color="stars",
        category_orders={"stars": sorted(db_r["stars"].unique())}
    )
    fig.update_traces(marker_line_width=1, marker_line_color="black")
    graphs.append(fig)

    corr = db_r[["stars", "useful", "funny", "cool"]].corr()
    corr = corr.mask(np.triu(np.ones_like(corr, dtype=bool))).round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdYlBu_r",
        title="Correlation Heatmap: Stars vs Engagement"
    )
    fig.update_layout(width=800, height=600, plot_bgcolor="white")
    graphs.append(fig)

    db_u["date"] = pd.to_datetime(db_u["date"])
    tips_over_time = db_u.groupby(db_u["date"].dt.to_period("M")).size().reset_index(name="tip_count")
    tips_over_time["date"] = tips_over_time["date"].dt.to_timestamp()
    fig = px.line(
        tips_over_time,
        x="date",
        y="tip_count",
        title="Number of Tips Over Time",
        labels={"date": "Month", "tip_count": "Number of Tips"},
        markers=True
    )
    events = {"2012-03": "Yelp Becomes Public", "2020-03": "COVID Starts"}
    for date, label in events.items():
        fig.add_vline(x=date, line_dash="dash", line_color="red")
        fig.add_annotation(x=date, y=max(tips_over_time["tip_count"]), text=label, showarrow=True, arrowhead=3)
    graphs.append(fig)

    db_r["date"] = pd.to_datetime(db_r["date"])
    avg_stars_per_year = db_r.groupby(db_r["date"].dt.year)["stars"].mean().reset_index()
    fig = px.line(
        avg_stars_per_year,
        x="date",
        y="stars",
        markers=True,
        title="Average Stars Over Time",
        labels={"date": "Year", "stars": "Average Stars"}
    )
    graphs.append(fig)

    features_expanded = df_b["features"].dropna().apply(pd.Series)
    feature_sums = features_expanded.sum().astype(float)
    avg_stars_per_feature = features_expanded.mul(df_b["stars"], axis=0).sum() / feature_sums.replace(0, np.nan)
    avg_stars_per_feature = avg_stars_per_feature.dropna().sort_values()
    fig = px.bar(
        avg_stars_per_feature,
        x=avg_stars_per_feature.values,
        y=avg_stars_per_feature.index,
        orientation="h",
        labels={"x": "Average Stars", "y": "Feature"},
        title="Average Stars by Gym Feature",
        color=avg_stars_per_feature.values,
        color_continuous_scale="Viridis"
    )
    fig.update_layout(coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
    graphs.append(fig)

    def total_hours(working_days):
        if pd.isna(working_days): return np.nan
        hours = 0
        for interval in working_days.values():
            if interval is None: continue
            start, end = interval if not isinstance(interval, np.ndarray) else interval
            h = (end.hour + end.minute/60) - (start.hour + start.minute/60)
            if h < 1: h += 24
            hours += h
        return hours

    df_b["total_hours"] = df_b["working_days"].apply(total_hours)
    fig = px.scatter(
        df_b,
        x="total_hours",
        y="review_count",
        color="stars",
        size="review_count",
        labels={"total_hours": "Total Weekly Hours", "review_count": "Number of Reviews", "stars": "Stars"},
        title="Total Weekly Hours vs Review Count",
        color_continuous_scale="Plasma"
    )
    graphs.append(fig)
    return graphs

def get_star_color(rating):
    if rating >= 4.5:
        return "#2ECC71"
    elif rating >= 4.0:
        return "#27AE60"
    elif rating >= 3.5:
        return "#F1C40F"
    elif rating >= 3.0:
        return "#E67E22"
    else:
        return "#E74C3C"


def horizontal_stars(avg_stars: float, title: str = "") -> go.Figure:
    total_stars = 5
    x_positions = np.arange(total_stars)
    y_positions = [0] * total_stars

    full_stars = int(avg_stars)
    partial_star = avg_stars - full_stars

    colors = []
    for i in range(total_stars):
        if i < full_stars:
            colors.append(get_star_color(avg_stars))
        elif i == full_stars and partial_star > 0:
            colors.append("#A59760")
        else:
            colors.append("#ECF0F1")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_positions,
        mode="markers",
        marker=dict(size=80, color=colors, symbol="star"),
        hoverinfo="none",
        showlegend=False
    ))

    fig.update_layout(
        title=f"{title} (Avg: {avg_stars:.2f})",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=200,
        margin=dict(l=0, r=0, t=50, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

def render_features_grid(selected_gym):
    df_b, _, _ = load_datasets()
    franchise_locations = df_b[df_b["name"] == selected_gym]

    features = (
        franchise_locations["features"]
        .dropna()
        .apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    )

    combined_features = {}
    for feature_dict in features:
        for key, value in feature_dict.items():
            if key not in combined_features:
                combined_features[key] = value
            else:
                combined_features[key] = combined_features[key] or value

    if combined_features:
        sorted_features = dict(sorted(combined_features.items()))

        num_cols = 3
        cols = st.columns(num_cols)

        for i, (feature, enabled) in enumerate(sorted_features.items()):
            color = "#2ECC71" if enabled else "#E74C3C"
            icon = "✅" if enabled else "❌"

            with cols[i % num_cols]:
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 8px;
                        margin: 6px 0;
                        border: 1px solid #444;
                        border-radius: 10px;
                        background-color: #2C2C2C;
                        color: #FFFFFF;
                        font-size: 16px;
                        text-align: center;">
                        <span style="font-size: 18px; margin-right: 8px; color:{color};">{icon}</span> {feature}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No feature data available for this franchise.")


def build_franchise_graphs(selected_gym: str):
    df_b, db_r, db_u = load_datasets()
    figures = {}

    franchise_locations = df_b[df_b["name"] == selected_gym].copy()

    lats = franchise_locations["latitude"].values
    lons = franchise_locations["longitude"].values
    n = len(lats)

    G = nx.Graph()
    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine(lats[i], lons[i], lats[j], lons[j])
            G.add_edge(i, j, weight=dist)

    mst = nx.minimum_spanning_tree(G)

    line_lats = []
    line_lons = []
    for edge in mst.edges():
        i, j = edge
        line_lats.extend([lats[i], lats[j], None])
        line_lons.extend([lons[i], lons[j], None])

    hover_text = franchise_locations.apply(
        lambda row: f"<b>{row['name']}</b><br>⭐ {row['stars']} Stars<br>{row['address']}",
        axis=1
    )

    map_fig = go.Figure()

    map_fig.add_trace(go.Scattermapbox(
        lat=franchise_locations["latitude"],
        lon=franchise_locations["longitude"],
        mode="markers",
        marker=dict(
            size=14,
            color=franchise_locations["stars"],
            colorscale=[
                [0, "#E74C3C"],
                [0.5, "#F1C40F"],
                [1, "#2ECC71"]
            ],
            cmin=2.0,
            cmax=5.0,
            showscale=True,
            colorbar=dict(title="Stars")
        ),
        hoverinfo=None,
        name=selected_gym,
        showlegend=False
    ))

    map_fig.add_trace(go.Scattermapbox(
        lat=line_lats,
        lon=line_lons,
        mode="lines",
        line=dict(width=2, color="rgba(52, 152, 219, 0.5)"),
        name="Shortest Network",
        showlegend=False,
        hoverinfo=None
    ))

    map_fig.add_trace(go.Scattermapbox(
        lat=[franchise_locations.iloc[0]["latitude"]],
        lon=[franchise_locations.iloc[0]["longitude"]],
        mode="markers",
        marker=dict(size=20, color="black", symbol="star"),
        name="HQ",
        hoverinfo=None,
        showlegend=False,
    ))

    map_fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=np.mean(lats), lon=np.mean(lons)),
            zoom=8
        ),
        margin=dict(r=0, t=30, l=0, b=0),
        title=f"Distribution of {selected_gym} Locations in Florida"
    )
    
    figures["locations_map"] = map_fig
    
    # 2. Stars
    avg_stars = float(franchise_locations["stars"].mean())
    star_fig = horizontal_stars(avg_stars, title=f"Average Rating for {selected_gym}")
    figures["average_star"] = star_fig

    # 3. Ratings
    
    franchise_reviews = db_r[db_r["business_id"].isin(franchise_locations["business_id"])].copy()
    franchise_reviews["date"] = pd.to_datetime(franchise_reviews["date"], errors="coerce")

    monthly_trend = (
        franchise_reviews
        .groupby(franchise_reviews["date"].dt.to_period("M"))
        .agg(avg_stars=("stars", "mean"), review_count=("review_id", "count"))
        .reset_index()
    )

    monthly_trend["date"] = monthly_trend["date"].astype(str)
    monthly_trend["rolling_avg"] = monthly_trend["avg_stars"].rolling(window=3, min_periods=1).mean()

    trend_fig = px.line(
        monthly_trend,
        x="date",
        y="avg_stars",
        title=f"{selected_gym} Ratings Over Time",
        labels={"date": "Month", "avg_stars": "Average Stars"},
        line_shape="spline"
    )
    trend_fig.update_traces(line=dict(color="#2ECC71", width=4), name="Monthly Avg")

    trend_fig.add_scatter(
        x=monthly_trend["date"],
        y=monthly_trend["rolling_avg"],
        mode="lines",
        line=dict(color="#E67E22", width=3, dash="dash"),
        name="3-Month Avg"
    )

    trend_fig.add_scatter(
        x=monthly_trend["date"],
        y=monthly_trend["avg_stars"],
        mode="lines",
        line=dict(color="rgba(46, 204, 113, 0.3)", width=0),
        fill='tozeroy',
        fillcolor="rgba(46, 204, 113, 0.2)",
        name="Rating Area",
        showlegend=False
    )

    min_idx = monthly_trend["avg_stars"].idxmin()
    max_idx = monthly_trend["avg_stars"].idxmax()

    trend_fig.add_annotation(
        x=monthly_trend.loc[min_idx, "date"],
        y=monthly_trend.loc[min_idx, "avg_stars"],
        text="Lowest Rating",
        showarrow=True,
        arrowhead=2,
        font=dict(color="red")
    )

    trend_fig.add_annotation(
        x=monthly_trend.loc[max_idx, "date"],
        y=monthly_trend.loc[max_idx, "avg_stars"],
        text="Highest Rating",
        showarrow=True,
        arrowhead=2,
        font=dict(color="green")
    )

    figures["ratings_over_time"] = trend_fig

    # 4. Hist
    features = (
        franchise_locations["features"]
        .dropna()
        .apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    )

    feature_counts = Counter()

    for feature_dict in features:
        for key, value in feature_dict.items():
            if value:
                feature_counts[key] += 1

    if feature_counts:
        feature_df = pd.DataFrame({
            "Feature": list(feature_counts.keys()),
            "Count": list(feature_counts.values())
        }).sort_values(by="Count", ascending=True)

        feature_fig = px.bar(
            feature_df,
            x="Count",
            y="Feature",
            orientation="h",
            title=f"Feature Availability Across {selected_gym} Locations",
            labels={"Count": "Number of Locations", "Feature": "Feature"},
        )
        feature_fig.update_traces(marker_color="#2ECC71")

    else:
        feature_fig = go.Figure()
        feature_fig.add_annotation(
            text="No feature data available",
            showarrow=False,
            x=0.5, y=0.5,
            xref="paper", yref="paper"
        )

    figures["feature_profile"] = feature_fig

    return figures
