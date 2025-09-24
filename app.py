import streamlit as st
from streamlit_folium import st_folium
import folium
url="https://raw.githubusercontent.com/rahimiabdulrahmanab/Clinics-Dashboard/refs/heads/main/Clinics.csv"
df=pd.read_csv(url)
# Columns: left for filter, right for search & toggle
left_col, right_col = st.columns([1, 1])

# ---------------- LEFT: Province filter ----------------
with left_col:
    st.header("Filter Clinics")
    provinces = ["All"] + list(df['Province Name'].unique())
    selected_province = st.selectbox("Select Province", provinces)

    if selected_province == "All":
        filtered_df = df.copy()
        center_lat = df['Latitude'].mean()
        center_lon = df['Longitude'].mean()
        zoom_level = 6
    else:
        filtered_df = df[df['Province Name'] == selected_province]
        center_lat = filtered_df['Latitude'].mean()
        center_lon = filtered_df['Longitude'].mean()
        zoom_level = 7

# ---------------- RIGHT: Search + Distance toggle ----------------
with right_col:
    st.subheader("Search Facility")
    search_name = st.text_input("Enter Facility Name:")
    show_distances = st.radio("Options", ["None", "Distance Between Clinics"])

# ----------------- Create base map -----------------
m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

# ----------------- Add markers -----------------
for _, row in filtered_df.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"{row['Facility Name (DHIS2)']} ({row['District Name']})",
        tooltip=row['Facility Name (DHIS2)'],
        icon=folium.DivIcon(html=f"""
        <div style="
            width: 15px;
            height: 15px;
            border-radius: 50%;
            border: 2px solid red;
            background-color: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: red;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            box-shadow: 5px 5px 6px rgba(0,0,0,0.5);
        ">✚</div>
        """)
    ).add_to(m)

# ----------------- Handle search -----------------
if search_name:
    clinic = df[df['Facility Name (DHIS2)'].str.contains(search_name, case=False)]
    if not clinic.empty:
        c = clinic.iloc[0]
        folium.Marker(
            location=[c['Latitude'], c['Longitude']],
            popup=f"{c['Facility Name (DHIS2)']} ({c['District Name']})",
            icon=folium.Icon(color="green", icon="star")
        ).add_to(m)
        m.location = [c['Latitude'], c['Longitude']]
        m.zoom_start = 10
        st.write(f"**Selected Clinic Info:** Province: {c['Province Name']}, District: {c['District Name']}, Facility ID: {c['FacilityID']}")

# ----------------- Handle distance between clinics -----------------
if show_distances == "Distance Between Clinics":
    nangarhar_df = df[df['Province Name'] == "Nangarhar"]
    m.location = [34.43, 70.44]
    m.zoom_start = 8
    # draw lines between nearest clinics (reuse Haversine + DivIcon distance labels logic)
    # ...

# ----------------- Add custom map title -----------------
title_html = """
    <h3 style="color:darkblue; font-size:18px; margin-bottom:10px; margin-top:-10px; text-align:center;">
        Clinics Map
    </h3>
"""
m.get_root().html.add_child(folium.Element(title_html))

# ----------------- Display map -----------------
st_folium(m, width=700, height=500)
