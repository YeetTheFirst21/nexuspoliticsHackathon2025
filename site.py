import streamlit as st
import pydeck
import pandas as pd
from streamlit.components.v1 import html



def main():
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

    cities = {
        "Garching bei München": {"latitude": 48.2496, "longitude": 11.6584},
        "Würzburg": {"latitude": 49.7913, "longitude": 9.9534},
        "Heilbronn": {"latitude": 49.1427, "longitude": 9.2109},
        "München": {"latitude": 48.1351, "longitude": 11.5820}
    }
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



    #reformatting cities to be in the same format as capitals with their latitude and longitude
    cities = pd.DataFrame(cities.items(), columns=["Capital", "coordinates"])
    cities[["Latitude", "Longitude"]] = pd.DataFrame(cities["coordinates"].tolist(), index=cities.index)
    #adding a size column to the cities dataframe
    # size is the diameter of the circle that will be drawn on the map.
    cities["size"] = 5000
    #st.write(cities)




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

    view_state = pydeck.ViewState(
        # the default zoom on the map.
        latitude=48.1351, longitude=11.5820, zoom=6.5, min_zoom=5, max_zoom=15
    )


    chart2 = pydeck.Deck(
        point_layer2,
        initial_view_state=view_state,
        # this is what is shown on hover when you hover over a point on the map
        tooltip={"text": "{Capital}\n{Latitude}, {Longitude}"},
    )


    # this is the map itself
    mainMap = st.pydeck_chart(chart2, on_select="rerun", selection_mode="multi-object",height=800)

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