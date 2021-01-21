# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
import plotly.express as px
import pandas as pd
import json
import time
import argparse

from dash.dependencies import Input, Output
from dataviz.timeseries import Timeseries
from dash.exceptions import PreventUpdate
from paho.mqtt import client as mqtt_client
from sqlalchemy import create_engine, MetaData, Table, Column, Time, Float

parser = argparse.ArgumentParser()
parser.add_argument("-broker", help="The broker address to connect to")
parser.add_argument("-port", help="The port of the broker")
parser.add_argument("-user", help="Your mqtt username credentials")
parser.add_argument("-psswd", help="Your password to connect to broker")
args = parser.parse_args()

RECONNECT_DELAY_SECS = 2
BROKER = args.host
PORT = int(args.port)
TOPIC = "current"
CLIENT_ID = args.user
USERNAME = args.user
PASSWORD = args.psswd

#create sql engine. CHange table creation and parameters as you see fit. For testing, sqlite is used
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
meta = MetaData()
master_record = Table(
   'master_record', meta, 
   Column('time', Time, primary_key = True), 
   Column('current', Float), 
   Column('power', Float),
)
meta.create_all(engine)

# we will acumulate the historic data in dataframes and the users inside dicts.
master_df = pd.DataFrame(columns=['time', 'username', 'current', 'power']).set_index('time')
available_users = dict()
slicer = 0

def create_mqtt_client() -> mqtt_client:

    #define callback for when client is connected
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(TOPIC)
        else:
            print("Failed to connect, return code %d\n", rc)

    #define callback for when message arrives
    def on_message(client, userdata, msg):
        global master_df
        global available_users

        json_string = msg.payload.decode()
        json_map = json.loads(json_string)
        if json_map["username"] not in available_users:
            available_users[json_map["username"]] = pd.DataFrame(columns=['time', 'username', 'current', 'power']).set_index('time')
        available_users[json_map["username"]] = available_users[json_map["username"]].append(json_map, ignore_index=True)
        master_df = master_df.append(json_map, ignore_index=True)
        with engine.connect() as conn:
            conn.execute(
                text(f"INSERT INTO master_record VALUES (:time, :current, :power)"),
                [{"time": json_map["time"], "current": json_map["current"], "power": json_map["power"]}]
            )
            conn.commit()
        print(f"Received `{json_string}` from `{msg.topic}` topic")

    #define callback for when clients gets disconnected
    def on_disconnect(client, userdata, rc):
        print(f"Disconnected from MQTT server with code: {rc}")
        while rc != 0:
            time.sleep(RECONNECT_DELAY_SECS)
            print("Reconnecting...")
            rc = client.reconnect()
        print("Successfully reconnected to broker")
        client.publish(topic="reset", 
                       payload=json.dump({"username": userdata["username"], 
                                          "reconnect_timestamp": datetime.datetime.now()}),
                                           qos=1, 
                                           retain=False)

    client = mqtt_client.Client(CLIENT_ID, clean_session=False)
    client.username_pw_set(username=USERNAME, password=PASSWORD)

    #assign callbacks to client
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.user_data_set({"username": USERNAME})
    client.connect(BROKER, PORT)
    #subscribe(client)
    return client

#Define dashh app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#create client and start loop on another thread
client = create_mqtt_client()
client.loop_start()

# styling constants
colors = {
    'background': 'white',
    'text': 'black'
}

# generating html layout
timeseries = Timeseries(pd.DataFrame(columns=['time', 'username', 'current', 'power']).set_index('time'), 
                                    'power_consumption', x="time", y="power")
timeseries.add_dropdrown('Select username', 'tw-dropdown', available_users.keys)
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
def update_tw_timeseries(n, selected_user):
    '''Updates the tw-figure with new data recieved from databricks aplying the dropdown filter
        a new row from master_df is displayed on each iteration'''
    global master_df
    global available_users

    # applies dropdown filter
    if selected_user and selected_user != "all":
        electric_lines = px.line(available_users[selected_user], x="time", y="power")
    else:
        temp_df = master_df.groupby("time").sum()
        electric_lines = px.line(temp_df, x="time", y="power")

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

