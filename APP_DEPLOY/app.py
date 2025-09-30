from dash import Dash, html, Input, Output, callback, dcc, State, dash_table, DiskcacheManager
import os
from datetime import datetime, timedelta
import dash

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
import pandas as pd
import numpy as np

from components.menu import *
from components.prophet import ProphetForecast
from components.analyse import Analyse
from components.techn import Techn
from components.model import Model
from components.calibration import Calibration

import plotly.express as px
import pandas as pd
from collections import Counter

from dash_holoniq_wordcloud import DashWordcloud

import requests
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')


# Initialisation du chemin permettant le lancement de l'application
# Définition du chemin de base pour l'application Dash en utilisant une variable d'environnement pour l'utilisateur

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

path = f"/"
app = Dash(__name__, requests_pathname_prefix=path, external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME], suppress_callback_exceptions = True)

app.index_string = INDEX_CONFIG

# Initialisation des différentes sections de l'application via des objets personnalisés
analyse = Analyse()      
tech = Techn() 
model = Model() 
calibration = Calibration() 


CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

sidebar = Menu(path).render()
content =  dbc.Spinner(html.Div(id="page-content", style=CONTENT_STYLE), spinner_style={"width": "3rem", "height": "3rem"})

app.layout = html.Div(
    [
        dcc.Location(id="url"), # Permet de gérer les URLs et la navigation au sein de l'application
        sidebar, # Ajout de la barre latérale
        content, # Contenu principal avec un Spinner
        html.Button(id='load-data-button', style={"display": "none"}), # Bouton caché pour déclencher le chargement des données
        dcc.Store(id='selected-item', data='', storage_type='session'),  # Stockage temporaire de données sélectionnées en session
        html.Div(id="hidden-div", style={"display": "none"}), # Division cachée pour stocker d'autres informations ou déclencher des callbacks
    ])



date_considere = (datetime.today() - timedelta(days=1)).date().strftime("%Y-%m-%d")
api_key = '1212688ede774309ad6e24ee2a5bd970'

def get_news(date, api_key):
    # URL de NewsAPI
    url = f'https://newsapi.org/v2/everything?q=adobe&?country=us&from={date}&sortBy=publishedAt&apiKey={api_key}'

    # Faire la requête
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        news_data = []

        # Vérifier s'il y a des articles dans la réponse
        if data['articles']:
            df = pd.json_normalize(data['articles'])[["publishedAt", "title", "description"]]
            
            df.columns = ["Date", "Title", "Description"]
            df = df[["Title", "Description"]]
            return df
        else:
            print("Aucun article trouvé pour cette date.")
            return pd.DataFrame() 
    else:
        print(f"Erreur lors de la récupération des actualités. Code : {response.status_code}")
        return pd.DataFrame()
    
##############################
# Import des données d'Adobe et des indices
start_date = '2010-01-01'
end_date = pd.to_datetime('today')

adobe_data = yf.download('ADBE', start=start_date, end=end_date)
sp_data = yf.download('^GSPC', start=start_date, end=end_date)
cac_data = yf.download('^FCHI', start=start_date, end=end_date)

adobe_data.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
sp_data.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
cac_data.columns = ['Close', 'High', 'Low', 'Open', 'Volume']

# Calcul du rendement logarithmique
adobe_data['LogReturn'] = np.log(adobe_data['Close'] / adobe_data['Close'].shift(1))
sp_data['LogReturn'] = np.log(sp_data['Close'] / sp_data['Close'].shift(1))
cac_data['LogReturn'] = np.log(cac_data['Close'] / cac_data['Close'].shift(1))

# Normalisation Min-Max des prix de clôture
adobe_data['NormalizedClose'] = (adobe_data['Close'] - adobe_data['Close'].min()) / (adobe_data['Close'].max() - adobe_data['Close'].min())
sp_data['NormalizedClose'] = (sp_data['Close'] - sp_data['Close'].min()) / (sp_data['Close'].max() - sp_data['Close'].min())
cac_data['NormalizedClose'] = (cac_data['Close'] - cac_data['Close'].min()) / (cac_data['Close'].max() - cac_data['Close'].min())


# Charger le dataframe
df_sentiment = pd.read_csv('data\macro_sentiment_info.csv')

df_sentiment['Year'] = pd.to_datetime(df_sentiment['DATE']).dt.year
df_sentiment['Month'] = pd.to_datetime(df_sentiment['DATE']).dt.month_name()

# Normaliser les valeurs en Min-Max pour les colonnes numériques manuellement
columns_to_normalize = ['EMVMACROBUS', 'CPIAUCSL', 'EXPINF1YR', 'LNS12032195', 'UMCSENT']
for column in columns_to_normalize:
    min_value = df_sentiment[column].min()
    max_value = df_sentiment[column].max()
    df_sentiment[column + '_N'] = (df_sentiment[column] - min_value) / (max_value - min_value)


# Calcul des indicateurs techniques pour Adobe
def calculate_indicators(df):
    df['RSI3Day'] = RSIIndicator(df['Close'], window=3).rsi()
    df['RSI9Day'] = RSIIndicator(df['Close'], window=9).rsi()
    df['RSI14Day'] = RSIIndicator(df['Close'], window=14).rsi()
    df['RSI30Day'] = RSIIndicator(df['Close'], window=30).rsi()
    df['MA10Day'] = SMAIndicator(df['Close'], window=10).sma_indicator()
    df['MA30Day'] = SMAIndicator(df['Close'], window=30).sma_indicator()
    df['MA50Day'] = SMAIndicator(df['Close'], window=50).sma_indicator()
    df['EMA10Day'] = EMAIndicator(df['Close'], window=10).ema_indicator()
    # MACD
    macd = MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()

    return df

adobe_data = calculate_indicators(adobe_data)
adobe_data['Date'] = pd.to_datetime(adobe_data.index)

forecast_model = ProphetForecast(adobe_data)
forecast_model.fit_model()






scrapped_data = get_news(date_considere, api_key)
scrapped_data = scrapped_data.dropna()

text = ' '.join(scrapped_data['Title']) + ' ' + ' '.join(scrapped_data['Description'])
# Convertir le texte en minuscules
text = text.lower()

# Retirer les caractères spéciaux, chiffres, et ponctuation
text = re.sub(r'[^a-z\s]', '', text)

# Liste des prépositions à retirer
prepositions = {'de', 'la', 'le', 'des', 'en', 'pour', 'avec', 'sans', 'sur', 'par', 'à', 'et', 'mais', 'ou'}

# Tokenisation du texte (division en mots)
words = text.split()

# Retirer les prépositions et les mots de moins de 3 caractères
words = [word for word in words if word not in prepositions and len(word) > 4]

# Compter la fréquence des mots
word_counts = Counter(words)

df_words = pd.DataFrame(word_counts.items(), columns=['Word', 'Count'])
df_words['Count'] = df_words['Count']*10


# Initialisation de l'analyseur de sentiment
sia = SentimentIntensityAnalyzer()

# Fonction pour classer le sentiment
def classify_sentiment(text):
    sentiment_score = sia.polarity_scores(text)
    compound_score = sentiment_score['compound']
    
    if compound_score >= 0.05:
        return 'Positive'
    elif compound_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

# Appliquer l'analyse de sentiment sur les titres et descriptions
scrapped_data['Sentiment'] = scrapped_data['Title'] + ' ' + scrapped_data['Description']
scrapped_data['Sentiment'] = scrapped_data['Sentiment'].apply(classify_sentiment)


sentiment_counts = scrapped_data['Sentiment'].value_counts()

# Créer le dataframe sentiment_data
sentiment_data = pd.DataFrame({
    'Sentiment': sentiment_counts.index,
    'Count': sentiment_counts.values
})


# Callback pour mettre à jour le contenu de la page en fonction du chemin d'URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    # Affiche le rendu correspondant à l'URL, sinon retourne l'analyse par défaut
    if pathname == f"{path}":
        return analyse.render() 
    elif pathname == f"{path}techn": 
        return tech.render() 
    elif pathname == f"{path}model": 
        return model.render() 
    elif pathname == f"{path}calibration": 
        return calibration.render() 
    else:
        return analyse.render()             # Page par défaut (analyse) si le chemin n'est pas reconnu



############################ ANALYSE TECHNIQUE #################################

@app.callback(
    Output('year-range-slider', 'min'),
    Output('year-range-slider', 'max'),
    Output('year-range-slider', 'value'),
    Output('year-range-slider', 'marks'),
    Input('load-data-button', 'n_clicks')
)
def update_range_slider(n_clicks):
    min_year = adobe_data.index.year.min()
    max_year = adobe_data.index.year.max()
    marks = {str(year): str(year) for year in range(min_year, max_year + 1)}
    return min_year, max_year, [min_year, max_year], marks

@app.callback(
    Output('adobe-graph', 'figure'),
    [Input('year-range-slider', 'value')]
)
def update_adobe_graph(year_range):
    start_year = 2010 if year_range is None else year_range[0]
    end_year = pd.to_datetime('today').year if year_range is None else year_range[1]
    filtered_data = adobe_data[(adobe_data.index.year >= start_year) & (adobe_data.index.year <= end_year)]

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=filtered_data.index,
        open=filtered_data['Open'],
        high=filtered_data['High'],
        low=filtered_data['Low'],
        close=filtered_data['Close'],
        name='Candlestick'
    ))

    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Close'], mode='lines', name='Close'))

    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['MA10Day'], mode='lines', name='MA10'))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['MA30Day'], mode='lines', name='MA30'))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['MA50Day'], mode='lines', name='MA50'))
    
    # Ajout de l'EMA10
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['EMA10Day'], mode='lines', name='EMA10'))

    fig.update_layout(title='Adobe Stock Analysis', xaxis_rangeslider_visible=False)
    return fig

@app.callback(
    Output('index-graph', 'figure'),
    [Input('year-range-slider', 'value'), Input('index-select', 'value'), Input('radio-analyse', 'value')]
)
def update_index_graph(year_range, index, radio):
    # Choix des données en fonction de l'index sélectionné
    index_data = {'SP': sp_data, 'CAC': cac_data}
    data = index_data.get(index, sp_data)

    # Filtrer les données en fonction de la plage d'années
    start_year = 2010 if year_range is None else year_range[0]
    end_year = pd.to_datetime('today').year if year_range is None else year_range[1]
    filtered_data = data[(data.index.year >= start_year) & (data.index.year <= end_year)]
    
    # Filtrer également les données d'Adobe
    filtered_adobe_data = adobe_data[(adobe_data.index.year >= start_year) & (adobe_data.index.year <= end_year)]

    # Choisir le type d'analyse à afficher (LogReturn ou autres)
    fig = go.Figure()

    # Ajouter les traces pour l'indice sélectionné
    if radio == 'rend':
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['LogReturn'], mode='lines', name=f'{index} LogReturn'))
    else:
        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['NormalizedClose'], mode='lines', name=f'{index} Close Price'))

    # Ajouter les traces pour Adobe (LogReturn ou Close)
    if radio == 'rend':
        fig.add_trace(go.Scatter(x=filtered_adobe_data.index, y=filtered_adobe_data['LogReturn'], mode='lines', name='Adobe LogReturn'))
    else:
        fig.add_trace(go.Scatter(x=filtered_adobe_data.index, y=filtered_adobe_data['NormalizedClose'], mode='lines', name='Adobe Close Price'))

    # Mise à jour de la mise en page du graphique
    fig.update_layout(title=f'{index} Index vs Adobe', xaxis_rangeslider_visible=False)

    return fig

# Callback pour mettre à jour le graphique et le tableau en fonction des années sélectionnées
@app.callback(
    [Output('line-chart', 'figure'),
     Output('data-table', 'data'), Output('data-table', 'columns')],
    [Input('year-range-slider', 'value')]
)
def update_graph_and_table(year_range):
    start_year, end_year = year_range
    
    # Filtrer les données selon la plage d'années
    filtered_data = df_sentiment[(df_sentiment['Year'] >= start_year) & (df_sentiment['Year'] <= end_year)]

    # Graphique de séries temporelles
    fig = px.line(filtered_data, 
                  x='DATE', 
                  y=[i + '_N' for i in columns_to_normalize], 
                  title='Normalized Macro Sentiment Analysis by Time')
    
    # Tableau de données
    table_data = filtered_data[['DATE'] + columns_to_normalize].to_dict('records')

    return fig, table_data, [{"name": i, "id": i} for i in ['DATE'] + columns_to_normalize]


############################ MODELE DEPLOYE #################################

@app.callback(
    Output("future-days", "value"),
    Input('load-data-button', 'n_clicks') 
)
def initialize_days(_):
    return 10


@app.callback(
    [Output('predict-graph', 'figure'),  Output('predict-table', 'data'), Output('predict-table', 'columns')],
    [Input('load-data-button', 'n_clicks'), Input("future-days", "value")]
)
def update_adobe_predict(n_clicks, p):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=adobe_data.index, y=adobe_data['Close'], mode='lines', name='Close'))

    forecast = forecast_model.predict(p)
    
    # Ajouter une barre verticale pour la date d'aujourd'hui
    today = datetime.today().date()
    fig.add_vline(x=today, line_width=2, line_dash="dash", line_color="red")

    fig.add_trace(go.Scatter(x=forecast.ds, y=forecast['yhat'], mode='lines', name='Prediction'))

    fig.update_layout(title='Adobe Stock Prediction', xaxis_rangeslider_visible=False)

    # Préparer les données du tableau
    forecast['ds'] = forecast['ds'].astype(str)
    forecast[['yhat', 'yhat_lower', 'yhat_upper']] = forecast[['yhat', 'yhat_lower', 'yhat_upper']].round(3)


    table_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(p).to_dict('records')
    columns = [{"name": i, "id": i} for i in ['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


    return fig , table_data, columns



############################ CALIBRATION BY NEWS #################################

@app.callback(
    [Output('word-graph', 'children'),
     Output('sentiment-graph', 'figure'),
     Output('scrapped-table', 'data'),
     Output('scrapped-table', 'columns'),
     Output('day-table', 'data'),
     Output('day-table', 'columns')],
    [Input('load-data-button', 'n_clicks')]
)
def update_news_calibration(n_clicks):
    # Nuage de mots
    wordcloud = DashWordcloud(
        list=[[word, count] for word, count in zip(df_words['Word'], df_words['Count'])],
        width=800, height=450,
        gridSize=16,
        shuffle=False,
        rotateRatio=0.5,
        shrinkToFit=True,
        shape='circle',
        hover=True
    )

    color_map = {
        'Positive': '#00FF00',  # Vert pour Positive
        'Negative': '#FF0000',  # Rouge pour Negative
        'Neutral': '#808080'    # Gris pour Neutral
    }
    colors = [color_map[sentiment] for sentiment in sentiment_data['Sentiment']]

    # Graphique en camembert pour l'analyse de sentiment
    fig_sentiment = go.Figure()
    fig_sentiment.add_trace(go.Pie(labels=sentiment_data['Sentiment'], values=sentiment_data['Count'], marker=dict(colors=colors)))
    fig_sentiment.update_layout(title='Sentiment Analysis')

    # Données pour la table
    forecast = forecast_model.predict(1)
    forecast[['yhat', 'yhat_lower', 'yhat_upper']] = forecast[['yhat', 'yhat_lower', 'yhat_upper']].round(3)


    table_data_pred = forecast[['yhat', 'yhat_lower', 'yhat_upper']].tail(1).to_dict('records')
    columns_pred = [{"name": i, "id": i} for i in ['yhat', 'yhat_lower', 'yhat_upper']]

    table_data = scrapped_data.to_dict('records')
    table_columns = [{'name': col, 'id': col} for col in scrapped_data.columns]
    
    
    return html.Div([wordcloud]), fig_sentiment, table_data, table_columns, table_data_pred, columns_pred


if __name__ == '__main__':
    app.run(debug=True)
    
