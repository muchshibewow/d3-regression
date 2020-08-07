import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import json
import psycopg2
import pandas.io.sql as psql
import numpy as np

connection_parameters = {
    'host':'10.2.2.150',
    'port':5432,
    'dbname':'deft-postgres',
    'user':'d3regression',
    'password':'d3regression'
}

conn = psycopg2.connect(
    host=connection_parameters['host'],
    port=connection_parameters['port'],
    dbname=connection_parameters['dbname'],
    user=connection_parameters['user'],
    password=connection_parameters['password']
    )

with open(r'turkeydata.json', encoding='utf-8') as f:
    turkey_city = json.load(f)

city_id_map = {}
for feature in turkey_city['features']:
    feature['id'] = feature['properties']['number']
    city_id_map[feature['properties']['name']] = feature['id']

# to check the violation
cityInGeoJson=[]
for feature in turkey_city['features']:
    cityInGeoJson.append(feature['properties']['name'])
cityInTrainDataSet = data['City'].tolist()

violation = np.setdiff1d(cityInTrainDataSet,cityInGeoJson)

dataset= data.iloc[:, [1,2,4,42]]
dm = dataset[~dataset.City.isin(violation)]
df= dm.groupby(['City'])['revenue'].mean().reset_index()
df['id']=df['City'].apply(lambda x:city_id_map[x])

m= data.iloc[:, [1,2,4,42]]
df1= m.groupby(['City','Type'])['revenue'].mean().reset_index()

fig1 = px.choropleth(df, locations='id', geojson=turkey_city, color='revenue',scope='asia',hover_data=['revenue'],hover_name='City',color_continuous_scale=px.colors.diverging.RdYlGn,color_continuous_midpoint=4470000,width=None, height=650)
fig1.update_geos(fitbounds='locations', visible=False)
df2 = df1.sort_values(by=['revenue'], ascending=False)
fig = px.bar(df2, x='City', y='revenue')
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
sidebar = html.Div(
    [
        html.H2("Revenue Prediction", className="display-4"),
        html.Hr(),
        html.P(
            "This model is build to help revenue prediction for cities", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Map", href="/Map", id="Map-link"),
                dbc.NavLink("Graph", href="/Graph", id="Graph-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)
content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 3)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False
    return [pathname == f"/page-{i}" for i in range(1, 3)]

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/Map"]:
        return html.Div([
                # adding a header and a paragraph
                html.Div([
                    html.H1("Predicted revenue distribution across states")
                         ]),
# adding a plot        
                dcc.Graph(id = 'mapping', figure = fig1)
                         ])
    elif pathname == "/Graph":
        return html.Div([html.H1("Cities with highest revenue prediction"),
           dcc.Dropdown(
        id='dropdown',
        options=[
{'label': i, 'value': i} for i in df2.Type.unique()
],
        value='FC'
    ),dcc.Graph(
        id='example-graph',
        #figure=fig
                         )])
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    
    )
@app.callback(
 dash.dependencies.Output('example-graph','figure'),
  [dash.dependencies.Input("dropdown","value")])
def update_graph(value1):
    #return {html.P("Hi")}
    return fun2(value1)
def fun2(value1):
    if value1=='FC':
        dff=df1[df1['Type']==value1].sort_values(by=['revenue'], ascending=False)[:5]
        fig = px.bar(dff, x='City', y='revenue')
        return fig
    elif value1=='IL':
        dff=df1[df1['Type']==value1].sort_values(by=['revenue'], ascending=False)[:5]
        fig = px.bar(dff, x='City', y='revenue')
        return fig
    elif value1=='DT':
        dff=df1[df1['Type']==value1].sort_values(by=['revenue'], ascending=False)[:5]
        fig = px.bar(dff, x='City', y='revenue')
        return fig
    elif value1=='MB':
        dff=df1[df1['Type']==value1].sort_values(by=['revenue'], ascending=False)[:5]
        fig = px.bar(dff, x='City', y='revenue')
        return fig

if __name__ == "__main__":
    app.run_server(debug=False, port = 8080)
