


# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# Import Libraries
import pandas as pd
import numpy as np
import json
import networkx as nx
import plotly.graph_objects as go
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
from stats import *
from DF import *
from BFSN import bfs
import pygraphviz as pgv
# Stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
coords_to_node={} # Dictionary that stores coordinates to node number
node_to_num={} # Dictionary that stores node number to phone number
data_columns=["Caller","Receiver","Date","Time","Duration","TowerID","IMEI"]
# Load  Data

#### Plots
# Plot Graph of calls
def plot_network(df):
    nodes=np.union1d(df['Caller'].unique(),df['Receiver'].unique())
    
    G=nx.DiGraph()
    df['Caller_node']=df['Caller'].apply(lambda x:list(nodes).index(x))
    df['Receiver_node']=df['Receiver'].apply(lambda x:list(nodes).index(x))
    def make_graph(x):
        G.add_edge(x["Caller_node"],x["Receiver_node"])
    print(len(df))
    df.apply(make_graph,axis=1)
    pos=nx.nx_agraph.graphviz_layout(G)
    
    # Add Edges to Plot
    edge_trace=[]
    def add_coords(x): 
        x0,y0=pos[x['Caller_node']]
        x1,y1=pos[x['Receiver_node']]
        coords_to_node[(x0,y0)]=x['Caller_node']
        coords_to_node[(x1,y1)]=x['Receiver_node']
        node_to_num[x['Caller_node']]=x['Caller']
        node_to_num[x['Receiver_node']]=x['Receiver']
        edge_trace.append(dict(type='scatter',
        x=[x0,x1], y=[y0,y1],
        line=dict(width=0.5, color='rgba'+str(x['Dura_color']).replace(']',')').replace('[','(')),
        hoverinfo='none',
        mode='lines'))
    df.apply(add_coords,axis=1)
    ## adding points
    node_x = []
    node_y = []
    for node in pos:
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            size=10,
            line_width=2))
    fig = go.Figure(data=edge_trace+[node_trace],
                layout=go.Layout(
                    title='<br>Phone Calls Made',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        showarrow=True,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.update_layout(transition_duration=500)
    fig.update_layout(clickmode='event+select')

    fig.update_traces(marker_size=20)
    return fig

# Create an image for the same.
# Layout of App
app.layout = html.Div(children=[
    html.H1(children='CDR Analyser'),

    html.Div(children='''
        Analyse the phone calls between people.
    '''),
    html.Div(
        id='date-selected'
    ),
    html.Div(id='message'),
    dcc.Graph(
        id='network-plot',
        figure=plot_network(df[df['Date']==df['Date'].min()].reset_index(drop=True))
    ),
    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown("""
                **Hover Data**

                Mouse over values in the graph.
            """),
            html.Pre(id='hover-data', style=styles['pre'])
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Click Data**

                Click on points in the graph.
            """),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.

                Note that if `layout.clickmode = 'event+select'`, selection data also 
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """),
            html.Pre(id='selected-data', style=styles['pre']),
        ], className='three columns')

       
    ]),
    dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=df['Date'].min(),
        max_date_allowed=df['Date'].max(),   
        initial_visible_month=dt(2020, 6, 5),
        date=str(dt(2020, 6, 5, 0, 0, 0 )) 
    ),
    dcc.Dropdown(
        id='select-caller-receiver',
        options =[{'label':'Caller','value':1}]+[{'label':'Receiver','value':2}] ,
        value='',
    ),

    dcc.Dropdown(
        id='caller-dropdown',
        options =[{'label':'None','value':''}]+ [{'label': k, 'value': k} for k in df['Caller'].unique()],
        value='',
    ),
    html.Div(
        id='filtered-data',
        style={'display': 'none'}
    ),
      dcc.Dropdown(
        id='receiver-dropdown',
        options =[{'label':'None','value':''}]+ [{'label': k, 'value': k} for k in df['Receiver'].unique()],
        value='',
    ),
    html.Label('View selected'),
    dcc.Input(
        id='selected-view',
        placeholder='Enter comma separated phone numbers',
        value='', type='text'),
])

# Callbacks
# Callback to update df used for plotting
# Callback to filter dataframe
@app.callback(
    [Output(component_id='filtered-data', component_property='children'),Output(component_id='message',component_property='children')],
    [Input(component_id='date-picker', component_property='date'),Input(component_id='select-caller-receiver',component_property='value'),Input(component_id='caller-dropdown', component_property='value'),Input(component_id='receiver-dropdown', component_property='value'),Input(component_id='selected-view', component_property='value')]
)
def update_filtered_div_caller(selected_date,selected_option,selected_caller,selected_receiver,selected_users):
    
    user_list=list(map(str.strip,list(selected_users.split(',')))) # Use this list of users to find connected component in text entry mode (TODO #4)
 
    if(selected_option==1):        
        if selected_caller!='':
            filtered_df=df[(df['Date']==pd.to_datetime(selected_date))&(df['Caller']==int(selected_caller))].reset_index(drop=True)
        else:
            filtered_df=df[df['Date']==pd.to_datetime(selected_date)]
        if filtered_df.shape[0]==0:
            # Update this 
            return dash.no_update,'Nothing Matches that Query'      
        else:
            # Update Filtered Dataframe
            return filtered_df.to_json(date_format='iso',orient='split'),'Updated'
    if(selected_option==2):        
        if selected_receiver!='':
            filtered_df=df[(df['Date']==pd.to_datetime(selected_date))&(df['Receiver']==int(selected_receiver))].reset_index(drop=True)
        else:
            filtered_df=df[df['Date']==pd.to_datetime(selected_date)]
        if filtered_df.shape[0]==0:
            # Update this 
            return dash.no_update,'Nothing Matches that Query'      
        else:
            # Update Filtered Dataframe
            return filtered_df.to_json(date_format='iso',orient='split'),'Updated'
@app.callback(
    Output('hover-data', 'children'),
    [Input('network-plot', 'hoverData')])
def display_hover_data(hoverData):
    if hoverData is not None:
        nodeNumber = coords_to_node[(hoverData['points'][0]['x'], hoverData['points'][0]['y'])]
        hd = str(node_to_num[nodeNumber]) + '\n'
        hd += "Mean Duration : " + str(meanDur(nodeNumber)) + "\n"
        hd +="Peak Hours(duration):\n"
        m = peakHours(nodeNumber)
        for x in m:
            hd+="\t\t  " + str(x)+"-"+str(x+1)+" : "+str(m[x])+"\n"
        z = ogIc(nodeNumber)
        hd += "No. of Outgoing Calls: " + str(z[0])+"\n"
        hd += "No. of Incomming Calls: " + str(z[1])+"\n"
        z = mostCalls(nodeNumber)
        hd += "Most Calls to: " + str(z[0]) + "\n"
        hd += "Most Calls from: " + str(z[1]) + "\n"
        hd += "Most Calls: " + str(z[2]) + "\n"
        return hd
    return "Hover data..."


@app.callback(
    Output('click-data', 'children'),
    [Input('network-plot', 'clickData')])
def display_click_data(clickData):
    if clickData is not None:
        nodeNumber = coords_to_node[(clickData['points'][0]['x'],clickData['points'][0]['y'])]
        return df[(df['Caller_node']==nodeNumber) |(df['Receiver_node']==nodeNumber)][data_columns].to_string(index=False)
    return "CLick on a node to view more data"
    


@app.callback(
    Output('selected-data', 'children'),
    [Input('network-plot', 'selectedData')])
def display_selected_data(selectedData):
    # TODO #3 Graph should also be filtered and only nodes in component should be displayed
    if selectedData is not None:
        l = []
        for point in selectedData['points']:
            l.append(node_to_num[coords_to_node[point['x'],point['y']]])
        components = bfs(l)
        s = ""
        i = 1
        for component in components:
            if not component:
                continue
            s += "Component "+str(i)+":\n"
            i+=1
            for number in component:
                s+= "\t" + str(number) + "\n"
        return s
    return json.dumps(selectedData, indent=2)


# Callback to update network plot
@app.callback(
    Output(component_id='network-plot',component_property='figure'),
    [Input(component_id='filtered-data',component_property='children')]
)
def update_network_plot_caller(filtered_data):
    return plot_network(pd.read_json(filtered_data, orient='split'))

# Callback to change selectors including caller no. according to date
@app.callback(
    Output(component_id='caller-dropdown',component_property='options'),
    [Input(component_id='date-picker', component_property='date')]
)
def update_phone_div_caller(selected_date):
    return [{'label':'None','value':''}]+[{'label': k, 'value': k} for k in df[df['Date']==pd.to_datetime(selected_date)]['Caller'].unique()]


@app.callback(
    Output(component_id='receiver-dropdown',component_property='options'),
    [Input(component_id='date-picker', component_property='date')]
)
def update_phone_div_receiver(selected_date):
    return [{'label':'None','value':''}]+[{'label': k, 'value': k} for k in df[df['Date']==pd.to_datetime(selected_date)]['Receiver'].unique()]


# Run Server
if __name__ == '__main__':
    app.run_server(debug=True,port=8000)

