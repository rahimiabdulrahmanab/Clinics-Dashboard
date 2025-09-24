# ===== IMPORT LIBRARIES =====
import pandas as pd
import folium
import numpy as np
from streamlit_folium import st_folium
import streamlit as st

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Afghanistan Clinics Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ===== TOP HEADER =====
st.markdown(
    """
    <div style='background-color:#4CAF50;padding:20px;border-radius:10px;margin-bottom:10px'>
        <h1 style='color:white;text-align:center;'>Afghanistan Clinics Dashboard</h1>
    </div>
    """, unsafe_allow_html=True
)

# ===== LOAD DATA =====
url = "https://raw.githubusercontent.com/rahimiabdulrahmanab/Clinics-Dashboard/main/Clinics.csv"
df = pd.read_csv(url)

# Exclude clinic with wrong coordinates
df = df[df["Facility Name (DHIS2)"] != "Jokan-CHC (8629)"]

# ===== HAVERSINE FUNCTION =====
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat/2)**2 +
         np.cos(np.radians(lat1))*np.cos(np.radians(lat2))*np.sin(dlon/2)**2)
    c = 2 * np.arcsin(np.sqrt(a))
    return R*c

# ===== SIDEBAR =====
st.sidebar.header("Filter Clinics")
provinces = ["All"] + list(df['Province Name'].unique())
selected_province = st.sidebar.selectbox("Select Province", provinces)

# Filter data
if selected_province == "All":
    filtered_df = df
else:
    filtered_df = df[df['Province Name'] == selected_province]

# ===== DETERMINE MAP CENTER =====
if not filtered_df.empty:
    center_lat = filtered_df['Latitude'].mean()
    center_lon = filtered_df['Longitude'].mean()
    zoom_level = 7 if selected_province != "All" else 6
else:
    center_lat, center_lon = 34.5, 69.2
    zoom_level = 6.5

# ===== CREATE COLUMNS =====
col1, col2 = st.columns([3, 1])  # Left for map (3/4), right for table (1/4)

# ===== MAP =====
with col1:
    afg_map = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)
    for _, row in filtered_df.iterrows():
        popup_html = f"""
        <table style="border-collapse: collapse; width: 220px;">
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
            tooltip=f"{row['Facility Name (DHIS2)']}",
            icon=folium.DivIcon(html='<div style="color:red;font-size:12px;">✚</div>')
        ).add_to(afg_map)
    
    st_folium(afg_map, width=900, height=600)

# ===== TABLE =====
with col2:
    st.markdown("### Clinic Details")
    st.dataframe(filtered_df.reset_index(drop=True))
