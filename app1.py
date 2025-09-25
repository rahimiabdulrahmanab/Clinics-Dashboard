import pandas as pd
import folium
import numpy as np
from streamlit_folium import st_folium
import streamlit as st

# Load the data
url="https://raw.githubusercontent.com/rahimiabdulrahmanab/Clinics-Dashboard/refs/heads/main/Clinics.csv"
df=pd.read_csv(url)

# Exclude the clinic with wrong coordinates
df = df[df["Facility Name (DHIS2)"] != "Jokan-CHC (8629)"]

# Haversine formula to calculate distance (km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat/2)**2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
         np.sin(dlon/2)**2)
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# Sidebar for filtering
st.sidebar.header("Filter Clinics")

# Add "All" to the list of provinces
provinces = ["All"] + list(df['Province Name'].unique())

# Dropdown to select province
selected_province = st.sidebar.selectbox("Select Province", provinces)

# Filter data
if selected_province == "All":
    filtered_df = df
else:
    filtered_df = df[df['Province Name'] == selected_province]

# Determine map center and zoom
if not filtered_df.empty:
    # Center on mean latitude/longitude
    center_lat = filtered_df['Latitude'].mean()
    center_lon = filtered_df['Longitude'].mean()
    # Zoom in closer if single province, farther if All
    zoom_level = 9 if selected_province != "All" else 6
else:
    center_lat = 34.5
    center_lon = 69.2
    zoom_level = 6.45

# Center of Afghanistan (approx)
afg_map = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

# Add markers for filtered clinics
for _, row in filtered_df.iterrows():  # Use filtered_df here
    popup_html = f"""
    <table style="border-collapse: collapse; width: 200px;">
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
        tooltip=f"<div style='text-align: center;'><strong>{row['Facility Name (DHIS2)']}</strong><br>{row['District Name']}</div>",
        icon=folium.DivIcon(html=f"""
        <div style="
            width: 15px;
            height: 15px;
            border-radius: 50%;
            border: 2px solid white;
            background-color: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: red;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            box-shadow: 5px 5px 6px rgba(0,0,0,0.5);
        ">
            ✚
        </div>
        """)
    ).add_to(afg_map)

# Filter for Nangarhar province for distance calculation
nangarhar_df = df[df['Province Name'] == 'Nangarhar'].copy()

# Loop through each clinic in Nangarhar to add distance lines and labels
for i, row in nangarhar_df.iterrows():
    lat1, lon1 = row['Latitude'], row['Longitude']

    # Find nearest clinic within Nangarhar
    distances = []
    for j, other in nangarhar_df.iterrows():
        if i != j:
            d = haversine(lat1, lon1, other['Latitude'], other['Longitude'])
            distances.append((d, other))
    if distances:  # Check if distances list is not empty
        nearest_dist, nearest = min(distances, key=lambda x: x[0])

        # Draw line to nearest clinic
        line = [[lat1, lon1], [nearest['Latitude'], nearest['Longitude']]]
        folium.PolyLine(
            locations=line,
            color="blue",
            weight=2,
            opacity=0.6,
            tooltip=f"Nearest: {nearest['Facility Name (DHIS2)']} ({nearest_dist:.2f} km)"
        ).add_to(afg_map)

        # Add distance label in the middle of the line
        mid_lat = (lat1 + nearest['Latitude']) / 2
        mid_lon = (lon1 + nearest['Longitude']) / 2
        folium.map.Marker(
            [mid_lat, mid_lon],
            icon=folium.DivIcon(html=f"""<div style="font-size: 10px; color: black;">
                {nearest_dist:.2f} km
            </div>""")
        ).add_to(afg_map)

# Show map
st_folium(afg_map, width=700, height=500)
