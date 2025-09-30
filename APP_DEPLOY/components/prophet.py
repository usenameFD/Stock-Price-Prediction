import pandas as pd
from prophet import Prophet
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator
from ta.trend import MACD
import plotly.graph_objects as go

class ProphetForecast:
    def __init__(self, data, date_col='Date', target='Close', features=None, exclude_weekends=True):
        # Initialisation des variables
        self.date_col = date_col
        self.target = target
        self.features = features or ['EMA10Day', 'MA10Day', 'MA30Day', 'RSI14Day', 'RSI3Day', 'RSI9Day', 'MA50Day', 'Signal']
        self.exclude_weekends = exclude_weekends
        self.data = data
        self.model = Prophet()
        self.forecast = None

    def preprocess_data(self):
        # Préparation des données
        self.data[self.date_col] = pd.to_datetime(self.data[self.date_col])
        self.data['ds'] = pd.to_datetime(self.data[self.date_col])
        self.prophet_df = self.data[[self.date_col, self.target] + self.features].copy()
        self.prophet_df = self.prophet_df.rename(columns={self.date_col: 'ds', self.target: 'y'})
        self.prophet_df.dropna(inplace=True)

    def add_regressors(self):
        for feature in self.features:
            self.model.add_regressor(feature)

    def fit_model(self):
        self.preprocess_data()
        self.add_regressors()
        self.model.fit(self.prophet_df)

    def make_future_dataframe(self, p):
        # Générer un dataframe pour la prédiction
        future = self.model.make_future_dataframe(periods=p, freq='B' if self.exclude_weekends else 'D')
        future = future.merge(self.data[['ds'] + self.features], on='ds', how='left')
        future['y'] = self.data[(self.data['Date'] >= future['ds'].min()) & (self.data['Date'] <= future['ds'].max())]['Close']
        return future

    def update_indicators(self, df):
        # Calcul des indicateurs techniques
        df['RSI3Day'] = RSIIndicator(df['y'], window=3).rsi()
        df['RSI9Day'] = RSIIndicator(df['y'], window=9).rsi()
        df['RSI14Day'] = RSIIndicator(df['y'], window=14).rsi()
        df['MA10Day'] = SMAIndicator(df['y'], window=10).sma_indicator()
        df['MA30Day'] = SMAIndicator(df['y'], window=30).sma_indicator()
        df['MA50Day'] = SMAIndicator(df['y'], window=50).sma_indicator()
        df['EMA10Day'] = EMAIndicator(df['y'], window=10).ema_indicator()

        # MACD
        macd = MACD(df['y'])
        df['MACD'] = macd.macd()
        df['Signal'] = macd.macd_signal()
        df.dropna(inplace=True)
        return df

    def predict(self, p):
        future = self.prophet_df[['ds'] + self.features].copy()
        future['y'] = self.data[(self.data['Date'] >= future['ds'].min()) & (self.data['Date'] <= future['ds'].max())][self.target]

        for i in range(p):
            next_date = future['ds'].max() + pd.tseries.offsets.BDay(1 if self.exclude_weekends else 0)
            new_row = {'ds': next_date}

            for feature in self.features:
                if feature in future.columns:
                    new_row[feature] = future[feature].iloc[-1]

            future = pd.concat([future, pd.DataFrame([new_row])], ignore_index=True)
            forecast = self.model.predict(future[['ds'] + self.features])
            new_prediction = forecast['yhat'].iloc[-1]
            future.loc[future['ds'] == next_date, 'y'] = new_prediction

            future = self.update_indicators(future)

        self.forecast = self.model.predict(future)
        return self.forecast

    def plot_forecast(self):
        fig = self.model.plot(self.forecast)
        fig.suptitle('Prédiction des prix de clôture avec Prophet')
        return fig

    def get_forecast_table(self):
        return self.forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(len(self.forecast))