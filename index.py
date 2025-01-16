from dash import Dash, dcc, html, callback, Input, Output, no_update
import dash_bootstrap_components as dbc
import pathlib
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import zipfile

# https://cartographyvectors.com/map/1604-new-york-zip-codes
with open("new-york-zip-codes-_1604.geojson") as f:
    zip_geojson = json.load(f)


df = pd.read_csv("NYC_Building_Energy_and_Water_Data_Disclosure_for_Local_Law_84__2022-Present__20250114.zip")
# df.rename(columns={"Electricity - Weather Normalized Site Electricity Intensity (Grid and Onsite Renewables) (kWh/ftÂ²)": "Site-Electricity-Intensity"}, inplace=True)

df['Site-Electricity-Intensity'] = df['Site-Electricity-Intensity'].replace('Not Available', '0')
df['Site-Electricity-Intensity'] = df['Site-Electricity-Intensity'].astype(float)

df['MedianEUI'] = df['MedianEUI'].replace('Not Available', '0')
df['MedianEUI'] = df['MedianEUI'].astype(float)

print(df['Site-Electricity-Intensity'].dtype)
print(df['MedianEUI'].dtype)

df["Postal Code"] = df["Postal Code"].astype(str)

def create_choropleth_map(dataframe, color, range_color, labels):
    """
    Creates a choropleth map with customizable range_color and labels.

    Returns:
    - fig: A Plotly choropleth map figure.
    """
    fig = px.choropleth_map(
        data_frame=dataframe,
        color=color,
        range_color=range_color,
        labels=labels,
        geojson=zip_geojson,
        opacity=0.5,
        zoom=10,
        featureidkey="properties.ZCTA5CE10",
        map_style="open-street-map",
        locations='Postal Code',
        center={"lat": 40.7128, "lon": -74.0060},
        height=650
    )
    return fig


app = Dash()
app.layout = [
    dcc.Dropdown(id='measurments', value='ENERGY STAR Score',
                 options=['ENERGY STAR Score',
                          'Indoor Water Use (All Water Sources) (kgal)',
                          'Year Built']
    ),
    dcc.Graph(id='zip-map'),
    html.Div(id='filler')
]

@callback(
    Output('zip-map', 'figure'),
    Input('measurments', 'value')
)
# choropleth function
def make_graph(measurment_chosen):
    df[measurment_chosen] = pd.to_numeric(df[measurment_chosen], errors='coerce')
    df_filtered = df.groupby('Postal Code')[measurment_chosen].mean().reset_index()

    if measurment_chosen == 'ENERGY STAR Score':
        fig = create_choropleth_map(df_filtered, color=measurment_chosen, range_color=[35, 75],
                                    labels={'ENERGY STAR Score': 'Energy Score'}, )
    elif measurment_chosen == 'Indoor Water Use (All Water Sources) (kgal)':
        fig = create_choropleth_map(df_filtered, color=measurment_chosen, range_color=[2000, 8000],
                                    labels={'Indoor Water Use (All Water Sources) (kgal)': 'Indoor Water Use'})
    elif measurment_chosen == 'Year Built':
        df_filtered['Year Built'] = df_filtered['Year Built'].astype(int)
        fig = create_choropleth_map(df_filtered, color=measurment_chosen, range_color=[1925, 1965], labels=None)

    return fig

# zoomed in scatter plot function
@callback(
    Output('filler', 'children'),
    Input('zip-map', 'clickData')
)
def make_graph(clicked_data):
    if clicked_data:
        zipcode = clicked_data['points'][0]['location']
        df_filtered = df[df["Postal Code"] == zipcode]

        fig = px.scatter_map(df_filtered, lat="Latitude", lon="Longitude",
                             hover_name="Year Built",
                             hover_data=["Site-Electricity-Intensity"],
                             # (kBtu/ftÂ²)
                             # Energy Use Intensity
                             color="MedianEUI",
                             color_continuous_scale=['green', 'orange', 'red'],
                             zoom=12,
                             # size_max='Site-Electricity-Intensity',  # Maximum size of points
                             height=400)
        fig.update_traces(marker=dict(size=11, opacity=0.8))
        return dcc.Graph(figure=fig)
    else:
        return no_update


if __name__ == '__main__':
    app.run(debug=True)