pip install streamlit pandas folium streamlit-folium plotly numpy
streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px

# --- Load data ---
url = "https://raw.githubusercontent.com/rahimiabdulrahmanab/Clinics-Dashboard/refs/heads/main/Clinics.csv"
df = pd.read_csv(url)

# Exclude clinic with wrong coordinates
df = df[df["Facility Name (DHIS2)"] != "Jokan-CHC (8629)"]

# --- Haversine formula ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat/2)**2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
         np.sin(dlon/2)**2)
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# --- Streamlit Page Config ---
st.set_page_config(page_title="Afghanistan Clinics Dashboard", layout="wide")

# --- Title ---
st.title("Afghanistan Clinics Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Province selection
provinces = ["All"] + list(df['Province Name'].unique())
selected_province = st.sidebar.selectbox("Select Province", provinces)

# Search by facility name
search_name = st.sidebar.text_input("Search Clinic by Name:")

# Options for Nangarhar distance lines
show_distance = st.sidebar.radio("Options:", ["Hide Distances", "Show Distances (Nangarhar)"])

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
afg_map = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

# Add markers
for _, row in filtered_df.iterrows():
    popup_html = f"""
    <table style="border-collapse: collapse; width: 250px;">
      <tr><th colspan="2" style="text-align:center; background-color:#f2f2f2;">{row['Facility Name (DHIS2)']}</th></tr>
      <tr><td style="border:1px solid black; padding:3px;">Province</td><td style="border:1px solid black; padding:3px;">{row['Province Name']}</td></tr>
      <tr><td style="border:1px solid black; padding:3px;">District</td><td style="border:1px solid black; padding:3px;">{row['District Name']}</td></tr>
      <tr><td style="border:1px solid black; padding:3px;">Facility ID</td><td style="border:1px solid black; padding:3px;">{row['FacilityID']}</td></tr>
      <tr><td style="border:1px solid black; padding:3px;">Facility Type</td><td style="border:1px solid black; padding:3px;">{row['Facility Type']}</td></tr>
      <tr><td style="border:1px solid black; padding:3px;">Donor</td><td style="border:1px solid black; padding:3px;">{row['Donor']}</td></tr>
    </table>
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_html,
        tooltip=f"<strong>{row['Facility Name (DHIS2)']}</strong><br>{row['District Name']}",
        icon=folium.DivIcon(html=f"""
        <div style="
            width: 15px;
            height: 15px;
            border-radius: 50%;
            border: 2px solid white;
            background-color: red;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        ">
            ✚
        </div>
        """)
    ).add_to(afg_map)

# --- Add distance lines if Nangarhar selected ---
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
            mid_lat = (lat1 + nearest['Latitude']) / 2
            mid_lon = (lon1 + nearest['Longitude']) / 2
            folium.map.Marker([mid_lat, mid_lon],
                              icon=folium.DivIcon(html=f"<div style='font-size: 10px; color: black;'>{nearest_dist:.2f} km</div>")
                              ).add_to(afg_map)

# --- Display Map ---
st.subheader("Clinics Map")
st_data = st_folium(afg_map, width=1000, height=600)

# --- Selected Clinic for Table & Histogram ---
selected_clinic_name = None
if st_data and st_data.get("last_active_drawing"):
    selected_clinic_name = st_data["last_active_drawing"].get("properties", {}).get("name")

# If search filtered results exist, just take first clinic for table/histogram
if not selected_clinic_name and not filtered_df.empty:
    selected_clinic_name = filtered_df.iloc[0]['Facility Name (DHIS2)']

if selected_clinic_name:
    selected_clinic = df[df['Facility Name (DHIS2)'] == selected_clinic_name]
else:
    selected_clinic = filtered_df.head(1)

# --- Display Table ---
st.subheader("Clinic Details")
st.table(selected_clinic)

# --- Histogram ---
st.subheader("Facilities Distribution")
hist_fig = px.histogram(filtered_df, x="Facility Type", color="Facility Type", title="Facility Type Count")
st.plotly_chart(hist_fig, use_container_width=True)
