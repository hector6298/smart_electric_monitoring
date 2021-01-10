# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dataviz.timeseries import Timeseries
from dash.exceptions import PreventUpdate
#from dataviz.barchart import Barchart #needs more work

import datetime
import plotly.express as px
import pandas as pd
import json

from paho.mqtt import client as mqtt_client

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Specifying the Data Source 
broker = 'YOUR_BROKER_URL'
port = 11703
topic = "current"
# generate client ID with pub prefix randomly
client_id = f'CLIENT_ID'
username = 'YOUR_USER'
password = 'YOUR_PASS'

# we will acumulate the historic data here
master_df =  pd.DataFrame(columns=['time','current', 'power']).set_index('time')
slicer = 0

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username=username, password=password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global master_df

        json_string = msg.payload.decode()
        json_map = json.loads(json_string)
        master_df = master_df.append(json_map, ignore_index=True)
        print(f"Received `{json_string}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message

client = connect_mqtt()
subscribe(client)

# styling constants
colors = {
    'background': 'white',
    'text': 'black'
}

# generating html layout
timeseries = Timeseries(pd.DataFrame(columns=['time','current', 'power']).set_index('time'), 'power_consumption', y=[["current","power"]])
timeseries.add_dropdrown(
    'Select measure', 'tw-dropdown', ["current", "power", "all"])
timeseries.add_interval('tw-refresh', 1)

app.layout = html.Div( style={'backgroundColor': colors['background']}, children=[

    # header element
    html.H1(
        children='Electric consumption measures',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    # subheader
    html.Div(children='This is just a Demo using Dash.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),  # we append our data viz here
    html.Div(style={
        'textAlign': 'center',
        'color': colors['text']
    },
        children=[
        timeseries.layout(),
    ]),
    dcc.Interval(
            id='data-update',
            interval=1000
            ),
    html.P(id='placeholder'),
])


# Here we use the selected value on the dropdown to filter the dataframe rows
@app.callback(
    Output('power_consumption', 'figure'),
    Input('tw-refresh', 'n_intervals'),Input('tw-dropdown', 'value'), prevent_initial_call=True)   
def update_tw_timeseries(n, selected_measurement):
    '''Updates the tw-figure with new data recieved from databricks aplying the dropdown filter
        a new row from master_df is displayed on each iteration'''

    global master_df
    client.loop()
    # applies dropdown filter
    if selected_measurement and selected_measurement != "all":
        electric_lines = px.line(master_df, y=f"{selected_measurement}")
    else:
        electric_lines = px.line(master_df, y=["current","power"])

    electric_lines.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        xaxis_title="Timeline",
        yaxis_title="measure",
        legend_title="Electric consumption over time",
    )
    
    return electric_lines




if __name__ == '__main__':
    app.run_server(debug=True)

