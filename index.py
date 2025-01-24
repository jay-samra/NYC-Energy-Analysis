from dash import Dash, dcc, html, callback, Input, Output, no_update
import dash_bootstrap_components as dbc
import pathlib
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import zipfile

from pandas.plotting import boxplot

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
        height=650,
        color_continuous_scale='matter_r',
    )
    return fig

def create_choropleth_emissions(dataframe, color, range_color, labels):
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
        height=650,
    )
    return fig
# Pie Chart ----------------------------------
# Data Cleaning
# df.rename(columns={'Electricity Use - Grid Purchase and Generated from Onsite Renewable Systems (kWh)' : 'electricUse'}, inplace = True)
# df.rename(columns={'Net Emissions (Metric Tons CO2e)' : 'netEmissions'}, inplace = True)
# df.rename(columns={'Weather Normalized Site Energy Use' : 'normalUse'}, inplace = True)
# df['electricUse'] = df['electricUse'].replace('Not Available', 0)
# df['electricUse'] = df['electricUse'].astype(float)
# city_df = df.groupby('City')['electricUse'].mean()

# fig1 = px.pie(df,values=[city_df['Queens'], city_df['Bronx'], city_df['Manhattan'], city_df['Staten Island'], city_df['Brooklyn']])
# --------------------------------------------
# Box Plot -----------------------------------
df1 = df.replace(['Manufacturing/Industrial Plant', 'Repair Services (Vehicle, Shoe, Locksmith, etc.)', 'Hospital (General Medical & Surgical)',
                 'Transportation Terminal/Station', 'Fitness Center/Health Club/Gym', 'Personal Services (Health/Beauty, Dry Cleaning, etc.)',
                 'Drinking Water Treatment & Distribution', 'Urgent Care/Clinic/Other Outpatient', 'Convenience Store without Gas Station'],
                 ['Industrial Plant', 'Repair Services', 'Hospital', 'Transportation', 'Gym', 'Personal Services', 'Water Treatment', 'Urgent Care',
                 'Store']
                )
df1_sorted = df1.sort_values(by='Site Energy Use (kBtu)', ascending=True)
fig = px.box(df1, df1['Largest Property Use Type'], df1['Site Energy Use (kBtu)'])
fig.update_layout(
    height=700,
    width=2000,
    margin=dict(l=50, r=50, t=50, b=50),)

# y axis adjustment
fig.update_layout(
    yaxis=dict(
        tickvals=[100000, 200000]
    )
)
# --------------------------------------------
# Bar Graph ----------------------------------
df['ENERGY STAR Score'] = df['ENERGY STAR Score'].replace('Not Available', 0)
df['ENERGY STAR Score'] = df['ENERGY STAR Score'].astype(float)

# adding the zipcodes that will be used
zip_df = df[df['Postal Code'].isin(['11378', '10461', '11691', '10029', '11105', '11230', '11354', '11207', '11432', '11435', '11432', '11211', '10457',
                                   '10459', '10453', '10452', '10459', '10456', '10031', '11432', '11211', '11106', '10027', '10471', '11231', '11211',
                                   '11106', '10027', '10471', '11231', '11101', '10451', '11356', '11201'])]

zip_df = zip_df.groupby('Postal Code')['ENERGY STAR Score'].mean().reset_index()

zip_df.columns = ['Postal Code', 'Mean ENERGY STAR Score']

figBox = go.Figure(
    data=[
        go.Bar(x=zip_df['Postal Code'], y=zip_df['Mean ENERGY STAR Score'], name="Gold", marker_color='rgb(26, 118, 255)'),
        # go.Bar(x=zip_df['Postal Code'], y=zip_df['ENERGY STAR Score'], name="Silver"),
        # go.Bar(x=zip_df['Postal Code'], y=zip_df['ENERGY STAR Score'], name="Bronze"),
    ],
    layout=dict(
        barcornerradius=5,
    ),
)

figBox.update_traces(marker=dict(line=dict(width=2)))
figBox.update_layout(title=dict(text="Figure Title"),
                  template='plotly_white')
# --------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
navbar = dbc.NavbarSimple(
    brand="New York City Energy Analysis Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)
app.layout = [
    html.Div(navbar),

    dcc.Dropdown(id='measurments', value='ENERGY STAR Score',
                 options=['ENERGY STAR Score',
                          'Indoor Water Use (All Water Sources) (kgal)',
                          'Year Built',
                          'Net Emissions (Metric Tons CO2e)']
    ),
    dcc.Graph(id='zip-map'),
    html.Div(id='filler'),

    dcc.Dropdown(id='pieMeasurements', options=['Electricity Use - Grid Purchase and Generated from Onsite Renewable Systems (kWh)', 'Net Emissions (Metric Tons CO2e)', 'ENERGY STAR Score'],
                 value='Onsite Renewable Systems (kWh)'),
    # add default using figure=figure
    dcc.Graph(id='pieChart'),

    html.Div(id='filler1'),

    dcc.Dropdown(df['Largest Property Use Type'].unique()),
    dcc.Graph(id='pieChart1', figure=fig),

    dcc.Graph(id='barGraph', figure=figBox),

    # geojson map
    dcc.Dropdown(id='geojson1', value='Net Emissions (Metric Tons CO2e)',
                 options=[
                          'Net Emissions (Metric Tons CO2e)',]
                 ),
    dcc.Graph(id='geojson2'),
    # html.Div(id='filler'),
]


# choropleth function
@callback(
    Output('zip-map', 'figure'),
    Input('measurments', 'value')
)
def make_graph(measurement_chosen):
    df[measurement_chosen] = pd.to_numeric(df[measurement_chosen], errors='coerce')
    df_filtered = df.groupby('Postal Code')[measurement_chosen].mean().reset_index()

    if measurement_chosen == 'ENERGY STAR Score':
        fig = create_choropleth_map(df_filtered, color=measurement_chosen, range_color=[35, 75],
                                    labels={'ENERGY STAR Score': 'Energy Score'}, )
    elif measurement_chosen == 'Indoor Water Use (All Water Sources) (kgal)':
        fig = create_choropleth_map(df_filtered, color=measurement_chosen, range_color=[2000, 8000],
                                    labels={'Indoor Water Use (All Water Sources) (kgal)': 'Indoor Water Use'})
    elif measurement_chosen == 'Year Built':
        df_filtered['Year Built'] = df_filtered['Year Built'].astype(int)
        fig = create_choropleth_map(df_filtered, color=measurement_chosen, range_color=[1925, 1965], labels=None)

    elif measurement_chosen == 'Net Emissions (Metric Tons CO2e)':
            fig = create_choropleth_map(df_filtered, color=measurement_chosen, range_color=[100, 900],
                                         labels={"Net Emissions (Metric Tons CO2e)": "Net Emissions"})


    return fig

# geojson practice
@callback(
    Output('geojson2', 'figure'),
    Input('geojson1', 'value')
)
def make_geojson(measurement_chosen):
    df[measurement_chosen] = pd.to_numeric(df[measurement_chosen], errors='coerce')
    df_filtered = df.groupby('Postal Code')[measurement_chosen].mean().reset_index()

    if measurement_chosen == 'Net Emissions (Metric Tons CO2e)':
        fig = create_choropleth_emissions(df_filtered, color=measurement_chosen, range_color=[100, 900], labels={"Net Emissions (Metric Tons CO2e)" : "Net Emissions"}  )


    return fig


@callback(
    Output('pieChart', 'figure'),
    Input('pieMeasurements', 'value'),
)
def pie_chart(option_chosen):

    labels = ['Queens', 'Bronx', 'Manhattan', 'Staten Island', 'Brooklyn']
    df[option_chosen] = df[option_chosen].replace('Not Available', 0)
    df[option_chosen] = df[option_chosen].astype(float)
    city_df = df.groupby('City')[option_chosen].mean()
    values = [
        city_df['Queens'].sum(),
        city_df['Bronx'].sum(),
        city_df['Manhattan'].sum(),
        city_df['Staten Island'].sum(),
        city_df['Brooklyn'].sum()
    ]


    if option_chosen == 'Electricity Use - Grid Purchase and Generated from Onsite Renewable Systems (kWh)':

        fig = go.Figure(data=[
            go.Pie(labels=labels, values=values, hole=0.3)]     ,)
        fig.update_layout(annotations=[dict(text='kWh', xanchor='center', showarrow=False, font_size=20)])
        # fig.add_trace( line=dict( width=2) )
    elif option_chosen == 'Net Emissions (Metric Tons CO2e)':

        fig = go.Figure(data=[
            go.Pie(labels=labels, values=values, hole=0.3)], )
        fig.update_layout(annotations=[dict(text='CO2e', xanchor='center', showarrow=False, font_size=20)])
    elif option_chosen == 'ENERGY STAR Score':

        fig = go.Figure(data=[
            go.Pie(labels=labels, values=values, hole=0.3)], )
        fig.update_layout(annotations=[dict(text='ESS',
                      font_size=20, showarrow=False, xanchor='center')])
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
                             height=650)
        fig.update_traces(marker=dict(size=11, opacity=0.8))
        return dcc.Graph(figure=fig)
    else:
        return no_update


if __name__ == '__main__':
    app.run(debug=False)