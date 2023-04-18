import dash
from dash import html, dcc, Output, Input, State
import flask
import plotly.express as px
import pandas as pd
import pickle
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap
import plotly.graph_objects as go
from forecast_function import forecasting
from plotly.subplots import make_subplots
from Calucation_electricity import calculate_electricity_charge

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired

# from flask_ckeditor import CKEditor
# import flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Server and Dashboard web app
server = flask.Flask(__name__)
server.config['SECRET_KEY'] = 'mykey'
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

FT_prediction = pd.read_csv("dataP/FT_full.csv")
FT_prediction['Date'] = pd.to_datetime(FT_prediction['Date'])
FT_prediction.set_index("Date", inplace=True)

df_historical = pd.read_csv("./dataP/all_historical.csv")
df_historical.set_index("Date", inplace=True)
historical_fig = px.line(df_historical, x=df_historical.index, y=df_historical.columns.values, title='Historical trends and predictions for Peak load (Unit:MW)')


df_norm = pd.read_csv("./dataP/Features_correlation.csv")
df_norm.set_index("Date", inplace=True)

df_norm_fig = px.line(title="Features Correlation")
df_norm_fig.add_trace(go.Scatter(x=df_norm.index.values, y=df_norm["Peak"], name='Peak',
                         line = dict(color='black', width=3, dash='dash')))
df_norm_fig.add_trace(go.Scatter(x=df_norm.index.values, y=df_norm["Population"], name='Population',
                         line = dict(color='firebrick', width=1, dash='dot')))
df_norm_fig.add_trace(go.Scatter(x=df_norm.index.values, y=df_norm["Temperature"], name='Temperature',
                         line = dict(color='green', width=1, dash='dot')))
df_norm_fig.add_trace(go.Scatter(x=df_norm.index.values, y=df_norm["CPI"], name='CPI',
                         line = dict(color='navy', width=1, dash='dot')))
df_norm_fig.add_trace(go.Scatter(x=df_norm.index.values, y=df_norm["GDP"], name='GDP',
                         line = dict(color='red', width=1, dash='dot')))
df_norm_fig.add_trace(go.Scatter(x=df_norm.index.values, y=df_norm["Year"], name='Year',
                         line = dict(color='fuchsia', width=1, dash='dash')))

xgboost_rmse = 390.68
lstm_rmse = 29.41
lasso_rmse = 373.65

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
                    name='Electricity generation classified by fuel type (Year=2022)', hole=0.7), row=1, col=1)
# Electricity consumption Group by sector
labels = df_consumption_2022.index[2:7]
values = df_consumption_2022[2:7]
consumption_sector = go.Figure(data=[go.Pie(labels=labels, values=values)])
consumption_sector.update_layout(
    title=dict(text="Electricity consumption classified by sector (Year=2022)",
               font=dict(size=20), automargin=False, yref='paper')
)
# check
figsubpie.add_trace(go.Pie(labels=labels, values=values, showlegend=True,
                    name='Electricity consumption Group by sector', hole=0.7), row=1, col=2)

fig_month = px.bar(df_month_2022[df_month_2022["Year"] == 2022], x='Month', y='Grand Total',
                   hover_data=df_month_2022.columns[2:-
                                                    1].values, color='Residential',
                   labels={'pop': 'Consumption seperated by month'}, height=400)
fig_month.update_layout(
    title=dict(text="Consumption seperated by month",
               font=dict(size=20), automargin=False, yref='paper')
)


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


@ server.route("/conseda")
def conseda():
    return render_template('right-sidebar.html')


@ server.route("/conspred")
def conspred():
    return render_template('right-sidebarpred.html')


class MyForm(FlaskForm):
    unit   = StringField('Energy used', validators=[DataRequired()])
    ft      = StringField('Ft', validators=[DataRequired()])
    submit  = SubmitField('confirm')

@ server.route("/pricepred", methods = ['GET','POST'])
def pricepred():
    unit  = False
    ft = False
    price = False
    form = MyForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        unit = form.unit.data 
        ft = form.ft.data
        price = calculate_electricity_charge(unit,ft)
        form.unit.data = ""
    return render_template('right-sidebarprice.html',form=form,unit=unit,ft=ft,price=price)


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
                        
                        html.B("Features correlation"),
                        dcc.Graph(figure=df_norm_fig),

                        html.B("Historical Data"),
                        dcc.Graph(figure=historical_fig),

                        html.H2('Model RMSE Values'),
                        html.Div('XGBoost RMSE: {} '.format(xgboost_rmse), style={'display': 'inline-block', 'margin-right': '20px'}),
                        html.Div('LSTM RMSE: {} '.format(lstm_rmse), style={'display': 'inline-block', 'margin-right': '20px'}),
                        html.Div('LASSO RMSE: {} '.format(lasso_rmse), style={'display': 'inline-block', 'margin-right': '20px'}),
                        
                        html.Div([
                        html.B("Energy Prediction (Unit: Gwh)"),], style={'margin-top': '20px'}),
                        html.Hr(),
                        html.P('GDP_input_value'),
                        dcc.Input(id="GDP_input_value", type="number",
                                  placeholder="GDP growth in percentage", value=2),
                        html.P('Population_input_value'),
                        dcc.Input(id="Population_input_value", type="number",
                                  placeholder="Population growth in percentage", value=0.05),
                        html.P('CPI_input_value'),
                        dcc.Input(id="CPI_input_value", type="number",
                                  placeholder="CPI growth in percentage", value=2),
                        dcc.Graph(figure=prediction_allmodelfig,
                                  id="forcastmultimd", responsive=True),
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


                      # dcc.Graph(figure=fig_month)]
                      dcc.Graph(figure=prediction_allmodelfig, id='fig_month_id'),                      dcc.Dropdown(id='fig_month_dropdown',
                                                                                                                     options=[
                                                                                                                         {'label': 'Residential',
                                                                                                                          'value': 'Residential'},
                                                                                                                         {'label': 'Business',
                                                                                                                          'value': 'Business'},
                                                                                                                         {'label': 'Industrial',
                                                                                                                          'value': 'Industrial'},
                                                                                                                         {'label': 'Government',
                                                                                                                          'value': 'Government and Non-Profit'},
                                                                                                                         {'label': 'Other sector',
                                                                                                                          'value': 'Other sector'}
                                                                                                                     ],
                                                                                                                     value='Residential'),
                      html.Button('Submit', id='submit-val', n_clicks=0),]
            + [html.Div(["initial child"], id="output-clientside",
                        style={"display": "none"})],
        )
    ],
)


@app1.callback(Output(component_id='fig_month_id', component_property='figure'),
               Input(component_id='submit-val', component_property='n_clicks'),
               State(component_id='fig_month_dropdown', component_property='value'))
def Update_month_by_sector(n_clicks, fig_month_dropdown):

    # print('Fig dropdown values')
    # print(fig_month_dropdown)

    fig_month = px.bar(df_month_2022[df_month_2022["Year"] == 2022], x='Month', y='Grand Total',
                       hover_data=df_month_2022.columns[2:-
                                                        1].values, color=fig_month_dropdown,
                       labels={'pop': 'Consumption seperated by month'}, height=400)
    fig_month.update_layout(
        title=dict(text="Consumption seperated by month (Year=2022)",
                   font=dict(size=20), automargin=False, yref='paper')
    )

    return fig_month


@app1.callback(Output(component_id='forcastmultimd', component_property='figure'),
               [Input(component_id='GDP_input_value', component_property='value'),
               Input(component_id='CPI_input_value',
                     component_property='value'),
               Input(component_id='Population_input_value', component_property='value')]
               )
def Update_forecast(GDP_input_value, CPI_input_value, Population_input_value):

    # model comsumption prediction
    forecast = forecasting(GDP_percent=GDP_input_value,
                           Population_percent=Population_input_value, CPI_percent=CPI_input_value)
    #fig = px.line(forecast.plotting_value, x="Date", y=forecast.plotting_value.columns[1:])
    prediction_allmodelfig = px.line(
        forecast.plotting_value, x="Date", y=forecast.plotting_value.columns[1:])
    prediction_allmodelfig.add_scatter(
        x=actial_values.index.values[130:], y=actial_values["Peak"][130:].values, name='Actual', line=dict(color='#8a938b'))

    return prediction_allmodelfig


#app2.layout = html.Div("Hello, Dash app 2!")
app2.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(src=app2.get_asset_url("JouleofSiam_logo.png"))],
        ),
        # Left column

        html.Div(
            id="left-column",
            className="eight columns",
            children=[
                # test prediction
                html.Div(
                    id="FT predict",
                    children=[
                        html.B("FT Prediction"),
                        html.Hr(),
                        dcc.Graph(figure=px.line(FT_prediction, x=FT_prediction.index.values[0:], y=FT_prediction["FT"].iloc[0:]),
                                  id="FT_predict", responsive=True),
                    ],
                ),

            ],
        ),
        # + [html.Div(["initial child"], id="output-clientside",
        #             style={"display": "none"})],

    ],
)


application = DispatcherMiddleware(
    server,
    {"/app1": app1.server, "/app2": app2.server},
)

if __name__ == "__main__":
    run_simple("localhost", 8050, application,
               use_reloader=True, use_debugger=True)
    #    app.run_server(debug=True)
