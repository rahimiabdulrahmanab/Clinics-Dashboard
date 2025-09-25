# app.py
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px

# --- Load data ---
url = "https://raw.githubusercontent.com/rahimiabdulrahmanab/Clinics-Dashboard/refs/heads/main/Clinics.csv"
df = pd.read_csv(url)
df = df[df["Facility Name (DHIS2)"] != "Jokan-CHC (8629)"]

# --- Haversine formula ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat/2)**2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
         np.sin(dlon/2)**2)
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# --- Page Config & CSS to fix full screen ---
st.set_page_config(page_title="Afghanistan Clinics Dashboard", layout="wide")
st.markdown("""
    <style>
        /* Fix full screen height and prevent scroll */
        html, body, [class*="css"]  {
            height: 100%;
            overflow: hidden;
        }
        .stApp {
            height: 100vh;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# --- Layout: left (map) & right (table+histogram) ---
col_map, col_right = st.columns([3,1])

with col_map:
    st.title("Afghanistan Clinics Dashboard (Map)")

    # --- Sidebar filters ---
    with st.sidebar:
        st.header("Filters")
        provinces = ["All"] + list(df['Province Name'].unique())
        selected_province = st.selectbox("Select Province", provinces)
        search_name = st.text_input("Search Clinic by Name")
        show_distance = st.radio("Options:", ["Hide Distances", "Show Distances (Nangarhar)"])

    # --- Filter Data ---
    filtered_df = df.copy()
    if selected_province != "All":
        filtered_df = filtered_df[filtered_df['Province Name'] == selected_province]
    if search_name:
        filtered_df = filtered_df[filtered_df['Facility Name (DHIS2)']
                                  .str.contains(search_name, case=False, na=False)]

    # --- Map Centering ---
    if not filtered_df.empty:
        center_lat = filtered_df['Latitude'].mean()
        center_lon = filtered_df['Longitude'].mean()
        zoom_level = 9 if selected_province != "All" else 6
    else:
        center_lat, center_lon = 34.5, 69.2
        zoom_level = 6

    # --- Create Folium Map ---
    afg_map = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, width="100%", height=800)

    for idx, row in filtered_df.iterrows():
        popup_html = f"""
        <b>{row['Facility Name (DHIS2)']}</b><br>
        Province: {row['Province Name']}<br>
        District: {row['District Name']}<br>
        Type: {row['Facility Type']}
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup_html,
            tooltip=row['Facility Name (DHIS2)'],
            icon=folium.Icon(color='red', icon='plus')
        ).add_to(afg_map)

    # --- Show Nangarhar distances ---
    if show_distance == "Show Distances (Nangarhar)":
        nangarhar_df = df[df['Province Name'] == "Nangarhar"].copy()
        for i, row in nangarhar_df.iterrows():
            lat1, lon1 = row['Latitude'], row['Longitude']
            distances = []
            for j, other in nangarhar_df.iterrows():
                if i != j:
                    d = haversine(lat1, lon1, other['Latitude'], other['Longitude'])
                    distances.append((d, other))
            if distances:
                nearest_dist, nearest = min(distances, key=lambda x: x[0])
                line = [[lat1, lon1], [nearest['Latitude'], nearest['Longitude']]]
                folium.PolyLine(locations=line, color="blue", weight=2, opacity=0.6,
                                tooltip=f"{nearest['Facility Name (DHIS2)']} ({nearest_dist:.2f} km)").add_to(afg_map)
                mid_lat = (lat1 + nearest['Latitude'])/2
                mid_lon = (lon1 + nearest['Longitude'])/2
                folium.map.Marker([mid_lat, mid_lon],
                                  icon=folium.DivIcon(html=f"<div style='font-size:10px'>{nearest_dist:.2f} km</div>")).add_to(afg_map)

    # --- Display Map ---
    map_data = st_folium(afg_map, width=900, height=800)

with col_right:
    st.header("Clinic Details")
    selected_clinic = None
    if map_data and map_data.get("last_object_clicked"):
        selected_clinic = map_data["last_object_clicked"]["tooltip"]

    if not selected_clinic and search_name:
        selected_clinic = search_name
    if not selected_clinic and not filtered_df.empty:
        selected_clinic = filtered_df.iloc[0]['Facility Name (DHIS2)']

    if selected_clinic:
        clinic_df = df[df['Facility Name (DHIS2)']==selected_clinic][
            ['Facility Name (DHIS2)','District Name','Facility Type']
        ]
    else:
        clinic_df = filtered_df[['Facility Name (DHIS2)','District Name','Facility Type']].head(1)

    st.table(clinic_df)

    st.header("Facility Type Histogram")
    hist_fig = px.histogram(clinic_df, x="Facility Type", color="Facility Type")
    st.plotly_chart(hist_fig, use_container_width=True)
