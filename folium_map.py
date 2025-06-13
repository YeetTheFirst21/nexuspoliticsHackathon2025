import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import MarkerCluster

def load_boundaries():
    bund = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_LAN.shp").to_crs(epsg=4326)
    kreis = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_KRS.shp").to_crs(epsg=4326)
    gemeinde = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_GEM.shp").to_crs(epsg=4326)
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

def load_issues():
    return pd.read_csv(
        './data/challenge_2/issues_with_districts.csv',
        usecols=['category', 'latitude', 'longitude', 'description']
    ).drop_duplicates()

def create_map(bund, kreis, gemeinde, issues):
    m = folium.Map(location=[51.0, 10.0], zoom_start=6, tiles="cartodbpositron")

    # Add GeoJson layers with unique layer names
    fg_bund = folium.FeatureGroup(name="Bundesländer", show=True)
    fg_kreis = folium.FeatureGroup(name="Landkreise", show=False)
    fg_gemeinde = folium.FeatureGroup(name="Gemeinden", show=False)

    folium.GeoJson(
        bund,
        name="Bundesländer",
        style_function=lambda x: {"fillColor": "#0000ff40", "color": "black", "weight": 1},
        tooltip=folium.GeoJsonTooltip(fields=["GEN"], aliases=["State:"])
    ).add_to(fg_bund)

    folium.GeoJson(
        kreis,
        name="Landkreise",
        style_function=lambda x: {"fillColor": "#00ff0040", "color": "black", "weight": 1},
        tooltip=folium.GeoJsonTooltip(fields=["GEN"], aliases=["District:"])
    ).add_to(fg_kreis)

    folium.GeoJson(
        gemeinde,
        name="Gemeinden",
        style_function=lambda x: {"fillColor": "#ff000040", "color": "black", "weight": 1},
        tooltip=folium.GeoJsonTooltip(fields=["GEN"], aliases=["Municipality:"])
    ).add_to(fg_gemeinde)

    fg_bund.add_to(m)
    fg_kreis.add_to(m)
    fg_gemeinde.add_to(m)

    # Add clustered issue points
    marker_cluster = MarkerCluster(name="Issues").add_to(m)
    for _, row in issues.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color="blue",
            fill=True,
            fill_opacity=0.7,
            popup=row["description"],
            tooltip=row["category"]
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    # --- Custom JS for dynamic layer switching based on zoom ---
    custom_js = """
    function setLayerVisibility() {
        var zoom = map.getZoom();
        var layers = map._layers;
        for (var idx in layers) {
            var l = layers[idx];
            if (l.options && l.options.name) {
                if (l.options.name === "Bundesländer") {
                    if (zoom < 8) { map.addLayer(l); } else { map.removeLayer(l); }
                }
                if (l.options.name === "Landkreise") {
                    if (zoom >= 8 && zoom < 11) { map.addLayer(l); } else { map.removeLayer(l); }
                }
                if (l.options.name === "Gemeinden") {
                    if (zoom >= 11) { map.addLayer(l); } else { map.removeLayer(l); }
                }
            }
        }
    }
    map.on('zoomend', setLayerVisibility);
    setLayerVisibility();
    """
    m.get_root().script.add_child(folium.Element(f"<script>{custom_js}</script>"))

    return m