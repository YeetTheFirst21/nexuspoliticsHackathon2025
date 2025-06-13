import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import MarkerCluster
import streamlit as st

@st.cache_data
def load_boundaries():
    bund = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_LAN.shp").to_crs(epsg=4326)
    kreis = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_KRS.shp").to_crs(epsg=4326)
    gemeinde = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_GEM.shp").to_crs(epsg=4326)

    bund["geometry"] = bund["geometry"].simplify(0.001)
    kreis["geometry"] = kreis["geometry"].simplify(0.001)
    gemeinde["geometry"] = gemeinde["geometry"].simplify(0.001)

    for col in bund.columns:
        if pd.api.types.is_datetime64_any_dtype(bund[col]):
            bund[col] = bund[col].astype(str)
    for col in kreis.columns:
        if pd.api.types.is_datetime64_any_dtype(kreis[col]):
            kreis[col] = kreis[col].astype(str)
    for col in gemeinde.columns:
        if pd.api.types.is_datetime64_any_dtype(gemeinde[col]):
            gemeinde[col] = gemeinde[col].astype(str)

    return bund, kreis, gemeinde

def create_map(bund, kreis, gemeinde, issues):
    # Use a dark tile layer
    m = folium.Map(location=[51.0, 10.0], zoom_start=6, tiles="OpenStreetMap")

    # Add GeoJson layers with higher-contrast colors for dark background
    gj_bund = folium.GeoJson(
        bund,
        name="Bundesländer",
        style_function=lambda x: {"fillColor": "#1e3a8a80", "color": "#60a5fa", "weight": 2},
        show=True,
        tooltip=folium.GeoJsonTooltip(fields=["GEN"], aliases=["State:"], style=("background-color: #222; color: #fff;"))
    )
    gj_bund.add_to(m)

    gj_kreis = folium.GeoJson(
        kreis,
        name="Landkreise",
        style_function=lambda x: {"fillColor": "#05966980", "color": "#34d399", "weight": 2},
        show=False,
        tooltip=folium.GeoJsonTooltip(fields=["GEN"], aliases=["District:"], style=("background-color: #222; color: #fff;"))
    )
    gj_kreis.add_to(m)

    gj_gemeinde = folium.GeoJson(
        gemeinde,
        name="Gemeinden",
        style_function=lambda x: {"fillColor": "#b91c1c80", "color": "#f87171", "weight": 2},
        show=False,
        tooltip=folium.GeoJsonTooltip(fields=["GEN"], aliases=["Municipality:"], style=("background-color: #222; color: #fff;"))
    )
    gj_gemeinde.add_to(m)

    # Clustered points with a lighter color for visibility
    marker_cluster = MarkerCluster(name="Issues").add_to(m)
    for _, row in issues.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            color="#fbbf24",
            fill=True,
            fill_color="#fbbf24",
            fill_opacity=0.85,
            popup=row["description"],
            tooltip=row["category"]
        ).add_to(marker_cluster)

    folium.LayerControl(collapsed=False).add_to(m)

    return m