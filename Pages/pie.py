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
# Data Cleaning
df.rename(columns={'Electricity Use - Grid Purchase and Generated from Onsite Renewable Systems (kWh)' : 'electricUse'}, inplace = True)
df['electricUse'] = df['electricUse'].replace('Not Available', 0)
df['electricUse'] = df['electricUse'].astype(float)
city_df = df.groupby('City')['electricUse'].mean()

fig = px.pie(df, values=[city_df['Queens'], city_df['Bronx'], city_df['Manhattan'], city_df['Staten Island'], city_df['Brooklyn']])


# callback syntax
# Output(component_id  ,      where the output will go)
# Input(component_id of where input is coming from ,      varibale that will go into output)
@callback(
    Output(),
    Input(),
)
def selectParameters():
    print()