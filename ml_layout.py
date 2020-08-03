import dash_core_components as dcc
import dash_html_components as html

ml_layout=html.Div([

    html.Div([
         dcc.Dropdown(
            id='ml-mode',
            options=[{'label': 'None', 'value': 0}]+[{'label': 'Suspicious Locations', 'value': 1}]+[{'label': 'Suspicious Users', 'value': 2}]+[{'label': 'Machine Learning - Isolation Forest', 'value': 3}]+[{'label': 'Machine Learning - Elliptic Envelope', 'value': 4}]+[
                {'label': 'Machine Learning - Local Outlier Factor', 'value': 5}] +[{'label': 'Statistical Anomaly', 'value': 6}],
            value=0,
        ),  
        dcc.Slider(
            id='contamination-slider',
            min=1,
            max=10,
            step=None,
            marks={
            
            1: '0.01',
            2: '',
            3: '0.03',
            4: '',
            5: '0.05',
            6: '',
            7: '0.07',
            8: '',
            9: '0.09',
            10:''
            },
            

            value=1,
            

        ),
    ]),


])
