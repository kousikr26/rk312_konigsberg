import dash_core_components as dcc
import dash_html_components as html

StatAnom_layout=html.Div([

    html.Div([
                html.H3(''),

                dcc.Graph(id='Duration-distribution-plot'),

                html.H3(''),

                dcc.Dropdown(
                        id='Anomaly-from-dropdown',
                        options=[{'label': 'None', 'value': 0}]+[{'label': 'Duration - CDR', 'value': 1}] + [{'label': 'Duration - IPDR', 'value': 2}]+[{'label': 'Uplink Volume', 'value': 3}]+[
                            {'label': 'Downlink Volume', 'value': 4}] + [{'label': 'Total Volume', 'value': 5}],
                        value=0,
                )
            ])
    ],id='stat-anom')  
