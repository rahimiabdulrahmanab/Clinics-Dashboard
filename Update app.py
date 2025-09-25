import pandas as pd
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Load data
url = "https://raw.githubusercontent.com/rahimiabdulrahmanab/Clinics-Dashboard/refs/heads/main/Clinics.csv"
df = pd.read_csv(url)

# Initialize app
app = dash.Dash(__name__)
app.title = "Afghanistan Clinics Dashboard"

# Map figure
map_fig = px.scatter_mapbox(
    df,
    lat="Latitude",
    lon="Longitude",
    hover_name="Facility Name (DHIS2)",
    hover_data=["Province Name", "District Name", "Facility Type", "Donor"],
    color="Facility Type",
    zoom=5,
    height=600
)
map_fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})

# Layout
app.layout = html.Div([
    html.H1("Afghanistan Clinics Dashboard", style={"textAlign": "center"}),

    html.Div([
        # Left Sidebar
        html.Div([
            html.Label("Select Province:"),
            dcc.Dropdown(
                id="province-dropdown",
                options=[{"label": p, "value": p} for p in sorted(df["Province Name"].unique())],
                value=None,
                placeholder="Choose a province"
            ),
            html.Br(),

            html.Label("Search Clinic:"),
            dcc.Input(id="search-input", type="text", placeholder="Enter facility name"),
            html.Button("Search", id="search-button"),

        ], style={"width": "20%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"}),

        # Map (Center)
        html.Div([
            dcc.Graph(id="map", figure=map_fig)
        ], style={"width": "55%", "display": "inline-block"}),

        # Right Sidebar
        html.Div([
            html.Label("Options:"),
            dcc.RadioItems(
                id="options-radio",
                options=[
                    {"label": "Show Distances (Nangarhar)", "value": "dist"},
                    {"label": "Hide Distances", "value": "hide"}
                ],
                value="hide"
            ),
            html.Br(),

            html.Div(id="histogram-container")
        ], style={"width": "20%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"}),

    ]),

    # Bottom Table
    html.Div([
        html.H3("Clinic Details"),
        dash_table.DataTable(
            id="clinic-table",
            columns=[{"name": col, "id": col} for col in df.columns],
            data=[],
            page_size=5,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"backgroundColor": "#f2f2f2", "fontWeight": "bold"}
        )
    ], style={"padding": "20px"})
])

# Callbacks
@app.callback(
    Output("map", "figure"),
    Output("clinic-table", "data"),
    Output("histogram-container", "children"),
    Input("province-dropdown", "value"),
    Input("search-button", "n_clicks"),
    Input("search-input", "value"),
    Input("options-radio", "value")
)
def update_dashboard(province, n_clicks, search_value, option):
    dff = df.copy()

    # Province filter
    if province:
        dff = dff[dff["Province Name"] == province]

    # Search filter
    if search_value:
        dff = dff[dff["Facility Name (DHIS2)"].str.contains(search_value, case=False, na=False)]

    # Map
    fig = px.scatter_mapbox(
        dff,
        lat="Latitude",
        lon="Longitude",
        hover_name="Facility Name (DHIS2)",
        hover_data=["Province Name", "District Name", "Facility Type", "Donor"],
        color="Facility Type",
        zoom=6 if province else 5,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})

    # Table
    table_data = dff.to_dict("records")

    # Histogram (example: count of facility types)
    hist_fig = px.histogram(dff, x="Facility Type", title="Facilities Distribution")
    histogram = dcc.Graph(figure=hist_fig)

    return fig, table_data, histogram


if __name__ == "__main__":
    app.run_server(debug=True)
