import streamlit as st
import pydeck
import geopandas as gpd
import pandas as pd
from streamlit.components.v1 import html
import os
from politics_map import PoliticsMap

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
issues_with_districts = pd.read_csv('./data/challenge_2/issues_with_districts.csv')
districts_data = issues_with_districts[['category', 'latitude', 'longitude']].drop_duplicates()
districts_data["size"] = 5000

def main():
    st.markdown("<h1 style='text-align: center;'>Politics Heatmap of Germany @ nexus Politics Hackathon 2025</h1>", unsafe_allow_html=True)

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

    

    politics_map = PoliticsMap(2, districts_data)
    mainMap = st.pydeck_chart(
        politics_map.get_deck(),
        selection_mode="multi-object",
        height=800,
        key="main_map"
    )

    # this removes openstreetmap logo at the bottom right of the map
    st.markdown('<style>.mapboxgl-ctrl-bottom-right{display: none;}</style>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()