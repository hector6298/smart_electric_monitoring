import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px


class Timeseries:

    def __init__(self, data, timeseries_figure_id, timeseries_figure=None, **kwargs):
        self.data = data
        self._children = []
        self.timeseries_figure_id = timeseries_figure_id
        self.loading_id = self.timeseries_figure_id +'_loading'

        if timeseries_figure:
            self.timeseries_figure = timeseries_figure
        else:

            self.timeseries_figure = px.line(
                data, **kwargs)

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
                        
                        
                
                
                

