import time

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from flask import Flask, render_template
from flask_caching import Cache

app = Flask(__name__)

# setting up page 1
my_dashboard = dash.Dash(__name__, server=app, url_base_pathname='/home/')
my_dashboard.title = 'Dashboard'

# flask cache properties
cache_data = Cache(my_dashboard.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

my_dashboard.layout = html.Div([
    html.Div([
        html.Div([
            html.A(children='Gauge', href='/gauge'),
            html.Br(),
            html.A(children='Static HTML Test Page', href='/test'),
            html.Div([
                html.P("Class:"),
                dcc.Dropdown(
                    id='class',
                    options=[{'label': c.upper(), 'value': c} for c in ["c1", "c2"]],
                    value='c1',
                    clearable=False,
                    style={'width': '200px', 'display': 'inline-block', 'color': '#000'}
                )], style={'margin-top': '10px'}),
            html.Div([
                html.P("Subject:"),
                dcc.Dropdown(
                    id='subject',
                    options=[{'label': c.capitalize(), 'value': c} for c in ["s1", "s2"]],
                    value='s1',
                    clearable=False,
                    style={'width': '200px', 'display': 'inline-block', 'color': '#000'}
                )], style={'margin-top': '10px'}),
            html.Div([dcc.Loading(
                id="loading",
                children=[
                    html.Div([
                        dcc.Graph(id="my-graph", style={'margin-top': '20px'})
                    ], style={'position': 'relative', 'float': 'left', 'margin-top': '20px', 'margin-left': '10px',
                              'width': '1050px'}),
                ], style={'position': 'relative', 'float': 'left', 'margin-top': '20px'}),
            ])
        ], style={'width': '100%', 'position': 'relative', 'float': 'left', 'display': 'inline-block',
                  'margin-left': '50px',
                  'margin-top': '125px'}),
    ])
])


def loading(value):
    time.sleep(0)
    return value


# Cache data to local with a timeout
@cache_data.memoize(timeout=60)
def get_data(class_name, subject_name):
    data = pd.read_csv('sample_data.csv')
    data = data[(data.class_name == class_name) & (data.subject_name == subject_name)]
    return data


# callback for the chart filters
# input - filters
# output - chart with updated data
@my_dashboard.callback(
    Output('my-graph', 'figure'),
    [Input("class", "value")],
    [Input("subject", "value")],
    [Input("loading", "value")]
)
def update_sentiment_line_chart(class_name, subject_name, loading):
    df = get_data(class_name, subject_name)
    fig = px.bar(df, x='name', y='marks')
    return fig


# Setting up Page 2 - Gauge
my_dashboard2 = dash.Dash(__name__, server=app, url_base_pathname='/gauge/')
my_dashboard2.title = 'Dashboard 2'

my_dashboard2.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Graph(
        id='life-exp-vs-gdp'
    )
])

my_dashboard2.layout = html.Div([
    html.A(children='Back <-', href='/home'),
    html.Br(),
    dcc.Location(id='url', refresh=False),
    dcc.Graph(
        id='life-exp-vs-gdp',
        style={'width': '500px'}
    )
])


@my_dashboard2.callback(Output('life-exp-vs-gdp', 'figure'), Input('url', 'pathname'))
def display_page(pathname):
    print(pathname)
    pathname = pathname.strip('/gauge/')
    if pathname == '':
        pathname = 200
    else:
        pathname = int(pathname.strip('/'))

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pathname,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Speed"}))
    return fig


# page 1
@app.route("/")
@app.route("/home")
def home():
    return my_dashboard.index()


# page 2
@app.route("/gauge")
def gauge():
    return my_dashboard2.index()


# page 3
@app.route("/test")
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
