import geopandas as gpd
import pandas as pd
import pydeck
import streamlit as st
import os
from politics_map import PoliticsMap
#from streamlit import _bottom
from streamlit_extras.bottom_container import bottom

from datetime import datetime
from politics_map import PoliticsMap, get_centroid


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
# Issues DATA
issues_with_districts = pd.read_csv('./data/challenge_2/complete_issues_data.csv',
    parse_dates=['timestamp'],
    usecols=['category', 'latitude', 'longitude', 'description', 'state', 'district', 'municipality', 'age_group', 'gender', 'origin', 'timestamp']
)
issues_with_districts["size"] = 5000

def main():
    st.markdown("<h1 style='text-align: center;'>Politics Heatmap of Germany @ nexus Politics Hackathon 2025</h1>", unsafe_allow_html=True)

    filtered_data = issues_with_districts.copy()
    politics_map = PoliticsMap(2, filtered_data) 

    lat, lon, zoom = 51.1634, 10.4477, 6.5


    # removes streamlit ads...
    st.markdown("""
        <style>
            .stMainBlockContainer { margin-top: -5em; }
            .stAppHeader {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            .stAppDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
        </style>
    """, unsafe_allow_html=True)

with bottom():
    st.markdown("## Filters")

    col1, col2 = st.columns(2)

    with col1:
        # Time resolution
        time_resolution = st.selectbox("Time Resolution", ["Raw issues", "Daily", "Weekly", "Monthly"])
        if time_resolution == "Raw issues":
            filtered_data = issues_with_districts.copy()
        elif time_resolution == "Daily":
            filtered_data = pd.read_csv("./data/challenge_2/daily_aggregated.csv")
        elif time_resolution == "Weekly":
            filtered_data = pd.read_csv("./data/challenge_2/weekly_aggregated.csv")
        elif time_resolution == "Monthly":
            filtered_data = pd.read_csv("./data/challenge_2/monthly_aggregated.csv")

        if "count" in filtered_data.columns:
            filtered_data["size"] = filtered_data["count"] * 100

        # Location
        location_level = st.selectbox("Location Level", ["All Germany", "State", "District", "Municipality"])
        geo_value = None
        if location_level == "State":
            geo_value = st.selectbox("Select State", sorted(issues_with_districts["state"].dropna().unique()))
            filtered_data = filtered_data[filtered_data["state"] == geo_value]
            lat, lon = get_centroid(politics_map.bund, geo_value)
            zoom = 7.5
        elif location_level == "District":
            geo_value = st.selectbox("Select District", sorted(issues_with_districts["district"].dropna().unique()))
            filtered_data = filtered_data[filtered_data["district"] == geo_value]
            lat, lon = get_centroid(politics_map.kreis, geo_value)
            zoom = 9
        elif location_level == "Municipality":
            geo_value = st.selectbox("Select Municipality", sorted(issues_with_districts["municipality"].dropna().unique()))
            filtered_data = filtered_data[filtered_data["municipality"] == geo_value]
            lat, lon = get_centroid(politics_map.gemeinde, geo_value)
            zoom = 11

        # Origin
        origin = st.selectbox("Origin", ["All"] + sorted(issues_with_districts["origin"].dropna().unique()))
        if origin != "All":
            filtered_data = filtered_data[filtered_data["origin"] == origin]

    with col2:
        # Category
        categories = sorted(filtered_data["category"].dropna().unique())
        selected_categories = st.pills("Select category", options=categories, default=categories, selection_mode="multi")
        filtered_data = filtered_data[filtered_data["category"].isin(selected_categories)]

        # Demographics
        age = st.selectbox("Age Group", ["All"] + sorted(issues_with_districts["age_group"].dropna().unique()))
        gender = st.selectbox("Gender", ["All"] + sorted(issues_with_districts["gender"].dropna().unique()))

        if age != "All":
            filtered_data = filtered_data[filtered_data["age_group"] == age]
        if gender != "All":
            filtered_data = filtered_data[filtered_data["gender"] == gender]
        st.success(f"{len(filtered_data)} issues shown on map.")


    # politics_map = PoliticsMap(2, districts_data)
    # mainMap = st.pydeck_chart(
    #     politics_map.get_deck(),
    #     selection_mode="multi-object",
    #     height=800,
    #     key="main_map"
    # )
    if "lat" not in locals():
        lat, lon, zoom = 51.1634, 10.4477, 6.5

    filtered_data = filtered_data.rename(columns={"latitude": "latitude", "longitude": "longitude"})
    politics_map = PoliticsMap(2, filtered_data)
    politics_map.view_state.latitude = lat
    politics_map.view_state.longitude = lon
    politics_map.view_state.zoom = zoom

    st.pydeck_chart(
        politics_map.get_deck(),
        selection_mode="multi-object",
        height=800,
        key="main_map"
    )

    # this removes openstreetmap logo at the bottom right of the map
    st.markdown('<style>.mapboxgl-ctrl-bottom-right{display: none;}</style>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()