from xgboost import XGBRegressor
from sklearn.neural_network import MLPRegressor

import numpy as np
import pandas as pd
import pickle

class forecasting():

    def __init__(self, 
                 GDP_percent=2, 
                 Population_percent=0.05, 
                 CPI_percent=2,
                 Start_date = '2023-01',
                 End_date = '2033-01'
                 ):
        
        # Check date eligibility
        self.Check_date_eligibility(Start_date, End_date)

        # Get Static temperature values
        file = open("./DataP/forecast_temperature.pkl", "rb")
        Temperature_forecast = pickle.load(file)
        self.Temperature_forecast = Temperature_forecast[0:len(self.Date)]

        # Get forecasted LSTM values
        LSTM_forecast = pickle.load(open("./DataP/forecast_LSTM.pkl", "rb"))
        self.LSTM_forecast = LSTM_forecast[0:len(self.Date)]

        # Get forecasted ARIMA values
        ARIMA_forecast = pickle.load(open("./DataP/forecast_ARIMA.pkl", "rb"))
        self.ARIMA_forecast = ARIMA_forecast[0:len(self.Date)]

        # Get forecasted SARIMA values
        SARIMA_forecast = pd.read_csv("./DataP/SARIMA_forecasts.csv")["Peak Forecast"]
        self.SARIMA_forecast = SARIMA_forecast[0:len(self.Date)]


        # Initial values for generating features
        self.GDP_value = 924033.33
        self.Population_value = 66.09
        self.CPI_value = 106.47

        # Initial percentages
        self.GDP_percent = GDP_percent
        self.Population_percent = Population_percent
        self.CPI_percent = CPI_percent

        # Initial XGBoost model
        self.XGBoost_model = XGBRegressor()
        self.XGBoost_model.load_model("./DataP/XGBoost_model.json")

        # # Initial ANN model
        # self.ANN_scaler = pickle.load(open('./Data/monthly_scaler.pkl', 'rb'))
        # self.ANN_model = pickle.load(open('./Data/ANN_monthly.pkl', 'rb'))

        # Prepare data
        self.prepare_data()

        # Prediction
        self.get_prediction()

        # Ploting Data
        self.plotting_data()
    
    def Check_date_eligibility(self, start_date, end_date):
        
        start_date = np.array(start_date, dtype='datetime64[M]')
        end_date   = np.array(end_date, dtype='datetime64[M]')

        date_delta = end_date - start_date

        if date_delta.astype(int) < 0:
            raise ValueError('Invalid start_date/end_date')
        else:
            self.Start_date = start_date
            self.End_date   = end_date
            Date        = np.arange(start_date, end_date, dtype='datetime64[M]')
            self.months = Date.astype('datetime64[M]').astype(int) % 12 + 1
            self.years  = Date.astype('datetime64[Y]').astype(int) + 1970
            self.Date   = Date.astype(str).tolist()

    # Function to convert integer to list.
    def as_list(self, x):
        if type(x) is list:
            return x
        else:
            return [x]
    

    # Function to generated prediction.
    def assume_predict(self, value, percent_list):
        
        results = list()
        temp = list()
        temp_val = value

        percent_list = self.as_list(percent_list)

        for percent in percent_list:

            # Divided % per years to per months

            percent_month = percent/12

            for current_date in self.Date:
                temp_val = temp_val + (temp_val * percent_month/100)
                temp.append(temp_val)

            temp_val = value
            results.append(temp)
            temp = list()
        return results[0]
    
    def prepare_data(self):

        # Get Assume values
        GDP_forecast = self.assume_predict(self.GDP_value, self.GDP_percent)
        Population_forecast = self.assume_predict(self.Population_value, self.Population_percent)
        CPI_forecast = self.assume_predict(self.CPI_value, self.CPI_percent)

        # Create DataFrame/features for XGBoost
        features_dataframe = pd.DataFrame([self.Date, self.years, self.months, 
                                           Population_forecast, self.Temperature_forecast, 
                                            CPI_forecast, GDP_forecast]).T
        features_dataframe.columns = ["Date", "Year", "Month", "Population", "Temperature", 
                                    "CPI", "GDP"]
        
        # Convert DataFrame types
        features_dataframe['Date']= pd.to_datetime(features_dataframe['Date'])
        features_dataframe['Year']= features_dataframe['Date'].dt.year
        features_dataframe['Month']= features_dataframe['Date'].dt.month
        
        features_dataframe[["Population", "Temperature", "CPI", "GDP"]] = \
        features_dataframe[["Population", "Temperature", "CPI", "GDP"]].astype(float)

        
        features_dataframe.set_index("Date", inplace=True)
        
        self.XGBoost_features = features_dataframe

        # Create features for ANN
        self.ANN_features = features_dataframe[["Population", "Temperature", "CPI", "GDP"]].values

    def get_prediction(self):
        
        # XG_Boost prediction
        self.XGBoost_prediction = self.XGBoost_model.predict(self.XGBoost_features)
        
        # ANN prediction
        #self.ANN_prediction     = self.ANN_model.predict(self.ANN_scaler.transform(self.ANN_features))

    def plotting_data(self):

        # With ANN
        # self.plotting_value = pd.DataFrame([self.Date, self.LSTM_forecast, 
        #                                     self.XGBoost_prediction, self.ANN_prediction, 
        #                                     self.ARIMA_forecast, self.SARIMA_forecast]).T
        
        self.plotting_value = pd.DataFrame([self.Date, self.LSTM_forecast, 
                                    self.XGBoost_prediction, self.ARIMA_forecast, 
                                    self.SARIMA_forecast]).T
        


        # self.energy_reserve_20 = 42909.9#self.LSTM_forecast.mean() * 1.20
        # self.energy_reserve_35 = 49144.8#self.LSTM_forecast.mean() * 1.35
        # self.energy_reserve_50 = self.LSTM_forecast.mean() * 1.50
        self.plotting_value.columns = ["Date", "LSTM", "XGBoost", "ARIMA", "SARIMA"]
        #self.plotting_value["ANN"] = self.plotting_value["ANN"].abs()

        # Convert Datatype
        #self.plotting_value["Date"] = pd.to_datetime(df['Date'])
        self.plotting_value[["LSTM", "XGBoost", "ARIMA", "SARIMA"]] = \
        self.plotting_value[["LSTM", "XGBoost", "ARIMA", "SARIMA"]].astype(float)

        # Insert current maximum capacity.
        self.plotting_value.insert(loc=len(self.plotting_value.columns), 
                                   column="Maximum_capacity",
                                   value= 49144.80
                                   )
        
        self.plotting_value.insert(loc=len(self.plotting_value.columns), 
                                   column="Maximum_capacity_wo_import",
                                   value= 42909.9
                                   )
