from datetime import datetime, timedelta

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px

class Techn:
    def __init__(self):
        
        self.button_mesure = html.Div(
                [
                    dbc.RadioItems(
                        id="radio-analyse",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                        options=[
                            {"label": "Log Yield", "value": 'rend'},
                            {"label": "Standardization", "value": 'norm'},
                        ],
                        value='rend',
                    )
                ],
                className="radio-group",
            )
        
        self.index_select = dbc.Select(
            id='index-select',
            options=[{'label': 'S&P 500', 'value': 'SP'}, {'label': 'CAC 40', 'value': 'CAC'}],
            value='SP'
        )

        
    def date_gestion(self):
        return dcc.RangeSlider(
                id='year-range-slider',
                step=1
            )
    
    def render(self):
        row = html.Div(
                [
                    dbc.Row(dbc.Col(html.H4("Technical Analysis", className="display-7", style={'font-weight':'bold', 'color':'#d10737'}))),
                    dbc.Row(
                        [
                            # Colonne de gauche avec le RangeSlider et un graphique
                            dbc.Col([html.Br(), dbc.Row([dbc.Col(self.date_gestion())]), dcc.Graph(id='adobe-graph')], width=6),
                            dbc.Col([html.Br(), dbc.Row([dbc.Col(self.index_select), dbc.Col(self.button_mesure)]), dcc.Graph(id='index-graph')], width=6),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col([html.Br(), dcc.Graph(id='line-chart')], width=6),
                            # Colonne de droite avec une table de données filtrable
                            dbc.Col([html.Br(), dash_table.DataTable(id="data-table", filter_action="native", filter_options={"placeholder_text": "Filter..."}, page_size=10)], width=6),
                        ], style={'height': '400px'}
                    ),
                ]
            )
        return row
