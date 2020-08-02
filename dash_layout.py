########################################################### Import Libraries ###################################################
import pandas as pd
import base64
import io
import numpy as np
import json
import networkx as nx
import plotly.graph_objects as go
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
from datetime import datetime as dt

import pygraphviz as pgv
import dash_bootstrap_components as dbc
import math
import matplotlib
import requests


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

dash_layout = html.Div(children=[
                                html.Div(children=[
                                    html.Img(
                                        src='assets/filter.png',width='20px',id='collapse-filters'
                                    ),
                                    html.Img(
                                        src='assets/reset.png',width='20px',id='reset-button',n_clicks=0
                                    ),
                                     dcc.Upload(
                                                                                        id='upload-data',
                                                                                        children=html.Img(src='assets/file-upload.png',
                                                                                        width='20px'),
                                                                                        
                                                                                        # Allow multiple files to be uploaded
                                                                                        multiple=False
                                                                                    ),
                                     html.Div(id='output-data-upload'),
                                   
                                    
                                ],id='sidebar'),
                                html.Div(children=[ 
                                                    html.Div([
                                                    html.Img(src='assets/Logo.jpeg',height='50px'),
                                                    html.H1('CDR Analyser'),],id='header-title'), # TITLE BOLDED, for more 'oompf'.
                                                    html.Br(),
                                                    html.Div([
                                                    html.I('Hello Officer, You can analyse the phone calls and internet activity of people'),  # Subtitle
                                                  
                                                    html.H4(id='message')],id='header-subtitle'),  # Message
                                                  ],id='header-text'),



                                dbc.Row(children=[

                                                    dbc.Col(children=[
                                                                        dcc.Markdown("# Filters"),
                                                                         html.H5(
                                                                            'Condition for Caller/Reciever:'
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id='select-caller-receiver',
                                                                            options=[{'label': 'Only Caller', 'value': 1}]+[{'label': 'Only Receiver', 'value': 2}]+[
                                                                                {'label': 'Either Caller or Reciever', 'value': 3}]+[{'label': 'Both Caller and Reciever', 'value': 4}],
                                                                            value=3,
                                                                        ),  # Select if you want the select the numbers to be from Caller/Reciever/Both/Either
                                                                    
                                                                        html.H5(
                                                                            ''
                                                                        ),# For visual clarity

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

                                                                        html.H5(
                                                                            ''
                                                                        ),# For visual clarity

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
                                                                        
                                                                        html.H5(
                                                                            ''
                                                                        ),# For visual clarity
                                                                        
                                                                      
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
                                                                                display_format='DD-MMM-YY'
                                                                            )],  # Data Picker
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
                                                                            display_format='DD-MMM-YY'
                                                                        ),])],id='from-to-box'),  # Data Picker
                                                                      

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
                                                                        html.Div([''],className='spacing'),
                                                                        dcc.Markdown(
                                                                            'Showing records with durations between {} - {} minutes'.format(default_duration_slider_val[0], default_duration_slider_val[1]),
                                                                            id="duration-value"
                                                                        ),

                                                                        html.H5(
                                                                            'Time of Day:'
                                                                            ),
                                                                        html.Div([''],className='spacing'),
                                                                        dcc.RangeSlider(
                                                                            id='time-slider',
                                                                            min=0,
                                                                            max=48,
                                                                            step=None,
                                                                            marks=times,
                                                                            dots=True,
                                                                            value=[0, 48],
                                                                            pushable=1

                                                                        ),  # Time Slider
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
                                                                        
                                                                        
                                                                     ],
                                                                     id='filters',lg=2,),  # Filters



                                                    dbc.Col(children=[
                                                                       

                                                                        html.Div(children=[
                                                                        html.H3('Network Plot '),
                                                                       daq.ToggleSwitch(id='toggle-network-map',value=False, size=40),
                                                                       html.H3('Map Plot')],id='plot-header'),
                                                                        html.Div([
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
                                                                        html.Div(children=[
                                                                        html.H3('Movement'),
                                                                       daq.ToggleSwitch(id='toggle-movement-time',value=False, size=40),
                                                                       html.H3('Time Series')],id='toggle-mov-div'),
                                                                        dcc.Graph(id='movement-plot'),
                                                                        dcc.Graph(id='duration-plot')],id='network-view'),
                                                                         dcc.Graph(
                                                                            id='map-plot'
                                                                        ),
                                                                     ],id='plot-area',lg=6),     # Network Plot



                                                    dbc.Col(children=[
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
                                                                            html.Div([
                                                                            html.Pre(id='click-data', ),
                                                                            ],id='click-data-cdr'),
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

                                                                            html.Pre(id='click-data-ipdr', ),

                                                                            dcc.Markdown(
                                                                            		"**The information of all the other persons who were using the same App during the constraints selected**"
                                                                            	),

                                                                            html.Pre(id='click-data-ipdr-piechart')],id='click-data-ipdr-div')


                                                                        ]),  # Click Data Container
                                                      

                                                                        html.Div([
                                                                            html.H3('Select'),
                                                                                    dcc.Markdown("""
                                                                                        Select using rectangle/lasso or by using your mouse.(Use Shift for multiple selections)
                                                                                    """),

                                                                                    html.Div(children=[
                                                                                                        html.Div([dbc.Button('Toggle',size="lg", id='toggle-components',className='buttons',n_clicks=0)],style={'textAlign':'center'}),
                                                                                                        

                                                                                                          html.Pre(id='selected-data', ),
                                                                                                      ])  
                                                                                ])
                                                                          # Selection Data Container


                                                                     ],id='stats',lg=3)

                                                 ],className='container-mid'), # End of dbc.Row(...)



                                html.Div(
                                    id='filtered-data',
                                    style={'display': 'none'}
                                        ), # Filtered Data
    
                                ]) #End of app.layout

