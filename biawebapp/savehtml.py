import pandas as pd
import plotly.express as px
FT_prediction = pd.read_csv("dataP/FT_full.csv")
FT_prediction['Date'] = pd.to_datetime(FT_prediction['Date'])
FT_prediction.set_index("Date", inplace=True)
figure = px.line(
    FT_prediction, x=FT_prediction.index.values[0:], y=FT_prediction["FT"].iloc[0:])
figure.write_html("templates/saveplot.html")
