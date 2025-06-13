import streamlit as st
from folium_map import load_boundaries, create_map
from streamlit_folium import st_folium
import pandas as pd
from streamlit_extras.bottom_container import bottom 

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

# Load issue data
issues_with_districts = pd.read_csv(
    './data/challenge_2/complete_issues_data.csv',
    parse_dates=['timestamp'],
    usecols=[
        'category', 'latitude', 'longitude', 'description',
        'state', 'district', 'municipality', 'age_group',
        'gender', 'origin', 'timestamp'
    ]
)
issues_with_districts["size"] = 5000

# Load boundaries
bund, kreis, gemeinde = load_boundaries()

# Default map location
lat, lon, zoom = 51.1634, 10.4477, 6
filtered_data = issues_with_districts.copy()

def main():


    # loading text with circle:


    # Load data
    # Load data only once using session state
    if "map_data" not in st.session_state:
        with st.spinner("Loading map data..."):
            bund, kreis, gemeinde = load_boundaries()
            issues = pd.read_csv(
                './data/challenge_2/issues_with_districts.csv',
                usecols=['category', 'latitude', 'longitude', 'description']
            ).drop_duplicates()
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
with bottom():
    st.markdown("## Filters")
    col1, col2 = st.columns(2)

    with col1:
        # Time resolution selector (functionality not active here unless you process the corresponding CSVs)
        time_resolution = st.selectbox("Time Resolution", ["Raw issues", "Daily", "Weekly", "Monthly"])
        # Optional: load other resolution CSVs here

        # Location filters
        location_level = st.selectbox("Location Level", ["All Germany", "State", "District", "Municipality"])
        geo_value = None
        if location_level == "State":
            geo_value = st.selectbox("Select State", sorted(filtered_data["state"].dropna().unique()))
            filtered_data = filtered_data[filtered_data["state"] == geo_value]
        elif location_level == "District":
            geo_value = st.selectbox("Select District", sorted(filtered_data["district"].dropna().unique()))
            filtered_data = filtered_data[filtered_data["district"] == geo_value]
        elif location_level == "Municipality":
            geo_value = st.selectbox("Select Municipality", sorted(filtered_data["municipality"].dropna().unique()))
            filtered_data = filtered_data[filtered_data["municipality"] == geo_value]

        # Origin filter
        origin = st.selectbox("Origin", ["All"] + sorted(filtered_data["origin"].dropna().unique()))
        if origin != "All":
            filtered_data = filtered_data[filtered_data["origin"] == origin]

    with col2:
        # Category filter
        categories = sorted(filtered_data["category"].dropna().unique())
        selected_categories = st.pills("Select category", options=categories, default=categories, selection_mode="multi")
        filtered_data = filtered_data[filtered_data["category"].isin(selected_categories)]

        # Age and gender
        age = st.selectbox("Age Group", ["All"] + sorted(filtered_data["age_group"].dropna().unique()))
        gender = st.selectbox("Gender", ["All"] + sorted(filtered_data["gender"].dropna().unique()))

        if age != "All":
            filtered_data = filtered_data[filtered_data["age_group"] == age]
        if gender != "All":
            filtered_data = filtered_data[filtered_data["gender"] == gender]

    st.success(f"{len(filtered_data)} issues shown on map.")
if __name__ == "__main__":
    main()