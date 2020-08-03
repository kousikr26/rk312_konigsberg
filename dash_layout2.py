import pandas as pd
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_table
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import dash_bootstrap_components as dbc
import dash_draggable



df = pd.read_csv('./data/final_data.csv')

default_duration_slider_val = [0, 100]

durations = {}
for i in range(0, int(df['Duration'].max()), 10):
    durations[i] = str(i)

time_str = ['0', '0', ':', '0', '0']
times = {0: {'label': "".join(time_str), "style": {
    "transform": "rotate(-90deg) translateY(-15px)"}}}
for i in range(0, 48):
    if i % 2 == 0:
        time_str[3] = '3'
        times[i+1] = {'label': "".join(time_str), "style": {'display': 'none'}}
    else:
        if i%4==3:
            time_str = list(
                        str(int("".join(time_str[0:2])) + 1).zfill(2) + str(':00'))
            times[i+1] = {'label': "".join(time_str),
                                "style": {"transform": "rotate(-90deg) translateY(-15px)"}}
        else:
            time_str = list(
                str(int("".join(time_str[0:2])) + 1).zfill(2) + str(':00'))
            times[i+1] = {'label': "".join(time_str),
                        "style": {"transform": "rotate(-90deg) translateY(-15px)",'display':'none'}}

final_data_columns = ["Receiver","Date","TowerID"]

final_ipdr_columns = ["App_name","Total Volume","Date","Time","Duration","Private IP"]

dash_layout2 = html.Div(children=[
                                dbc.Row(children=[html.Div(children=[
				                                    html.Img(
				                                        src='assets/filter.png',width='20px',id='collapse-filters', style={'cursor':'pointer'}
				                                    ),
				                                    html.Img(
				                                        src='assets/reset.png',width='20px',id='reset-button',n_clicks=0, style={'cursor':'pointer'}
				                                    ),
                                                    html.Img(
				                                        src='assets/drag.png',width='20px',id='fix-button',n_clicks=0, style={'cursor':'pointer'}
				                                    ),
				                                   	dcc.Upload(
				                                                                                        id='upload-data',
				                                                                                        children=html.Img(src='assets/file-upload.png',
				                                                                                        width='20px'),
				                                                                                        
				                                                                                        # Allow multiple files to be uploaded
				                                                                                        multiple=False
				                                                                                    ),
				                                     html.Div(id='output-data-upload'),

				                                     dbc.Tooltip(
													            "Click to toggle Filters",
													            target="collapse-filters",
													            placement = 'right'
													        ),

				                                     dbc.Tooltip(
													            "Click to Reset filter values",
													            target='reset-button',
													            placement = 'right'
													        ),

				                                     dbc.Tooltip(
				                                     		"Click to upload the database in .csv format",
				                                     		target='upload-data',
				                                     		placement='right',
				                                     	)
                                    
                                				],id='sidebar')
                                                
                                                ]),
                                dbc.Row(children=[html.Div(children=[ 
                                                    html.Div([
                                                    html.Img(src='assets/Logo.jpeg',height='50px'),
                                                    html.H1('CDR Analyser'),],id='header-title'), # TITLE BOLDED, for more 'oompf'.
                                                    html.Br(),
                                                    html.Div([
                                                    html.I('Welcome back officer, You can analyse the phone calls and internet activity of people'),  # Subtitle
                                                  
                                                    html.H4(id='message')],id='header-subtitle'),  # Message
                                                  ],id='header-text')]),
                                
                                
                                dash_draggable.dash_draggable(
                                                                                    id='draggable-filters',
                                                                                    axis='both',
                                                                                    handle='.handle',
                                                                                    defaultPosition={'x': 0, 'y': 2},
                                                                                    position=None,
                                                                                    grid=[25, 25],
                                                                                    children=[
                                                                                        html.Div(
                                                                                            id='draggable-filters-div',
                                                                                            className='handle',
                                                                                            children=[
                                                                        dbc.Row(id='filters',children=[          # for all filters

                                                                                
                                                                                dbc.Col(children=[     # to from
                                                                      
                                                                                        html.Div([
                                                                                        html.Div([html.H5(
                                                                                            'From:'

                                                                                        ),
                                                                                            dcc.DatePickerSingle(
                                                                                                id='date-picker1',
                                                                                                min_date_allowed=df['Date'].min(),
                                                                                                max_date_allowed=df['Date'].max(),
                                                                                                initial_visible_month=dt(2020, 6, 5),
                                                                                                date=str(dt(2020, 6, 17, 0, 0, 0)),
                                                                                                display_format='DD-MMM-YY',
                                                                                                style={'z-index':1000},
                                                                                                with_portal=True,
                                                                                            )],  # Data Picker
                                                                                            ),
                                                                                        dbc.Tooltip(
                                                                                            "Start Date",
                                                                                            target= 'date-picker1',
                                                                                            placement = 'right'
                                                                                        ),

                                                                                        html.Div([
                                                                                                html.H5(
                                                                                            'To:'
                                                                                        ),
                                                                                        dcc.DatePickerSingle(
                                                                                            id='date-picker2',
                                                                                            min_date_allowed=df['Date'].min(),
                                                                                            max_date_allowed=df['Date'].max(),
                                                                                            initial_visible_month=dt(2020, 6, 5),
                                                                                            date=str(dt(2020, 6, 17, 0, 0, 0)),
                                                                                            display_format='DD-MMM-YY',
                                                                                            with_portal=True
                                                                                        ),])],id='from-to-box'),  # Data Picker
                                                                                        
                                                                                        dbc.Tooltip(
                                                                                            "End Date",
                                                                                            target= 'date-picker2',
                                                                                            placement = 'right'
                                                                                        ),
                                                                                           html.Div([''],className='spacing'),
                                                                                      html.H5(
                                                                                                                'Time of Day:'
                                                                                                                ),
                                                                                                         
                                                                                                             # Time Slider

                                                                                                            dbc.Tooltip(
                                                                                                                "Filter on Time of Day",
                                                                                                                target= 'time-slider',
                                                                                                                placement = 'right'
                                                                                                            ),
                                                                                        dcc.RangeSlider(
                                                                                                                id='time-slider',
                                                                                                                min=0,
                                                                                                                max=48,
                                                                                                                step=None,
                                                                                                                marks=times,
                                                                                                                dots=True,
                                                                                                                value=[0, 48],
                                                                                                                pushable=1

                                                                                                            ), 


                                                                                ], id='to-from-column',lg=3), 

                                                                                #OKAY

                                                                                dbc.Col(children=[  # sliders time, duration
                                                                                                    
                                                                                                    
                                                                                                                html.H5(
                                                                                                                    'Duration :'
                                                                                                                    ),

                                                                                                                dcc.RangeSlider(
                                                                                                                    id='duration-slider',
                                                                                                                    min=0,
                                                                                                                    max=df['Duration'].max(),
                                                                                                                    step=10,
                                                                                                                    marks=durations,
                                                                                                                    

                                                                                                                    value=default_duration_slider_val,
                                                                                                                    dots=True,

                                                                                                                ),  # Duration Slider

                                                                                                                dbc.Tooltip(
                                                                                                                    "Filter on Call Length",
                                                                                                                    target= 'duration-slider',
                                                                                                                    placement = 'right'
                                                                                                                ),


                                                                                                                html.Div([''],className='spacing'),
                                                                                                                dcc.Markdown(
                                                                                                                    'Showing records with durations between {} - {} minutes'.format(default_duration_slider_val[0], default_duration_slider_val[1]),
                                                                                                                    id="duration-value"
                                                                                                                ),

                                                                                                

                                                                                                    #dbc.Row(children=[
                                                 


                                                                                                            html.Div([''],className='largespacing'),
                                    
                                                                                                            html.Div([
                                                                                                            dcc.Slider(
                                                                                                                id='radius-slider',
                                                                                                                min=0,
                                                                                                                max=20,
                                                                                                                step=None,
                                                                                                                marks={
                                                                                                                    0: '0 km',
                                                                                                                    5: '5 km',
                                                                                                                    10: '10 km',
                                                                                                                    15: '15 km',
                                                                                                                    20: '20 km'
                                                                                                                },
                                                                                                                value=0)],
                                                                                                                id='radius-div',
                                                                                                                style={
                                                                                                                    'display':'none'
                                                                                                                }
                                                                                                            ),
                                                                                                        
                                                                                                            
                                                                                                            html.Div([
                                                                                                                    
                                                                                                                    ]),
                                                                                                            html.H5(
                                                                                                                ''
                                                                                                            ),# For visual clarity

                                                                                                    #])

                                                                                                        

                                                                                ], id='sliders-column',lg=3), 

                                                                                # OKAY
                                                                                                                                    
                                                                                dbc.Col(children=[    # caller, receiver
                                                                                      #  dbc.Row(   children=[      #condition
                                                                                                        html.H5(
                                                                                                            'Condition for Caller/Reciever:'
                                                                                                        ),
                                                                                                        dcc.Dropdown(
                                                                                                            id='select-caller-receiver',
                                                                                                            options=[{'label': 'Only Caller', 'value': 1}]+[{'label': 'Only Receiver', 'value': 2}]+[
                                                                                                                {'label': 'Either Caller or Reciever', 'value': 3}]+[{'label': 'Both Caller and Reciever', 'value': 4}],
                                                                                                            value=3,
                                                                                                        ),  # Select if you want the select the numbers to be from Caller/Reciever/Both/Either
                                                                                                    
                                                                                                        dbc.Tooltip(
                                                                                                            "Filter the person on the basis of type of call",
                                                                                                            target='select-caller-receiver',
                                                                                                            placement = 'right'
                                                                                                        ),

                                                                                                        html.H5(
                                                                                                            ''
                                                                                                        ),# For visual clarity

                                                                                        #]),  
                                                                                        dbc.Row(children=[
                                                                                            dbc.Col(# choose caller
                                                                                            children=[
                                                                                                        html.H5(
                                                                                                                'Caller:'
                                                                                                            ),
                                                                                                            dcc.Dropdown(
                                                                                                                id='caller-dropdown',
                                                                                                                options=[{'label': 'None', 'value': 'None'}] + \
                                                                                                                [{'label': k, 'value': k} for k in df['Caller'].unique()],
                                                                                                                value='None',
                                                                                                                multi=True,
                                                                                                            ),  # Dropdown for Caller

                                                                                                            dbc.Tooltip(
                                                                                                                "Select the numbers to display whom they called",
                                                                                                                target='caller-dropdown',
                                                                                                                placement = 'right'
                                                                                                            ),


                                                                                            ],
                                                                                            id='column-1',lg=3),
                                                                                            dbc.Col( #choose receiver
                                                                                                children=[
                                                                                                            html.H5(
                                                                                                                'Reciever:'
                                                                                                            ),
                                                                                                            dcc.Dropdown(
                                                                                                                id='receiver-dropdown',
                                                                                                                options=[{'label': 'None', 'value': 'None'}] + \
                                                                                                                [{'label': k, 'value': k} for k in df['Receiver'].unique()],
                                                                                                                value='None',
                                                                                                                multi=True,
                                                                                                            ),  # Dropdown for Reciever,

                                                                                                            dbc.Tooltip(
                                                                                                                "Select the numbers to display whom they were called by",
                                                                                                                target= 'receiver-dropdown',
                                                                                                                placement = 'right'
                                                                                                            ),
                                                                                                            
                                                                                                            html.H5(
                                                                                                                ''
                                                                                                            ),# For visual clarity

                                                                                            ],id='column-2',lg=3),
                                                                                            
                                                                                        
                                                                                        ]),
                                                                                ], id='filters-user',lg=6)]   
                                                                        )])]), 

###FILTERS DONE*****************************************************************************************


#
                                            html.Div(children=[
                                                       # for network plot wala column
                                                    
                                                                     dash_draggable.dash_draggable(
                                                                                    id='draggable-plot-area',
                                                                                    axis='both',
                                                                                    handle='.handle',
                                                                                    defaultPosition={'x': 0, 'y': 2},
                                                                                    position=None,
                                                                                    grid=[25, 25],
                                                                                    children=[
                                                                                        html.Div(
                                                                                            id='draggable-plot-area-div',
                                                                                            className='handle',
                                                                                            children=[

                                                    html.Div(children=[
                                                                       
                                                                    dash_draggable.dash_draggable(
                                                                                    id='draggable-toggle-plot',
                                                                                    axis='both',
                                                                                    handle='.handle',
                                                                                    defaultPosition={'x': 0, 'y': 2},
                                                                                    position=None,
                                                                                    grid=[25, 25],
                                                                                    children=[
                                                                                        html.Div(
                                                                                            id='draggable-toggle-div',
                                                                                            className='handle',
                                                                                            children=[
                                                                        html.Div(children=[
                                                                        html.H3('Network Plot ', id='Network-Plot-text'),
                                                                        dbc.Tooltip(
                                                                        	"The plot of all the callers and receivers as a directed graph",
                                                                        	target='Network-Plot-text',
                                                                        	placement='top'
                                                                        	),


                                                                       daq.ToggleSwitch(id='toggle-network-map',value=False, size=40),


                                                                       html.H3('Map Plot', id = 'Map-Plot-text')],id='plot-header'),

                                                                       dbc.Tooltip(
																            "Plot of Tower IDs with above average traffic",
																            target='Map-Plot-text',
																            placement = 'top'
																        ),
                                                                        ])]),
                                                                        html.Div([

                                                                             html.Div(
                                                                              
                                                                                children=dash_draggable.dash_draggable(
                                                                                    id='draggable-network',
                                                                                    axis='both',
                                                                                    handle='.handle',
                                                                                    defaultPosition={'x': 0, 'y': 2},
                                                                                    position=None,
                                                                                    grid=[25, 25],
                                                                                    children=[
                                                                                        html.Div(
                                                                                            id='draggable-network-div',
                                                                                            className='handle',
                                                                                            children=[
                                                                        html.Div([
                                                                        dcc.Graph(
                                                                            id='network-plot'

                                                                        ), 
                                                                        html.H5('The size of the dots and the width of the edges denote the total duration of the caller/receiver'),
                                                                        dcc.Markdown("""
                                                                        x -> Selected Caller
                                                                                Diamond Cross -> Selected Receiver
                                                                                o -> Other
                                                                                """),] ,id='network-plot-div'),
                                                                                            ])])),
                                                                        ###### 

                                                                      
                                                                        dash_draggable.dash_draggable(
                                                                                    id='draggable-movement',
                                                                                    axis='both',
                                                                                    handle='.handle',
                                                                                    defaultPosition={'x': 0, 'y': 2},
                                                                                    position=None,
                                                                                    grid=[25, 25],
                                                                                    children=[
                                                                                        html.Div(
                                                                                            id='draggable-movement-div',
                                                                                            className='handle',
                                                                                            children=[
                                                                        html.Div([
                                                                        html.Div(children=[
                                                                        html.H3('Movement', id='Movement-text'),
                                                                        dbc.Tooltip(
																            "Path Trace of the selected person with respect to Tower IDs",
																            target='Movement-text',
																            placement = 'left'
																        ),

                                                                       daq.ToggleSwitch(id='toggle-movement-time',value=False, size=40),
                                                                       html.H3('Time Series', id='Time-Series-text')],id='toggle-mov-div'),
                                                                       dbc.Tooltip(
																            "Call Duration over time of the selected person",
																            target='Time-Series-text',
																            placement = 'right'
																        ),

                                                                        dcc.Graph(id='movement-plot'),
                                                                        dcc.Graph(id='duration-plot')
                                                                                            ], id='movement-div')
                                                                        ])])],id='network-view'),
                                                                      
                                                                     dash_draggable.dash_draggable(
                                                                                    id='draggable-map',
                                                                                    axis='both',
                                                                                    handle='.handle',
                                                                                    defaultPosition={'x': 0, 'y': 2},
                                                                                    position=None,
                                                                                    grid=[25, 25],
                                                                                    children=[
                                                                                        html.Div(
                                                                                            id='draggable-map-div',
                                                                                            className='handle',
                                                                                            children=[
                                                                         dcc.Graph(
                                                                            id='map-plot'
                                                                        )])])


                                                                     ],id='plot-area'),
                                                                     ])]),     # Network Plot
                                                    
                                                    
                                                      # for stats column
                                                    
                                                    dash_draggable.dash_draggable(
                                                                                    id='draggable-stats',
                                                                                    axis='both',
                                                                                    handle='.handle',
                                                                                    defaultPosition={'x': 0, 'y': 2},
                                                                                    position=None,
                                                                                    grid=[25, 25],
                                                                                    children=[
                                                                                        html.Div(
                                                                                            id='draggable-stats-div',
                                                                                            className='handle',
                                                                                            children=[
                                                    html.Div(children=[
                                                                        dcc.Markdown('# Statistics'),
                                                                        html.Div([ 
                                                                            html.H3('Hover:'),
                                                                                    dcc.Markdown("""
                                                                                                     Mouse over nodes in the graph to get statistics.
                                                                                                """),
                                                                                    html.Pre(id='hover-data',)
                                                                                ],id='hover-data-div'),  # Hover Data Container

                                                                      html.Div([
                                                                            html.H3('Click:'),
                                                                            dcc.Markdown("""
                                                                            **Click to get CDR and IPDR for a number** \n
                                                                            
                                                                            Selected number:
                                                                        """),
                                                                            html.Div(
                                                                                id="display-selected-num"
                                                                            ),
                                                                             html.Div(children=[
                                                                        html.H3('Calls '),
                                                                       daq.ToggleSwitch(id='toggle-cdr-ipdr',value=False, size=40),
                                                                       html.H3('Internet')],id='switch-cdr-ipdr'),
                                                                            # html.Div([
                                                                            # html.Pre(id='click-data-table', )]
                                                                            # , id='click-data-cdr-table'),   
                                                                                   
                                                                            html.Div([html.Pre(id='click-data-table',)],id='click-cdr-data-table'),                                            
                                                                    
                                                                            dash_table.DataTable(id='click-data-cdr-table', columns=(
                                                                               [{'id': header, 'name': header} for header in final_data_columns]
                                                                            ),),
                                
                                                                            html.Div([
                                                                            dcc.Markdown(
                                                                                "#### Usage Statistics of various Apps"
                                                                                ),

                                                                            dcc.Graph(
                                                                                id='pie-chart'
                                                                            ),

                                                                            dcc.Markdown(
                                                                                    "**App usage of the person selected**"
                                                                                ),

                                                                            #html.Pre(id='click-data-ipdr-table', ),
                                                                            dash_table.DataTable(id='click-data-ipdr-table', columns=(
                                                                                 [{'id': header, 'name': header} for header in final_ipdr_columns] 
                                                                             ),),

                                                                            dcc.Markdown(
                                                                                    "**The information of all the other persons who were using the same App during the constraints selected**"
                                                                                ),

                                                                            html.Pre(id='click-data-ipdr-piechart')],id='click-data-ipdr-div'),
                                                                            

                                    
                                                                        ]),  # Click Data Container 494 bracket
                                                
                                                                        

                                                                        html.Div([
                                                                            html.H3('Select'),
                                                                                    dcc.Markdown("""
                                                                                        Select using rectangle/lasso or by using your mouse.(Use Shift for multiple selections)
                                                                                    """),

                                                                                    html.Div(children=[
                                                                                                        html.Div([dbc.Button(children=[
                                                                                                            html.Img(src='assets/vision.png',height='24px')
                                                                                                        ],size="lg", id='toggle-components',className='buttons',n_clicks=0)],style={'textAlign':'center'}),
                                                                                                        

                                                                                                          html.Pre(id='selected-data', ),
                                                                                                      ])  
                                                                                ])
                                                                          # Selection Data Container


                                                                     ],id='stats')
                                                                                            ])])

                                            
                                            ], id='main-area') ,  

                                    html.Div(
                                            id='filtered-data',
                                            style={'display': 'none'}
                                        ), # Filtered Data

])
    




