import streamlit as st
from folium_map import load_boundaries, create_map
from streamlit_folium import st_folium


if "done_init" not in st.session_state:
    st.session_state["done_init"] = True
    st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Politics Heatmap of Germany @ nexus Politics Hackathon 2025</h1>", unsafe_allow_html=True)
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



def main():


    # loading text with circle:


    # Load data
    # Load data only once using session state
    if "map_data" not in st.session_state:
        with st.spinner("Loading map data..."):
            bund, kreis, gemeinde = load_boundaries()
            issues = load_issues()
            st.session_state["map_data"] = {
                "map": create_map(bund, kreis, gemeinde, issues)
            }

    # Display the map from session state
    with st.spinner("loading map..."):
        st_folium(
            st.session_state["map_data"]["map"], 
            width=1500, 
            height=800,
            returned_objects=[],  # Prevents re-runs on map interactions
        )

    #st.markdown('<style>.leaflet-bottom.leaflet-right{display: none;}</style>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()