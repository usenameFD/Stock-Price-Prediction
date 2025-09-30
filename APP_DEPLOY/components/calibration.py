from datetime import datetime, timedelta

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px

class Calibration:
    def __init__(self):
        
        self.button_mesure = html.Div(
                [
                    dbc.RadioItems(
                        id="radios_mesure-analyse",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                        options=[
                            {"label": "Nombre", "value": 'count'},
                            {"label": "Montant", "value": 'volume'},
                        ],
                        value='count',
                    )
                ],
                className="radio-group",
            )
        
        
    def render(self):
        row = html.Div(
                [
                    dbc.Row(dbc.Col(html.H4("Calibration by News", className="display-7", style={'font-weight':'bold', 'color':'#d10737'}))),
                    dbc.Row(
                        [
                            # Colonne de gauche avec le RangeSlider et un graphique
                            dbc.Col([ html.Br(), html.Div(id="word-graph")], width=6),
                            dbc.Col([dcc.Graph(id='sentiment-graph'),
                                     dash_table.DataTable(id="day-table", filter_action="native", filter_options={"placeholder_text": "Filter..."}, page_size=10)], width=6),
                        ]
                    ),
                    dbc.Row(
                        [
                            # Colonne de gauche avec le RangeSlider et un graphique
                            dbc.Col([ html.Br(), html.H5("Scrapped Adobe Information", style={
                                "color": "#2c3e50",  # Bleu nuit
                                "fontWeight": "normal" , # Texte moins gras
                                "marginLeft": "30px",
                            }), html.Br(),  dash_table.DataTable(id="scrapped-table", filter_action="native", 
                                                                 filter_options={"placeholder_text": "Filter..."}, page_size=10,
                                                                 style_table={'width': '100%', 'maxWidth': '100%', 'overflowX': 'auto'},
                                                                 style_cell={
        'width': '10%',  # Largeur de la première colonne (10%)
        'maxWidth': '10%',
        'overflow': 'hidden',  # Empêche le débordement du texte
        'textOverflow': 'ellipsis',  # Ajoute des points de suspension pour le texte trop long
    },)], width=12),
                        ],
                        style={
                            "marginLeft": "20px",
                            "marginRight": "20px"
                        }
                    )
                ]
            )
        return row
