import pydeck
import geopandas as gpd
import pandas as pd
import streamlit as st

def get_centroid(geodf, region_name):
    row = geodf[geodf['GEN'] == region_name]
    if not row.empty:
        return row.iloc[0].geometry.centroid.y, row.iloc[0].geometry.centroid.x
    return 51.1634, 10.4477

class PoliticsMap:
    def __init__(self, zoom, districts_data):
        self.zoom = zoom
        self.districts_data = districts_data
        self.view_state = pydeck.ViewState(
            latitude=48.1351, longitude=11.5820, zoom=6.5, min_zoom=5, max_zoom=15
        )

        self.bund, self.kreis, self.gemeinde = self.load_shapefiles()

    @st.cache_data
    def load_shapefiles(_self):
        bund_gdf = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_LAN.shp")
        bund_gdf["geometry"] = bund_gdf["geometry"].simplify(0.001)
        bund = bund_gdf.to_crs(epsg=4326)

        kreis_gdf = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_KRS.shp")
        kreis_gdf["geometry"] = kreis_gdf["geometry"].simplify(0.001)
        kreis = kreis_gdf.to_crs(epsg=4326)
        
        gemeinde_gdf = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_GEM.shp")
        gemeinde_gdf["geometry"] = gemeinde_gdf["geometry"].simplify(0.001)
        gemeinde = gemeinde_gdf.to_crs(epsg=4326)
        return bund, kreis, gemeinde
    def get_admin_regions_layer(self):
        pickable = False
        return [
            pydeck.Layer(
                "GeoJsonLayer",
                data=self.bund,
                id="bundeslaender",
                get_fill_color=[0, 0, 255, 80],
                get_line_color=[0, 0, 0],
                get_line_width=1,
                pickable=pickable,
                auto_highlight=True,
                visible=self.zoom == 1
            ),
            pydeck.Layer(
                "GeoJsonLayer",
                data=self.kreis,
                id="landkreise",
                get_fill_color=[0, 255, 0, 80],
                get_line_color=[255,255,255],
                get_line_width=100,
                pickable=pickable,
                auto_highlight=True,
                visible=self.zoom == 2
            ),
            pydeck.Layer(
                "GeoJsonLayer",
                data=self.gemeinde,
                id="gemeinde",
                get_fill_color=[255, 0, 0, 80],
                get_line_color=[0, 0, 0],
                get_line_width=1,
                pickable=pickable,
                auto_highlight=True,
                visible=self.zoom == 3
            )
        ]

    def get_points_layer(self):
        return pydeck.Layer(
            "ScatterplotLayer",
            data=self.districts_data,
            id="issues",
            get_position=["longitude", "latitude"],
            get_color="[75, 75, 255]",
            pickable=True,
            auto_highlight=True,
            get_radius="size",
        )
    
    def get_deck(self):
        self.deck = pydeck.Deck(
            self.get_admin_regions_layer() + [self.get_points_layer()],
            initial_view_state=self.view_state,
            tooltip={"text": "{category}\n{date}\n{GEN}"}
        )
        return self.deck

    def update_zoom(self, new_zoom):
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            self.deck = self.get_updated_deck()
        return self.deck