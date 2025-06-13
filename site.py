import streamlit as st
import pydeck
import geopandas as gpd
import pandas as pd
from streamlit.components.v1 import html
import os

# Add cached data loading for shapefiles
@st.cache_data
def load_shapefiles():
    bund = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_LAN.shp").to_crs(epsg=4326)
    land = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_KRS.shp").to_crs(epsg=4326)
    gemeinde = gpd.read_file("./data/vg5000_ebenen_1231/VG5000_GEM.shp").to_crs(epsg=4326)
    return bund, land, gemeinde

# Load administrative boundaries
bund, land, gemeinde = load_shapefiles()

# Get layer dynamically
def get_admin_layers(current_zoom):
    return [
        pydeck.Layer(
            "GeoJsonLayer",
            data=bund,
            id="bundeslaender",
            get_fill_color=[0, 0, 255, 80],
            pickable=False,
            visible=current_zoom < 8
        ),
        pydeck.Layer(
            "GeoJsonLayer",
            data=land,
            id="landkreise",
            get_fill_color=[0, 255, 0, 80],
            pickable=False,
            visible=8 <= current_zoom < 12
        ),
        pydeck.Layer(
            "GeoJsonLayer",
            data=gemeinde,
            id="gemeinde",
            get_fill_color=[255, 0, 0, 80],
            pickable=False,
            visible=current_zoom >= 12
        )
    ]


cities = {
        "Garching bei München": {"latitude": 48.2496, "longitude": 11.6584},
        "Würzburg": {"latitude": 49.7913, "longitude": 9.9534},
        "Heilbronn": {"latitude": 49.1427, "longitude": 9.2109},
        "München": {"latitude": 48.1351, "longitude": 11.5820}
    }
#reformatting cities to be in the same format as capitals with their latitude and longitude
cities = pd.DataFrame(cities.items(), columns=["Capital", "coordinates"])
cities[["Latitude", "Longitude"]] = pd.DataFrame(cities["coordinates"].tolist(), index=cities.index)
#adding a size column to the cities dataframe
# size is the diameter of the circle that will be drawn on the map.
cities["size"] = 5000
#st.write(cities)

def main():

    if "done_init" not in st.session_state:
        st.session_state["done_init"] = True
        # st.set_page_config(
        #     # collapses the pages sidebar if there are any pages in pages dir.
        #     initial_sidebar_state="collapsed",
        #     layout="wide"
        # )
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

    # Initial zoom
    current_zoom = view_state.zoom

    # Get map return data to track zoom
    chart2 = None
    map_return = None

    # Build layers based on zoom
    admin_layers = get_admin_layers(current_zoom)
    point_layer2 = pydeck.Layer(
        "ScatterplotLayer",
        data=cities,
        id="cities",
        get_position=["Longitude", "Latitude"],
        get_color="[75, 75, 255]",
        pickable=True,
        auto_highlight=True,
        get_radius="size",
    )
    chart2 = pydeck.Deck(
        layers=[point_layer2] + admin_layers,
        initial_view_state=view_state,
        tooltip={"text": "{Capital}\n{Latitude}, {Longitude}"},
    )

    # If zoom changed, rebuild layers
    if map_return and "viewState" in map_return:
        current_zoom = map_return["viewState"]["zoom"]
        admin_layers = get_admin_layers(current_zoom)
        chart2 = pydeck.Deck(
            layers=[point_layer2] + admin_layers,
            initial_view_state=view_state,
            tooltip={"text": "{Capital}\n{Latitude}, {Longitude}"},
        )
    
    mainMap = st.pydeck_chart(
        chart2,
        on_select="rerun",
        selection_mode="multi-object",
        height=800,
        key="main_map"
    )
    
    try:
        selectedCities = mainMap.selection["objects"]["cities"]
    except :
        selectedCities = []



    #st.write(selectedCities)

    # this removes openstreetmap logo at the bottom right of the map
    st.markdown('<style>.mapboxgl-ctrl-bottom-right{display: none;}</style>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 2])
    with col1:
        
        if len(selectedCities) > 0:
            option = st.selectbox("🧳Select Starting City", cities["Capital"].tolist(), index=cities["Capital"].tolist().index(selectedCities[0]["Capital"]))
        else:
            option = st.selectbox("🧳Select Starting City", cities["Capital"].tolist(), index=0)
    with col2:
        if len(selectedCities) > 1:
            option2 = st.selectbox("🏠Select Destination City", cities["Capital"].tolist(), index=cities["Capital"].tolist().index(selectedCities[1]["Capital"]))
        else:
            option2 = st.selectbox("🏠Select Destination City", cities["Capital"].tolist(), index=1)

    # with st.popover("View Connection"):
    #     # Define the coordinates for first two selected cities:
    #     if len(selectedCities) == 2:
    #         line_data = pd.DataFrame([
    #             {"start": [selectedCities[0]["Longitude"], selectedCities[0]["Latitude"]], "end": [selectedCities[1]["Longitude"], selectedCities[1]["Latitude"]]}
    #         ])

    #         # Create a LineLayer
    #         line_layer = pydeck.Layer(
    #             "LineLayer",
    #             data=line_data,
    #             get_source_position="start",
    #             get_target_position="end",
    #             get_color=[255, 0, 0],
    #             get_width=5
    #         )

    #         view_state = pydeck.ViewState(
    #             latitude=48.1351, longitude=11.5820, zoom=6.5, min_zoom=5, max_zoom=15
    #         )


    #         chart3 = pydeck.Deck(
    #             line_layer,
    #             initial_view_state=view_state,
    #             tooltip={"text": "{Capital}\n{Latitude}, {Longitude}"},
    #         )
    #         st.pydeck_chart(chart3)

    col2, col3 = st.columns(2)

    with col2:
        st.subheader("Pick-up Date & Time")
        pickup_date = st.date_input("Pick-up Date")
        pickup_time = st.time_input("Pick-up Time")

    with col3:
        st.subheader("Return Date & Time")
        return_date = st.date_input("Return Date")
        import datetime
        #set time to now + 1 hour:
        return_time = st.time_input("Return Time",value=datetime.datetime.now() + datetime.timedelta(hours=1))




if __name__ == "__main__":
    main()