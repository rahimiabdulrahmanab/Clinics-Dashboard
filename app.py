import streamlit as st
import folium
import pandas as pd
import numpy as np
from streamlit_folium import st_folium

# Assuming your DataFrame 'df' is already loaded and processed
# If not, you'll need to include the data loading and processing code here
# Example:
url="https://raw.githubusercontent.com/rahimiabdulrahmanab/Clinics-Dashboard/refs/heads/main/Clinics.csv"
df=pd.read_csv(url)
df = df[df["Facility Name (DHIS2)"] != "Jokan-CHC (8629)"]


st.set_page_config(layout="wide")

st.title("Clinic Locations Map")

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
    # Center on mean latitude/longitude of filtered data
    center_lat = filtered_df['Latitude'].mean()
    center_lon = filtered_df['Longitude'].mean()
    # Zoom in closer if single province, farther if All
    zoom_level = 7 if selected_province != "All" else 6.45
else:
    # Default center and zoom if no data
    center_lat = 33.93911
    center_lon = 67.7100
    zoom_level = 6.45


# Create the map
m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

# Add markers for filtered clinics
for _, row in filtered_df.iterrows():
    popup_html = f'''
    <table style="border-collapse: collapse; width: 200px;">
      <tr><th colspan="2" style="text-align:center; background-color:#f2f2f2;">{row['Facility Name (DHIS2)']}</th></tr>
      <tr><td style="border:1px solid black; padding:3px;">Province</td><td style="border:1px solid black; padding:3px;">{row['Province Name']}</td></tr>
      <tr><td style="border:1px solid black; padding:3px;">District</td><td style="border:1px solid black; padding:3px;">{row['District Name']}</td></tr>
      <tr><td style="border:1px solid black; padding:3px;">Facility Type</td><td style="border:1px solid black; padding:3px;">{row['Facility Type']}</td></tr>
    </table>
    '''
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_html,
        tooltip=f"<div style='text-align: center;'><strong>{row['Facility Name (DHIS2)']}</strong><br>{row['District Name']}</div>",
        icon=folium.Icon(icon="plus", prefix="fa", color="red")
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=1000, height=800)
