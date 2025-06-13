import streamlit as st
from folium_map import load_boundaries, create_map
from streamlit_folium import st_folium
import pandas as pd

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
issues = pd.read_csv(
        './data/challenge_2/issues_with_districts.csv',
        usecols=['category', 'latitude', 'longitude', 'description']
    ).drop_duplicates()

main_map = create_map(bund, kreis, gemeinde, issues)
map_data = st_folium(main_map, width=1100, height=800)

# --- Show popup in Streamlit if a marker is clicked ---
if map_data and map_data.get("last_object_clicked"):
    clicked = map_data["last_object_clicked"]
    lat = clicked["lat"]
    lon = clicked["lng"]
    # Find the issue closest to the clicked marker
    match = issues.loc[
        ((issues["latitude"] - lat).abs() < 1e-5) & ((issues["longitude"] - lon).abs() < 1e-5)
    ]
    if not match.empty:
        row = match.iloc[0]
        st.markdown(f"""
        ### 📝 Issue Details
        - **Category:** {row['category']}
        - **Description:** {row['description']}
        - **Latitude:** {row['latitude']}
        - **Longitude:** {row['longitude']}
        """)