import dash
from dash import html, dcc, Output, Input
import flask
import plotly.express as px
import pandas as pd
import pickle
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap
import plotly.graph_objects as go
from forecast_function import forecasting
from plotly.subplots import make_subplots

# from flask_ckeditor import CKEditor
# import flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Server and Dashboard web app
server = flask.Flask(__name__)
app1 = dash.Dash(requests_pathname_prefix="/app1/")
app2 = dash.Dash(requests_pathname_prefix="/app2/")

# Data for web load preparing
with open('dataP/Actual_values.pkl', 'rb') as file:
    actial_values = pickle.load(file)

with open('dataP/df_generation_type_2022.pkl', 'rb') as file:
    df_generation_type_2022 = pickle.load(file)

with open('dataP/df_generation_sector_2022.pkl', 'rb') as file:
    df_consumption_2022 = pickle.load(file)

with open('dataP/df_consumption_month_2022.pkl', 'rb') as file:
    df_month_2022 = pickle.load(file)
# check
# This still temp
# test2 = pd.read_csv('dataP/allmodelpredictedsaved.csv')


# Figure for dashboard
figsubpie = make_subplots(rows=1, cols=2, subplot_titles=('Electricity generation Group by type', 'Electricity  consumption Group by sector'), specs=[
                          [{'type': 'pie'}, {'type': 'pie'}]])

# Electricity generation Group by type
labels = df_generation_type_2022.index[0:7]
values = df_generation_type_2022[0:7]

pietype_generation_fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
pietype_generation_fig.update_layout(title=dict(text='Electricity generation Group by type', font=dict(size=20), automargin=False, yref='paper')
                                     )
figsubpie.add_trace(go.Pie(labels=labels, values=values, showlegend=True,
                    name='Electricity generation Group by type'), row=1, col=1)
# Electricity consumption Group by sector
labels = df_consumption_2022.index[2:7]
values = df_consumption_2022[2:7]
consumption_sector = go.Figure(data=[go.Pie(labels=labels, values=values)])
consumption_sector.update_layout(
    title=dict(text="Electricity consumption Group by sector",
               font=dict(size=20), automargin=False, yref='paper')
)
figsubpie.add_trace(go.Pie(labels=labels, values=values, showlegend=True,
                    name='Electricity consumption Group by sector'), row=1, col=2)

fig_month = px.bar(df_month_2022[df_month_2022["Year"] == 2022], x='Month', y='Grand Total',
             hover_data=df_month_2022.columns[2:-1].values, color='Residential',
             labels={'pop':'Consumption seperated by month'}, height=400)

# model comsumption prediction
forecast = forecasting(GDP_percent=2, Population_percent=0.05, CPI_percent=2)
# fig = px.line(forecast.plotting_value, x="Date", y=forecast.plotting_value.columns[1:])
prediction_allmodelfig = px.line(forecast.plotting_value, x="Date", y=forecast.plotting_value.columns[1:]).add_scatter(
    x=actial_values.index.values[130:], y=actial_values["Peak"][130:].values, name='Actual', line=dict(color='#8a938b'))


# Route of our web
@ server.route("/")
def home():
    return render_template('index.html')
    # return "Hello, Flask!"


@ server.route("/data_")
def data_():
    return render_template('left-sidebar.html')
    # return "Hello, Flask!"


@ server.route("/analysis_")
def analysis_():
    return render_template('right-sidebar.html')
    # return "Hello, Flask!"


@ server.route("/aboutus")
def aboutus():
    return render_template('no-sidebar.html')
    # return "Hello, Flask!"


@ server.route('/render_dashboard')
def render_dashboard():
    return flask.redirect('/app1')


@ server.route('/render_dashboard2')
def render_dashboard2():
    return flask.redirect('/app2')


# DashApp Layout
app1.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(src=app1.get_asset_url("JouleofSiam_logo.png"))],
        ),
        # Left column

        html.Div(
            id="left-column",
            className="eight columns",
            children=[
                # test prediction
                html.Div(
                    id="power predict",
                    children=[
                        html.B("Energy Prediction"),
                        html.Hr(),
                        dcc.Graph(figure=prediction_allmodelfig,
                                  id="forcastmultimd"),
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

        # Right column
        html.Div(
            id="right-column",
            className="four columns",
            children=[html.B('Electricity generation & consumption segmentation'), html.Hr(),
                      # dcc.Graph(figure=pietype_generation_fig),
                      # dcc.Graph(figure=consumption_sector),
                      dcc.Graph(figure=figsubpie),
                      dcc.Graph(figure=fig_month)]
            + [html.Div(["initial child"], id="output-clientside",
                        style={"display": "none"})],
        )
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


app2.layout = html.Div("Hello, Dash app 2!")

application = DispatcherMiddleware(
    server,
    {"/app1": app1.server, "/app2": app2.server},
)

if __name__ == "__main__":
    run_simple("localhost", 8050, application,
               use_reloader=True, use_debugger=True)
    #    app.run_server(debug=True)
