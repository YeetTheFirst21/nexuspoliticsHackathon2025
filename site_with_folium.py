import streamlit as st
from folium_map import load_boundaries, load_issues, create_map
from streamlit_folium import st_folium

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

# Load data
bund, kreis, gemeinde = load_boundaries()
issues = load_issues()

# Create and show map
m = create_map(bund, kreis, gemeinde, issues)
st_folium(m, width=1100, height=800)