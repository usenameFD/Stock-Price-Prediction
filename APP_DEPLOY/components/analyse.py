from datetime import datetime, timedelta

from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px

class Analyse:
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
        
        self.card_icon = {
        "color": "white",
        "textAlign": "center",
        "fontSize": 30,
        "margin": "auto",
    }

        self.tab =  dcc.Tabs([
                dcc.Tab(label='Description', children=[
                        dbc.Row(
                                [
                                    dbc.Col([
                                        html.Br(),
                                        dbc.ListGroup([
                                            dbc.ListGroupItem("Financial Performance", active=True),
                                            dbc.ListGroupItem("Revenue Growth: 12%"),
                                            dbc.ListGroupItem("Profit Margins: 30.51%"),
                                            dbc.ListGroupItem("EPS: $14.25"),
                                            dbc.ListGroupItem("FCF: $6.8B"),
                                            dbc.ListGroupItem("ROE: 29%"),
                                            dbc.ListGroupItem("P/E Ratio: 35.57"),
                                            dbc.ListGroupItem("Total Assets: $29.83B"),
                                            dbc.ListGroupItem("Dividend Yield: N/A"),
                                        ])
                                    ], width=6),

                                    dbc.Col([
                                        html.Br(),
                                        dbc.ListGroup([
                                            dbc.ListGroupItem("Operational & Strategic Metrics", active=True),
                                            dbc.ListGroupItem("Market Share: 30%"),
                                            dbc.ListGroupItem("Debt/Equity: 0.25"),
                                            dbc.ListGroupItem("R&D: $2.2B"),
                                            dbc.ListGroupItem("Retention: 90%"),
                                            dbc.ListGroupItem("Employees: 29 945"),
                                            dbc.ListGroupItem("CEO Tenure: 6 years"),
                                            dbc.ListGroupItem("Customer Base: 26M+"),
                                            dbc.ListGroupItem("Sustainability Rating: A"),
                                        ])
                                    ], width=6),


                                ])
                    
                        ]),
                ])
        
    def card_top(self, icon, title, info):
        card = dbc.CardGroup(
            [
                
                dbc.Card(
                    html.Div(className=icon, style=self.card_icon),
                    className="bg-danger",
                    style={"maxWidth": 75},
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5(title, className="card-title"),
                            html.P(info, className="card-text",),
                        ]
                    )
                ),
            ],className="mt-4 shadow",
        )
        return card
    
    def notif_time_line(self):
        
        list_group = html.Div([
                        dbc.Row([dbc.Col(html.H4("About Adobe Systems Inc.", className="my-4", style={'font-weight':'bold', 'color':'#d10737'}), width=6)]),
                    html.Div([

                        html.P([
                            "Adobe Systems Inc. was founded in 1982 and is headquartered in California. This software company offers a range of solutions for individual and commercial customers worldwide. Adobe products include", 
                            html.Strong("Adobe Acrobat, Photoshop, InDesign, Illustrator, and more. ") ,
                            "The company has offices in North America, Asia, Australia, New Zealand, Europe, the Middle East, Africa, and South America. For the fiscal year 2017, the company's revenue reached ", 
                            html.Strong("$7.302 billion. ")
                        
                        ]),

                        html.P([
                            "With a strong focus on ", html.Em("innovation and artificial intelligence (AI)"), 
                            ", Adobe continues to evolve by integrating AI capabilities such as ", 
                            html.Strong("Adobe Sensei"), ", which powers intelligent features across its product portfolio. This commitment to cutting-edge technology positions Adobe as a key player in shaping the future of ", 
                            html.Em("digital content creation and management"), "."
                        ]),

                        html.P([
                            "Adobe's leadership, led by CEO ", html.Strong("Shantanu Narayen"), 
                            ", has been instrumental in driving the company's success. Under his guidance, Adobe maintains a reputation for ", 
                            html.Strong("strong financial performance, innovation"), " and ", 
                            html.Em("sustainable growth"), "."
                        ])
                        
                    ],
                        style={
                            'maxHeight': '700px', 
                            'overflowY': 'auto',  
                            'border': '1px solid #ddd',
                            'padding': '10px', 
                            'borderRadius': '5px',
                        }
                    )
                ])
        return list_group

    def render(self):
        row = html.Div(
                [
                    dbc.Row(dbc.Col(html.H4("Fundamental Analysis", className="display-7", style={'font-weight':'bold', 'color':'#d10737'}))),
                    dbc.Row(
                        [
                            dbc.Col([html.Br(), self.card_top("fa fa-industry", "Sector", "Technology Services")], width=3),
                            dbc.Col([html.Br(), self.card_top("fa fa-cogs", "Industry", "Packaged Software")], width=3),
                            dbc.Col([html.Br(), self.card_top("fa fa-user-tie", "CEO", "Shantanu Narayen, MBA")], width=3),
                            dbc.Col([html.Br(), self.card_top("fa fa-users", "Employees", "29 945")], width=3),
                        ]
                    ),
                    html.Br(),
                    dbc.Row(
                        [ dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [ 
                                dbc.Row([dbc.Col( self.tab )]),
                                ]
                            ),
                        ), width=6),
                            
                            dbc.Col([self.notif_time_line()], width=6),
                        ]
                    ),
                ]
            )
        return row
