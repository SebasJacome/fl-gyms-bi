import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd
import folium
import branca.colormap as cm
from folium.plugins import MarkerCluster, HeatMap

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

    df_b = pd.read_parquet("./data/business.parquet")
    db_r = pd.read_parquet("./data/review.parquet")
    db_u = pd.read_parquet("./data/tip.parquet")

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
