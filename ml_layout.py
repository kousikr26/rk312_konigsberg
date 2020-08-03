import dash_core_components as dcc
import dash_html_components as html

ml_layout=html.Div([

    html.Div([
         dcc.Dropdown(
            id='ml-mode',
            options=[{'label': 'None', 'value': 0}]+[{'label': 'Isolation Forest', 'value': 1}]+[{'label': 'Elliptic Envelope', 'value': 2}]+[
                {'label': 'Local Outlier Factor', 'value': 3}],
            value=0,
        ),  
        dcc.Slider(
            id='contamination-slider',
            min=1,
            max=10,
            step=None,
            marks={
            
            1: '0.01',
            2: '0.02',
            3: '0.03',
            4: '0.04',
            5: '0.05',
            6: '0.06',
            7: '0.07',
            8: '0.08',
            9: '0.09',
            10:'0.10'
            },
            

            value=1,
            

        ),
    ]),


])