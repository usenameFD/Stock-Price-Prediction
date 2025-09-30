from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime


INDEX_CONFIG = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Adobe Price Prophet</title>
        <link rel="icon" type="image/png" href="https://static.cdnlogo.com/logos/a/90/adobe.png">  <!-- Référence à votre favicon -->
        {%metas%}
        {%css%}
    </head>
    <body>
        <!--[if IE]><script>
        alert("Dash v2.7+ does not support Internet Explorer. Please use a newer browser.");
        </script><![endif]-->
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

class Menu:
    def __init__(self, path):
        self.path = path
        self.SIDEBAR_STYLE = {
                "position": "fixed",
                "top": 0,
                "left": 0,
                "bottom": 0,
                "width": "16rem",
                "padding": "2rem 1rem",
                "background-color": "#f8f9fa",
            }
    def get_current_year(self):
        return datetime.now().year
    
    def render(self):
        return html.Div(
                [   dbc.CardImg(src="https://static.cdnlogo.com/logos/a/90/adobe.png", top=True),
                 
                    html.H4("Stock Price", className="display-6", style={'font-weight':'bold'}),
                    html.Hr(),
                    html.P(
                        "Adobe Prediction", className="lead", style={'text-align':'center'}
                    ),
                    html.Br(),
                    dbc.Nav(
                        [
                            dbc.NavLink("Fundamental Analysis", href=f"{self.path}", active="exact"),
                            dbc.NavLink("Technical Analysis", href=f"{self.path}techn", active="exact"),
                            dbc.NavLink("Model Adobe Deployed", href=f"{self.path}model", active="exact"),
                            dbc.NavLink("Calibration by News", href=f"{self.path}calibration", active="exact"),
                        ],
                        vertical=True,
                        pills=True,
                    ),
                     html.Footer(f"© {self.get_current_year()} 3A ENSAI", style={'text-align': 'center', 'position': 'absolute', 'color':'#d10737', 'font-weight':'bold',
                                                                                 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 
                                                                                 'width': '100%', 'margin': 'auto'})
                ],
                style=self.SIDEBAR_STYLE,
            )
