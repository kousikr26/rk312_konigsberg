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
from stats import *
import pygraphviz as pgv
import dash_bootstrap_components as dbc
import math
import matplotlib
import requests
import dash_draggable
from math import radians, sin, sqrt, cos, atan2
########################################################## Import functions for Breadth First Search ##########################
from addEdge import addEdge,addEdgemap
from BFSN import bfs



########################################################## Stylesheet ##########################################################
external_stylesheets = [dbc.themes.SANDSTONE]


# Load  Data
df = pd.read_csv('./data/final_data.csv')
#df2 = pd.read_csv('./data/ipdr_data.csv')
towers=pd.read_csv('./data/towers_min.csv') #Data for Cell Towers
tower_mean=df.groupby(['TowerID'])['Duration'].mean()
tower_std=df.groupby(['TowerID'])['Duration'].std()
#### Create App ###
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'CDR/IPDR Analyser'




# 3. Setting Default Variables for various Filters ####
default_duration_slider_val = [0, 100]
default_time_slider_val = [0,48]
default_caller_receiver_val = 3
date_format='%d-%m-%Y'




# 4. Miscellaneous variables 
## 4.1. Slider Markers and Loop to generate marks for Time
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

## 4.2. Generating marks for duration slider
durations = {}
for i in range(0, int(df['Duration'].max()), 10):
    durations[i] = str(i)

## 4.3. Color Map for Edges based on Duration of call (see Section 7.3.)
cmap = cm.get_cmap('coolwarm')



# 5. Variables for Graph Functions
coords_to_node = {}  # Dictionary that stores coordinates to node number
node_to_num = {}  # Dictionary that stores node number to phone number
num_to_node = {}  #Dictionary that stores numbers to node
data_columns = ["Caller", "Receiver", "Date",
                "Time", "Duration", "TowerID", "IMEI"]

data_columns_ipdr = ["Caller","App_name","Private IP","Private Port", "Public IP", "Public Port", "Dest IP","DEST PORT", "MSISDN", "IMSI", "Date","Time",\
    "Duration", "TowerID", "Uplink Volume","Downlink Volume","Total Volume","I_RATTYPE"]


ports_to_apps = {'DEST PORT':'App','0':'nan','5223':'WhatsApp','5228':'WhatsApp', '4244':'WhatsApp', '5222':'WhatsApp', '5242':'WhatsApp','443_':'Skype','443':'SSL',\
    '3478-3481':'Skype','49152-65535':'Skype','80':'Web connection','8080':'Web Connection', \
        '8081': 'Web Connection', '993':'IMAP', '143':'IMAP', '8024':'iTunes', '8027':'iTunes', '8013':'iTunes', \
            '8017':'iTunes', '8003':'iTunes', '7275':'iTunes', '8025':'iTunes', '8009':'iTunes',\
                '58128': 'Xsan', '51637':'Xsan', '61076':'Xsan','40020':'Microsoft Online Games', '40017':'Microsoft Various Games', \
                    '40023':'Microsoft Online Games',\
                    '40019':'Microsoft Online Games', '40001':'Microsoft Online Games', '40004':'Microsoft Online Games', \
                        '40034':'Microsoft Online Games', '40031':'Microsoft Online Games', '40029':'Microsoft Online Games',\
                              '40005':'Microsoft Online Games', '40026': 'Microsoft Online Games', '40008': 'Microsoft Online Games',\
                                  '40032':'Microsoft Online Games'}   # did not took '443':'SSL, Web connection' to avoid double 443.




# 6. Function to set color scale of edges
viridis = cm.get_cmap('viridis', 12)

def preprocess_data(df):
    # nodes
    l=df['Receiver'].unique()
    l=l[l!=20000] # to remove occurrences of 20000
    nodes = np.union1d(df['Caller'].unique(),l )
    # Define Color
    df['Dura_color'] = (df['Duration']/df['Duration'].max()).apply(viridis)
    
    df['Date'] = df['Date'].apply(lambda x: pd.to_datetime(x,format=date_format)).dt.date


    df['Caller_node'] = df['Caller'].apply(
        lambda x: list(nodes).index(x))  # Caller Nodes
    
#    df['Receiver_node'] = df['Receiver'].apply(lambda x: list(nodes).index(x))
    df['Receiver_node'] = df['Receiver'].apply(lambda x: list(nodes).index(x) if x!=20000 else -1)

    df['IMEI_node'] = df['Caller'].apply(lambda x: list(nodes).index(x) if x!=20000 else -1)
    df['App_name'] = df['DEST PORT'].apply(lambda x:ports_to_apps[str(x)] if (ports_to_apps[str(x)]!='nan') else None)

    coords_to_node.clear()
    num_to_node.clear()
    node_to_num.clear()



preprocess_data(df)


#### Plots ####
# Plot Graph of calls

# 7. Main Plot Functions 
fig = go.Figure() # Defining the main figure
pos = {}

## 7.1. Returns the figure for geographical map from input Dataframe.
def plot_map(filtered_df):

    new_df=pd.merge(filtered_df,towers[['lat','lon','TowerID']],on='TowerID')
    towers_deviation=new_df.groupby(['TowerID'])[['Duration']].apply(lambda x : (x.mean()-tower_mean[x.name])/tower_std[x.name] ).reset_index()
    towers_deviation['Duration']=towers_deviation['Duration'].apply(lambda x : max(x,0))
    node_x=towers_deviation['TowerID'].apply(lambda x : towers[towers['TowerID']==x]['lat'].unique()[0])
    node_y=towers_deviation['TowerID'].apply(lambda x : towers[towers['TowerID']==x]['lon'].unique()[0])
    people=dict(type='scattermapbox',lat=node_x,lon=node_y,mode='markers',marker=go.scattermapbox.Marker( size=30*pow(0.3,towers_deviation['Duration'])))
    fig=go.Figure(people,layout={
        'mapbox_style':'open-street-map',
        'margin': dict(l = 0, r = 0, t = 0, b = 0),
        'height':500,
        'mapbox':dict(
        
            bearing=0,
            center=dict(
                lat=23.2599,
                lon=77.4126
            ),
            pitch=0,
            zoom=10
        )}
        
    )

    return fig


#Plot trace
def plot_movement(df,selected_numbers):
    data=[]
    colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
    color_no=0
    df=pd.merge(df,towers[['lat','lon','TowerID']],on='TowerID')
    for number in selected_numbers:
        
        df['Date']=pd.to_datetime(df['Date'],format='%d-%m-%Y')
        #df=df[df['Date'].isin(pd.date_range('2020/06/05','2020/06/06'))].sort_values(['Date','Time']).reset_index()

        
        filtered_df=df[df['Caller']==number].sort_values(['Date','Time']).reset_index()
        all_lat=[]
        all_lon=[]
        locs=[]
        duration_hover=[]
        duration_output=[]

        l1 = filtered_df['Date'].dt.date.apply(str) + ' '+ filtered_df['Time'].apply(str)
        for i in range(len(l1)):
            l1[i] =pd.to_datetime(l1[i],format='%Y-%m-%d %H:%M:%S')

        for i in range(len(l1)-1):
            x=l1[i+1]-l1[i]
            duration_hover.append(x)

        
        dura_op=[]  # Will hold str(transitduration) to be hovered per edge
        for i in range(len(duration_output)):
            dura_op.append(str(duration_output[i]))
        
            
        for (index,row) in filtered_df.iterrows():
            locs.append([row['lat'],row['lon']])

        for i in range(len(locs)-1):
            all_lat,all_lon,duration_output=addEdgemap(locs[i],locs[i+1],duration_hover[i],all_lat,all_lon,duration_output, 0.7, "end",0.009, 30, 10) 
            data.append(go.Scattermapbox(lat=all_lat,lon=all_lon,mode = "lines",hovertext=duration_output,marker=go.scattermapbox.Marker(
                    size=17,
                    color=colors[color_no],
                    opacity=1
                ),
            ))
        color_no+=1
        color_no%=len(colors)
    fig=go.Figure(data,layout={
        'mapbox_style':'open-street-map',
        'showlegend':False,
        'margin': dict(l = 0, r = 0, t = 0, b = 0),
        'mapbox':dict(
        
            bearing=0,
            center=dict(
                lat=23.2599,
                lon=77.4126
            ),
            pitch=0,
            zoom=10
        )
    
    })
    return fig

## 7.2. Main function to get the Figure for the Graph of Calls.
# Plot Graph of calls
def plot_network(df, srs, scs):

    G = nx.DiGraph()  # networkX Graph

    # Reciever Nodes
    df=df[df['Receiver_node']!=-1]
    def make_graph(x):
            G.add_edge(x["Caller_node"], x["Receiver_node"])

    df.apply(make_graph, axis=1)  # Make a graph
    pos = nx.nx_agraph.pygraphviz_layout(G)  # Position of Points

    edge_trace = [] # Add Edges to Plot

## 7.3. Adds the caller and reciever edge information to each entry. 
    def add_coords(x):
        x0, y0 = pos[x['Caller_node']]
        x1, y1 = pos[x['Receiver_node']]

        node_to_num[x['Caller_node']] = x['Caller']
        node_to_num[x['Receiver_node']] = x['Receiver']
        num_to_node[x['Caller']] = x['Caller_node']
        num_to_node[x['Receiver']] = x['Receiver_node']
        edges_x,edges_y=addEdge([x0,y0],[x1,y1],[],[], 0.6, 'end', 20, 30, 15)
        
        ### 7.3.1. cmap returns the rgba color for the input number in (0.0,1.0)
        norm_x = x["Duration"]/df["Duration"].max()
        rgba = cmap(norm_x)


        edge_trace.append(dict(type='scatter',
                               x=edges_x, y=edges_y,
                               showlegend=False,
                               line=dict(
                                   width=3, color='rgba'+str(rgba)),
                               hoverinfo='none',
                               mode='lines',
        ))  # Graph object for each connection
       
    df.apply(add_coords, axis=1)  # Adding edges


## 7.4. Adds the caller and reciever node information.

    # adding points
    node_x = []
    node_y = []
    total_duration = []
    hover_list = []
    for node in pos:
        x, y = pos[node]
        coords_to_node[(x, y)] = node
        hover_list.append(str(node_to_num[node]))
        node_x.append(x)
        node_y.append(y)
        total_duration.append(27*pow((df[(df['Caller_node']==node)|(df['Receiver_node']==node)]['Duration'].sum())/df['Duration'].max(),0.3))
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hovertext = hover_list,
        hoverinfo='text',
        showlegend=False,
        marker=dict(
            size=total_duration,
            showscale=True,
            line_width=2,
            line_color='black'))  # Nodes visual design info.

## 7.5. The main figure for both the edges and nodes data.
    fig = go.Figure(data=edge_trace+[node_trace],
                    layout=go.Layout(
                   
                    titlefont_size=16,
                 

                    hovermode='closest',
                    margin=dict(b=20, l=0, r=0, t=20),
                    annotations=[dict(
                        showarrow=True,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002)],
                    xaxis=dict(showgrid=False, zeroline=False,
                               showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )  # Complete Figure
    fig.update_layout(transition_duration=500)  # Transition animation dynamics.

    fig.update_layout(
         hoverlabel = dict(bgcolor='white',font_size = 15,font_family = 'Rockwell'),
          #Hover-info design.
    )
    fig.update_layout(clickmode='event+select')  # Event method
    fig.update_layout(yaxis = dict(scaleanchor = "x", scaleratio = 1), plot_bgcolor='rgb(255,255,255)')
    fig.update_layout(height=500)
    return fig




# 8. The HTML Layout of the App.

# NOTE : All the elements here (visual or statistical) are updated through callbacks as defined in section 9
app.layout = html.Div(children=[
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
                                                    html.I('Welcome back officer, You can analyse the phone calls and internet activity of people'),  # Subtitle
                                                  
                                                    html.H4(id='message')],id='header-subtitle'),  # Message
                                                  ],id='header-text'),



                                dbc.Row(children=[

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
                                                                     id='filters',lg=2,)
                                                                     ])]),  # Filters
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

                                                    dbc.Col(children=[
                                                                       
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
                                                                        html.H3('Network Plot '),
                                                                       daq.ToggleSwitch(id='toggle-network-map',value=False, size=40),
                                                                       html.H3('Map Plot')],id='plot-header')])]),
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
                                                                        html.H3('Movement'),
                                                                       daq.ToggleSwitch(id='toggle-movement-time',value=False, size=40),
                                                                       html.H3('Time Series')],id='toggle-mov-div'),
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


                                                                     ],id='plot-area',lg=12),
                                                                     ])]),     # Network Plot
                                                        
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
                                                                                                        html.Div([dbc.Button(children=[
                                                                                                            html.Img(src='assets/vision.png',height='24px')
                                                                                                        ],size="lg", id='toggle-components',className='buttons',n_clicks=0)],style={'textAlign':'center'}),
                                                                                                        

                                                                                                          html.Pre(id='selected-data', ),
                                                                                                      ])  
                                                                                ])
                                                                          # Selection Data Container


                                                                     ],id='stats',lg=3)
                                                                                            ])])

                                                 ],className='container-mid'), # End of dbc.Row(...)



                                html.Div(
                                    id='filtered-data',
                                    style={'display': 'none'}
                                        ), # Filtered Data
    
                                ]) #End of app.layout




# 9. Callbacks to process the dataframe according to Filters

## NOTE:  REMEMBER WHILE EDITING (RWI): THIS IS A TWO OUTPUT FUNCTION


sel_lat = 0
sel_lon = 0
## 9.1. TO UPDATE THE DataFrame BASED ON ALL FILTER VALUES.
@app.callback(
    [Output(component_id='filtered-data', component_property='children'),
     Output(component_id='message', component_property='children')],
    [Input('radius-slider', 'value'),Input('upload-data', 'contents'),Input(component_id='date-picker1', component_property='date'),Input(component_id='date-picker2', component_property='date'), Input(component_id='duration-slider', component_property='value'), Input(component_id='time-slider', component_property='value'),
     Input(component_id='select-caller-receiver', component_property='value'), Input(component_id='caller-dropdown', component_property='value'), Input(component_id='receiver-dropdown', component_property='value')]
)
def update_filtered_div_caller(radius,contents, selected_date1, selected_date2, selected_duration, selected_time, selected_option, selected_caller, selected_receiver):
    # Date,Time,Duration Filter
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        global df
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        preprocess_data(df)

    filtered_df = df[(df['Date'] >= pd.to_datetime(selected_date1)) & (df['Date'] <= pd.to_datetime(selected_date2))
                     & ((df['Duration'] >= selected_duration[0]) & (df['Duration'] <= selected_duration[1]))
                     & ((df['Time'] < times[selected_time[1]]['label']) & (df['Time'] >= times[selected_time[0]]['label']))].reset_index(drop=True)
    def chk(lat1,lon1,radius):
        R = 6373.0
        global sel_lat
        global sel_lon
        lat2 = sel_lat
        lon2 = sel_lon

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        print(distance)
        if distance > radius:
            return False
        return True

    if radius != 0:
        towers_c = towers.copy()
        ver = towers_c.apply(lambda x: chk(x['lat'],x['lon'],radius), axis=1)
        towers_req = towers_c[ver]['TowerID'].unique()
        filtered_df = filtered_df[filtered_df['TowerID'].isin(towers_req)]

    # Number Filter
    # If Caller is Selected
    if(selected_option == 1):
        if selected_caller != 'None':
            filtered_df = filtered_df[(filtered_df['Caller'].isin(
                list(selected_caller)))].reset_index(drop=True)

   # If Receiver is selected
    if(selected_option == 2):
        if selected_receiver != 'None':
            filtered_df = filtered_df[(filtered_df['Receiver'].isin(
                (selected_receiver)))].reset_index(drop=True)
   # If the option either is selected
    if(selected_option == 3):
        if selected_caller != 'None' or selected_receiver != 'None':
            filtered_df = filtered_df[((filtered_df['Caller'].isin(list(selected_caller))) | (
                filtered_df['Receiver'].isin(list(selected_receiver))))].reset_index(drop=True)
    # If option both is selected
    if(selected_option == 4):
        if selected_caller != 'None' and selected_receiver != 'None':
            filtered_df = df[((filtered_df['Caller'].isin(list(selected_caller))) & (
                filtered_df['Receiver'].isin(list(selected_receiver))))].reset_index(drop=True)
    if filtered_df.shape[0] == 0:
        # No update since nothing matches
        return dash.no_update, 'Nothing Matches that Query'
    else:
        # Update Filtered Dataframe
        return filtered_df.to_json(date_format='iso', orient='split'), 'Updated'



## 9.2. TO UPDATE THE HOVER DATA OF THE SELECTED NODE.
@app.callback(
    Output('hover-data', 'children'),
    [Input('network-plot', 'hoverData'), Input(component_id='filtered-data', component_property='children'),Input(component_id='map-plot',component_property='hoverData')])
def display_hover_data(hoverData, filtered_data,hoverDataMap):

    df = pd.read_json(filtered_data, orient='split')
    if hoverData is not None and 'marker.size' in hoverData['points'][0]:
        # Get node number corresponding to the point.
        nodeNumber = coords_to_node[(
            hoverData['points'][0]['x'], hoverData['points'][0]['y'])]
        hd = 'Selected Number: ' + \
            str(node_to_num[nodeNumber]) + '\n'  # hd: Hover Data string

        # Functions are from stats.py
        hd += "Mean Duration : " + str(meanDur(nodeNumber, df)) + "\n"
        hd += "Peak Hours(duration):\n"
        m = peakHours(nodeNumber, df)
        for x in m:
            hd += "\t\t  " + str(x)+"-"+str(x+1)+" : "+str(m[x])+"\n"
        z = ogIc(nodeNumber, df)  # Outgoing Incoming
        hd += "No. of Outgoing Calls: " + str(z[0])+"\n"
        hd += "No. of Incomming Calls: " + str(z[1])+"\n"
        z = mostCalls(nodeNumber, df)  # Most Calls
        hd += "Most Calls to: " + str(z[0]) + "\n"
        hd += "Most Calls from: " + str(z[1]) + "\n"
        hd += "Most Calls: " + str(z[2]) + "\n"
        return hd
        
    if hoverDataMap is not None:
    
        cur_lat,cur_lon=hoverDataMap['points'][0]['lat'],hoverDataMap['points'][0]['lon']
        req_json = requests.get('https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'.format(
                lat=cur_lat, lon=cur_lon)).json()
        add_string = ""
        add_string +=" ,".join(req_json['address'].values())
        return add_string
    return "Hover data..."



## 9.3. TO UPDATE THE DURATION PLOT AND IPDR USAGE PIE-CHART FOR A NODE.
@app.callback(
    [Output('display-selected-num','children'),Output('click-data', 'children'), Output('pie-chart','figure'), Output('click-data-ipdr', 'children'), Output('duration-plot','figure')], #Suggest to put all extra plots in this callback's output...
    [Input('network-plot', 'clickData'), Input(component_id='filtered-data', component_property='children')])
def display_click_data(clickData,filtered_data):
    emptyPlot= go.Figure()
    emptyPlot.update_layout(
    showlegend=False,
    annotations=[
        dict(
            x=3,
            y=1.5,
            xref="x",
            yref="y",
            text="Click a point to get started",
            showarrow=False

        )
    ],
    margin= dict(l = 0, r = 0, t = 0, b = 0),
    height=200,
)
    df = pd.read_json(filtered_data, orient='split')
    if clickData is not None and 'marker.size' in clickData['points'][0]:
        nodeNumber = coords_to_node[(
            clickData['points'][0]['x'], clickData['points'][0]['y'])]
        groups=df[df['IMEI_node']==nodeNumber].groupby('App_name')['Caller'].count()
    
        fig = go.Figure(data=dict(type='pie',values=groups,labels=groups.index))
        fig.update_layout(showlegend=False)
        fig.update_layout(margin= dict(l = 0, r = 0, t = 0, b = 0),height=200)
  
        # Filtering DF
        new_df = df[((df['Receiver_node'] !=-1)&(df['Caller_node'] == nodeNumber) | (df['Receiver_node'] == nodeNumber))][data_columns]
        
        x=df[(df['Caller_node'] == nodeNumber)]['Caller'].unique()
        if x.shape[0]>0:
            x=x[0]
        else: 
            x='No Points'
        new_df_ipdr = df[(df['Caller_node'] == nodeNumber)][data_columns_ipdr]

        new_df_ipdr=new_df_ipdr[new_df_ipdr['App_name'].notna()]

        return str(x),new_df.to_string(index=False), fig,new_df_ipdr.to_string(index=False), plot_Duration(new_df)
    return 'None',"Click on points in the graph to get the call data records.\n\n",emptyPlot,"Click on points in the graph to get the internet data records.\n\n" , emptyPlot #DO NOT RETURN HERE 'None', otherwise duration-plot will always be empty.



@app.callback(
	[Output('click-data-ipdr-piechart', 'children')],
	[Input('pie-chart', 'clickData'), Input('filtered-data', 'children')]
	)
def update_ipdr_simult_users(clickData, filtered_data):

	if clickData is not None:

		df = pd.read_json(filtered_data, orient='split')
		new_df = df[df['App_name'] == clickData['points'][0]['label']].drop(['Unnamed: 0', 'Dura_color', 'Caller_node', 'Receiver_node'], axis=1)

		return new_df.to_string(index=False),
	return "Click on a field in pie-chart to see data",



#Callback to output the new figure for Duration plot of selected node.
def plot_Duration(new_df):

    if new_df is not None:

        x = sorted(new_df["Date"])
        y = new_df["Duration"]
        fig = go.Figure([ go.Bar(x = x, y = y,
                              
                                name='duration-plot') ]) 
        fig.update_layout(margin= dict(l = 0, r = 0, t = 0, b = 0),height=400) 
        return fig
    else:
        return None



## 9.4. TO UPDTAE THE COMPONENT LIST FOR THE SELECTED DATA
l = []
@app.callback(
    [Output('selected-data', 'children'),Output('movement-plot','figure')],
    [Input('network-plot', 'selectedData'), Input(component_id='filtered-data', component_property='children')])
def display_selected_data(selectedData, filtered_data):
    df = pd.read_json(filtered_data, orient='split')
    # TODO #3 Graph should also be filtered and only nodes in component should be displayed
    if selectedData is not None:
        l = []
        for point in selectedData['points']:
            l.append(node_to_num[coords_to_node[point['x'], point['y']]])
        components = bfs(l, df[df['Receiver']!=20000].reset_index(drop=True))
        s = ""
        i = 1
        for component in components:
            if not component:
                continue
            s += "Component "+str(i)+":\n"
            i += 1
            for number in component:
                s += "\t" + str(number) + "\n"
        return s,plot_movement(df,l)

    return json.dumps(selectedData, indent=2),go.Figure(layout=dict(margin= dict(l = 0, r = 0, t = 0, b = 0)))



## 9.5. TO UPDATE THE RECEIVER-DROPDOWN IN MAP MODE.
@app.callback(
    Output(component_id='receiver-dropdown', component_property='value'), [Input('toggle-components', 'n_clicks')]
)
def update_receiver_value(n_clicks):
    if n_clicks%2 == 1:
        k = []
        global l
        for x in l:
            k.append(x)
        return k
    else:
        return 'None'



## 9.6. TO UPDATE THE CALLER-DROPDOWN IN MAP MODE.         
@app.callback(
    Output(component_id='caller-dropdown', component_property='value'), [Input('toggle-components', 'n_clicks')]
)
def update_caller_value(n_clicks):
    if n_clicks%2 == 1:
        k = []
        global l
        for x in l:
            k.append(x)
        return k
    else:
        return 'None'



## 9.7. TO UPDATE THE MAIN PLOT w.r.t. SELECTED RECEIVERS & CALLERS. 
@app.callback(
    Output(component_id='network-plot', component_property='figure'),
    [Input(component_id='collapse-filters', component_property='n_clicks'),Input(component_id='filtered-data', component_property='children'), Input(component_id='receiver-dropdown', component_property='value'), Input(component_id='caller-dropdown', component_property='value')]
)
def update_network_plot_caller(n_clicks,filtered_data, srs, scs):
    # if zoom == True and fig['layout']['height'] != 850:
    #     fig['layout']['height']=850
    #     fig['layout']['width']=850
    #     return fig
    # if zoom == False and fig['layout']['height'] != 500:
    #     fig['layout']['height']=500
    #     fig['layout']['width']=500
    #     return fig
    fig = plot_network(pd.read_json(filtered_data, orient='split'), srs, scs)
    if n_clicks!= None and n_clicks%2==1:
        fig.update_layout(height=500)
    
    return fig



## 9.7. TO UPDATE THE MAIN PLOT AFTER FILTERING THE DATA FROM 9.1.
# Callback to update map plot
@app.callback(
    Output(component_id='map-plot',component_property='figure'),
    [Input(component_id='filtered-data', component_property='children')]

)
def update_map_plot_callback(filtered_data):
    return plot_map(pd.read_json(filtered_data, orient='split'))



## 9.8. TO TOGGLE BETWEEN MAP OR NETWORK PLOT
@app.callback(
    [Output(component_id='network-view',component_property='style'),Output(component_id='map-plot',component_property='style')],
    [Input(component_id='toggle-network-map',component_property='value')]
)
def toggle_network_map(toggle):
    if toggle:
        return {'display':'none'},{'display': 'block'}
    else:
        return {'display': 'block'},{'display':'none'}

## 9.0. TO TOGGLE BETWEEN Time Series OR Movement PLOT
@app.callback(
    [Output(component_id='movement-plot',component_property='style'),Output(component_id='duration-plot',component_property='style')],
    [Input(component_id='toggle-movement-time',component_property='value')]
)
def toggle_movement_time(toggle):
    if toggle:
        return {'display':'none'},{'display': 'block'}
    else:
        return {'display': 'block'},{'display':'none'}
@app.callback(
    [Output(component_id='click-data-cdr',component_property='style'),Output(component_id='click-data-ipdr-div',component_property='style')],
    [Input(component_id='toggle-cdr-ipdr',component_property='value')]
)
def toggle_cdr_ipdr(toggle):
    if toggle:
        return {'display':'none'},{'display': 'block'}
    else:
        return {'display': 'block'},{'display':'none'}
## 9.10. TO CHANGE THE AVAILABLE ENTRIES IN CALLER-DROPDOWN MENU ACCORDING TO THE DATE RANGE SELECTED.
@app.callback(
    Output(component_id='caller-dropdown', component_property='options'),
    [Input(component_id='date-picker1', component_property='date'),Input(component_id='date-picker2', component_property='date')]
)
def update_phone_div_caller(selected_date1, selected_date2):
    return [{'label': 'None', 'value': ''}]+[{'label': k, 'value': k} for k in df[(df['Date'] >= pd.to_datetime(selected_date1)) & (df['Date']<=pd.to_datetime(selected_date2))]['Caller'].unique()]



## 9.11. TO CHANGE THE AVAILABLE ENTRIES IN RECEIVER-DROPDOWN MENU ACCORDING TO THE DATE RANGE SELECTED.
@app.callback(
    Output(component_id='receiver-dropdown', component_property='options'),
    [Input(component_id='date-picker1', component_property='date'),Input(component_id='date-picker2', component_property='date')]
)
def update_phone_div_receiver1(selected_date1, selected_date2):
    return [{'label': 'None', 'value': ''}]+[{'label': k, 'value': k} for k in df[(df['Date'] >= pd.to_datetime(selected_date1)) & (df['Date']<=pd.to_datetime(selected_date2))]['Receiver'].unique()]



## 9.12. TO UPDATE THE TEXT ON TIME AND DURATION SLIDERS
@app.callback(
    Output('duration-value', 'children'),
    [Input('duration-slider', 'value')]
    )
def update__selected_duration_text(value):
    return  'Showing records with durations between {} - {} minutes'.format(value[0], value[1]),


## 9.13. TO RESET ALL FILTERS (except condition, caller and reciever drop-down menus)
@app.callback(
    [Output('date-picker1', 'date'), Output('date-picker2', 'date'), Output('duration-slider', 'value'), Output('time-slider', 'value'), Output('select-caller-receiver', 'value')],
    [Input('reset-button', 'n_clicks')]
    )
def ResetFilters(button_reset):
    return str(dt(2020, 6, 17, 0, 0, 0)), str(dt(2020, 6, 17, 0, 0, 0)), default_duration_slider_val, default_time_slider_val, default_caller_receiver_val


@app.callback(
    [Output(component_id='plot-area', component_property='lg'),
     Output(component_id='filters', component_property='style')],
    [Input('collapse-filters', 'n_clicks')]
)
def Zoom(mode):
    if mode!=None and mode%2==1 :
        return 12, {'display':'none'}
    else:
        return 12, {'display':'block'}

@app.callback(
    Output('radius-div', 'style'),
    [Input('map-plot', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return {'display': 'none'}
    else:
        global sel_lon, sel_lat
        sel_lat = float(clickData['points'][0]['lat'])
        sel_lon = float(clickData['points'][0]['lon'])
        return {'display': 'block'}
########################################################## Run Server ##########################################################
server=app.server
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')