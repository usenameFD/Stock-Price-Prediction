from datetime import datetime, timedelta

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px

class Model:
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

        self.tab_group =  dbc.ListGroup(
                    [
                        dbc.ListGroupItem("Model Performance Metrics", active=True),
                        dbc.ListGroupItem("RMSE: 7.20"),
                        dbc.ListGroupItem("MAE: 4.76"),
                        dbc.ListGroupItem("MAPE: 0.90%"),
                        dbc.ListGroupItem("Training Period: Jan 2010 - Dec 2023"),
                        dbc.ListGroupItem("Test Period: Jan 2024 - Oct 2024"),
                        dbc.ListGroupItem("Last Updated: 04 Jan 2025")
                    ]
                )      
        
    def render(self):
        row = html.Div(
                [
                    dbc.Row(dbc.Col(html.H4("Model Adobe Deployed", className="display-7", style={'font-weight':'bold', 'color':'#d10737'}))),
                    dbc.Row(
                        [
                            # Colonne de gauche avec le RangeSlider et un graphique
                            dbc.Col([dcc.Graph(id='predict-graph')], width=9),
                            dbc.Col([html.Br(), html.H5("Number of Future Days :", style={"color": "#2c3e50", "fontWeight": "normal" }) ,
                                     dbc.Input(id="future-days",debounce=True, type='number', placeholder="Valid input...", valid=True, className="mb-3"),
                                     self.tab_group], width=3),
                        ]
                    ),
                    dbc.Row(
                        [
                            # Colonne de gauche avec le RangeSlider et un graphique
                            dbc.Col([html.H5("Table of Predictions and Confidence Intervals", style={
                                "color": "#2c3e50",  # Bleu nuit
                                "fontWeight": "normal" , # Texte moins gras
                                "marginLeft": "30px",
                            }), html.Br(),  dash_table.DataTable(id="predict-table", filter_action="native", filter_options={"placeholder_text": "Filter..."}, page_size=10)], width=9),
                        ],
                        style={
                            "marginLeft": "20px",
                            "marginRight": "20px"
                        }
                    )
                ]
            )
        return row
