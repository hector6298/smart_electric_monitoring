import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px


class Barchart:

    def __init__(self, data, figure_id, figure=None, **kwargs):
        self.data = None
        self._children = []
        self.figure_id = figure_id

        if figure:
            self.figure = figure
        else:
            self.figure = px.bar(
                data, x=kwargs['x'], y=kwargs['y'], color=kwargs['color'], barmode=kwargs['group'])

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

    def layout(self):
        return html.Div(self._children +
                        [
                            dcc.Graph(
                                id=self.figure_id,
                                figure=self.figure,
                            )
                        ],
                        style={'width': '48%', 'display': 'inline-block', 'margin-top': '10%', 'rowCount': 1})
