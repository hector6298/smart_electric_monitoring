import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


class Timeseries:

    def __init__(self, columns, timeseries_figure_id, timeseries_figure=None, **kwargs):
        self.columns = columns
        self.data = pd.DataFrame(columns=columns)
        self._children = []
        self.timeseries_figure_id = timeseries_figure_id
        self.loading_id = self.timeseries_figure_id +'_loading'

        if timeseries_figure:
            self.timeseries_figure = timeseries_figure
        else:

            self.timeseries_figure = px.line(
                self.data, **kwargs)

    def get_figure(self, **kwargs):
        return px.line(self.data, **kwargs)
        
    def append_data(self, dictionary, ignore_index=True):
        self.data = self.data.append(dictionary, ignore_index=ignore_index)

    def add_dropdrown(self, dropdown_label, dropdown_id, dropdown_options):
        self._children.extend([
            html.Span(
                children=dropdown_label
            ),

            # dropdown filter control
            dcc.Dropdown(
                id=dropdown_id,
                options=[{'label': i, 'value': i}
                         for i in dropdown_options]
            )])

    def add_interval(self, interval_id, refresh_rate):
        self._children.extend([
            dcc.Interval(
            id=interval_id,
            interval=refresh_rate*1000
            ),
        ])


    # FIXME does not work quite yet
    def add_slider(self, filtered_column):
        min_value = min(filtered_column)
        max_value = max(filtered_column)
        self._children.extend([dcc.Slider(
            min=min_value,
            max=max_value,
            marks={i: 'Label {}'.format(i) if i == 1 else str(
                i) for i in range(min_value, max_value)},

        )])

    def layout(self):
        return  html.Div(self._children +
                        [
                            
                                dcc.Graph(
                                    id=self.timeseries_figure_id,
                                    figure=self.timeseries_figure,
                                    responsive=True)
                            
                        ],
                        style={'width': '48%', 'display': 'inline-block', 'margin-top': '10%', 'rowCount': 1})
                        
                        
                
class multiInstanceTimeseries(Timeseries):

    def __init__(self, columns, timeseries_figure_id, timeseries_figure=None, **kwargs):
        super().__init__(columns, timeseries_figure_id, timeseries_figure, **kwargs)
        self.available_keys = dict()

    def get_figure_by_key(self, key, **kwargs):
        return px.line(self.available_keys[key], **kwargs)
    
    def get_available_keys(self):
        return self.available_keys

    def set_available_key(self, key):
        self.available_keys[key] = pd.DataFrame(columns=self.columns)
    
    def append_data_by_key(self, key,  dictionary, ignore_index=True):
        self.available_keys[key] = self.available_keys[key]\
                                   .append(dictionary, ignore_index=ignore_index)
