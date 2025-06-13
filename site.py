import geopandas as gpd
import pandas as pd
import pydeck
import streamlit as st
import os

if "done_init" not in st.session_state:
    st.session_state["done_init"] = True
    st.set_page_config(
        # collapses the pages sidebar if there are any pages in pages dir.
        initial_sidebar_state="collapsed",
        layout="wide"
    )
    # this removes the deploy and run crap on the top right of screen
    st.markdown(
        """
    <style>
        .st-emotion-cache-yfhhig.ef3psqc5 {
            display: none;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

# Add cached data loading for shapefiles
@st.cache_data
def load_shapefiles():
    # Bundesland
    if not os.path.exists("./data/vg5000_ebenen_1231/VG5000_LAN_simple.gpkg"):
        print("new Bundesland map needed")
        bund_gdf = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_LAN.shp", usecols=["geometry"])
        bund_gdf["geometry"] = bund_gdf["geometry"].simplify(0.01)  # higher tolerance
        bund_gdf.to_file("./data/vg5000_ebenen_1231/VG5000_LAN_simple.gpkg", driver="GPKG")
    bund = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_LAN_simple.gpkg").to_crs(epsg=4326)

    # Kreis
    if not os.path.exists("./data/vg5000_ebenen_1231/VG5000_KRS_simple.gpkg"):
        print("new kreis map needed")
        kreis_gdf = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_KRS.shp", usecols=["geometry"])
        kreis_gdf["geometry"] = kreis_gdf["geometry"].simplify(0.01)
        kreis_gdf.to_file("./data/vg5000_ebenen_1231/VG5000_KRS_simple.gpkg", driver="GPKG")
    kreis = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_KRS_simple.gpkg").to_crs(epsg=4326)

    # Gemeinde
    if not os.path.exists("./data/vg5000_ebenen_1231/VG5000_GEM_simple.gpkg"):
        print("new gemeinde map needed")
        gemeinde_gdf = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_GEM.shp", usecols=["geometry"])
        gemeinde_gdf["geometry"] = gemeinde_gdf["geometry"].simplify(0.01)
        gemeinde_gdf.to_file("./data/vg5000_ebenen_1231/VG5000_GEM_simple.gpkg", driver="GPKG")
    gemeinde = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_GEM_simple.gpkg").to_crs(epsg=4326)

    return bund, kreis, gemeinde


# Issues DATA
issues_with_districts = pd.read_csv('./data/challenge_2/issues_with_districts.csv',
                                    usecols=['category', 'latitude', 'longitude', 'description'])
districts_data = issues_with_districts[['category', 'latitude', 'longitude', 'description', ]].drop_duplicates()

districts_data["size"] = 5000

# Load administrative boundaries
bund, kreis, gemeinde = load_shapefiles()

# Get layer dynamically
def get_admin_regions_layer(current_zoom):
    return [
        pydeck.Layer(
            "GeoJsonLayer",
            data=bund,
            id="bundeslaender",
            get_fill_color=[0, 0, 255, 80],
            pickable=True,
            auto_highlight=True,
            visible=current_zoom < 8
        ),
        pydeck.Layer(
            "GeoJsonLayer",
            data=kreis,
            id="landkreise",
            get_fill_color=[0, 255, 0, 80],
            pickable=True,
            auto_highlight=True,
            visible=8 <= current_zoom < 12
        ),
        pydeck.Layer(
            "GeoJsonLayer",
            data=gemeinde,
            id="gemeinde",
            get_fill_color=[255, 0, 0, 80],
            pickable=True,
            auto_highlight=True,
            visible=current_zoom >= 12
        )
    ]

def get_points_layer():
    return pydeck.Layer(
            "ScatterplotLayer",
            data=districts_data,
            id="issues",
            get_position=["longitude", "latitude"],
            get_color="[75, 75, 255]",
            pickable=True,
            auto_highlight=True,
            get_radius="size",
        )

def update_layers(zoom_level):
    return [
        get_admin_regions_layer(zoom_level),
        get_points_layer()
    ]


def get_updated_deck(view_state, zoom_level):
    return pydeck.Deck(
                update_layers(zoom_level),
                initial_view_state = view_state,
                tooltip={"text": "{category}"},
            )


def main():

    st.markdown("<h1 style='text-align: center;'>Politics Heatmap of Germany @ nexus Politics Hackathon 2025</h1>", unsafe_allow_html=True)

    # removes streamlit ads...
    st.markdown("""
        <style>
            .stMainBlockContainer {
                margin-top: -5em;
            }
                .stAppHeader {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            .stAppDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
        </style>
    """, unsafe_allow_html=True)


    view_state = pydeck.ViewState(
        latitude=48.1351, longitude=11.5820, zoom=6.5, min_zoom=5, max_zoom=15
    )

    mainMap = st.pydeck_chart(
        get_updated_deck(view_state, view_state.zoom),
        selection_mode="multi-object",
        height=800,
        key="main_map"
    )

    #st.write(selectedCities)

    # this removes openstreetmap logo at the bottom right of the map
    st.markdown('<style>.mapboxgl-ctrl-bottom-right{display: none;}</style>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()