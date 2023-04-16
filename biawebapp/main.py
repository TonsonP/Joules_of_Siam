import dash
from dash import html, dcc,Output, Input
import flask
import plotly.express as px
import pandas as pd
import pickle
from flask import Flask,render_template, redirect, url_for, flash,request,send_from_directory
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor

# import flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

server = flask.Flask(__name__)


file = open('dataP/Actual_values.pkl', 'rb')
actial_values = pickle.load(file)
test2 = pd.read_csv('dataP/allmodelpredictedsaved.csv')

@server.route("/")
def home():
    return render_template('index.html')
    return "Hello, Flask!"

@server.route('/render_dashboard')
def render_dashboard():
    return flask.redirect('/app1')

@server.route('/render_dashboard2')
def render_dashboard2():
    return flask.redirect('/app2')

app1 = dash.Dash(requests_pathname_prefix="/app1/")

app1.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app1.get_asset_url("plotly_logo.png"))],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[html.B('testtesttest')]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                # test prediction
                html.Div(
                    id="power predict",
                    children=[
                        html.B("Energy Prediction"),
                        html.Hr(),
                        dcc.Graph(figure=px.line(test2, x="Date", y=test2.columns[1:]).add_scatter(x=actial_values.index.values[130:], y=actial_values["Peak"][130:].values, name='Actual', line=dict(color='#8a938b')),id="forcastmultimd"),
                    ],
                ),
                # Patient Wait time by Department
                # html.Div(
                #     id="wait_time_card",
                #     children=[
                #         html.B("Patient Wait Time and Satisfactory Scores"),
                #         html.Hr(),
                #         html.Div(id="wait_time_table", children=initialize_table()),
                #     ],
                # ),
            ],
        ),
    ],
)


# @app1.callback(
#     Output("forcastmultimd", "figure"),
# )
# def forcastingPred():
#     # import plotly.express as px

#     # df = px.data.gapminder().query("continent=='Oceania'")
#     fig = px.line(test2, x="Date", y=test2.columns[1:])
#     fig.add_scatter(x=actial_values.index.values, y=actial_values["Peak"].values, name='Actual',
#                     line=dict(color='#8a938b'))
    # return fig



app2 = dash.Dash(requests_pathname_prefix="/app2/")
app2.layout = html.Div("Hello, Dash app 2!")

application = DispatcherMiddleware(
    server,
    {"/app1": app1.server, "/app2": app2.server},
)

if __name__ == "__main__":
    run_simple("localhost", 8050, application,use_reloader=True, use_debugger=True)
    #    app.run_server(debug=True)