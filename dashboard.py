from dash import Dash, html, dash_table, dcc
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, redirect, url_for
from flask_dance.contrib.azure import azure, make_azure_blueprint
import os
from PIL import Image
import numpy as np
import pandas as pd
import plotly.express as px

if 'OAUTHLIB_INSECURE_TRANSPORT' not in os.environ:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def login_required(func):
    """Require a login for the given view function."""

    def check_authorization(*args, **kwargs):
        if not azure.authorized or azure.token.get("expires_in") < 0:
            return redirect(url_for("azure.login"))
        else:
            return func(*args, **kwargs)

    return check_authorization

blueprint = make_azure_blueprint(
    client_id="832378f7-5fee-4713-af36-a88afc95c134",
    client_secret="wa48Q~WEShjsG6qZntEIuu~h-4B.Cnb5Iu2n1aTD",
    tenant="6495f1e2-0d47-4be2-826d-bef88fc09df3",
    scope=["openid", "email", "profile"],
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "9P39loaIYctJ"
app.register_blueprint(blueprint, url_prefix="/login")

dash_app = Dash(__name__, server=app)

# use this in your production environment since you will otherwise run into problems
# https://flask-dance.readthedocs.io/en/v0.9.0/proxies.html#proxies-and-https
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

for view_func in app.view_functions:
    if not view_func.startswith("azure"):
        app.view_functions[view_func] = login_required(app.view_functions[view_func])

pil_img = Image.open("logo-blavk.png")
data_dict = {'Measurement': [], 'Mass (1000 x kg)': [], 'Temperature (°C)': [], 'Current Time': []}

# Sample data
dt = {"Measurement": [1, 2, 3, 4, 5, 6, 7, 8],
      "Mass (1000 x kg)": [4, 12, 13, 10, 15, 11, 10, 16]}

df = pd.DataFrame(dt)
fig = px.line(df, x="Measurement", y="Mass (1000 x kg)", markers=True, template='plotly_dark',
              width=1000, height=350, title="Real-time ore pile mass")
dash_app.layout = html.Div(children=[
                html.Div(id='sidebar', className='sidebar',
                     style={
                         'position': 'fixed',
                         'top': 0,
                         'left': 0,
                         'width': '250px',
                         'height': '100%',
                         'background-color': 'black',
                         'padding': '20px',
                         'color': 'white',
                     },
                     children=[
                         html.Img(src=Image.open("dashboard.png"), style={'height': '20%', 'width': '110%'}),
                         html.H3(f"Welcome,", style={'font-size': '20px'}),
                         html.H4("Guest", style={'font-size': '17px'}),  # Placeholder for the user's name
                         html.A(
                             html.Button("Download Data", id="download-button"),
                             id="download-link",
                             download="data.xlsx",
                             href="",
                             target="_blank",
                             style={'margin-top': '20px'}
                         ),
                         html.A(
                             html.Button("Logout", id="logout-button"),
                             href="/",  # Redirects to the login page
                             style={'margin-top': '20px'}
                         ),
                         # Add more content to the sidebar as needed
                     ],
            ),
            html.Div(
                id='info-container',
                className='info-container',
                style={'flex': 1, 'margin-left': '250px'},  # Mover a tabela e o gráfico para a direita
                children=[
                    dash_table.DataTable(
                        id='table-virtualization',
                        columns=[
                            {'name': 'Measurement', 'id': 'Measurement'},
                            {'name': 'Mass (1000 x kg)', 'id': 'Mass (1000 x kg)'},
                            {'name': 'Temperature (°C)', 'id': 'Temperature (°C)'},
                            {'name': 'Current Time', 'id': 'Current Time'}
                        ],
                        data=pd.DataFrame(data_dict).to_dict('records'),
                        style_cell={'textAlign': 'center', 'minWidth': '100px', 'font_size': '18px',
                                    'font_family': 'Arial, sans-serif'},
                        style_table={'height': 250, 'width': 1000, 'overflowY': 'auto'},
                        fixed_rows={'headers': True, 'data': 0},  # Torna apenas os headers fixos
                        virtualization=True,
                        page_action='none',
                        style_header={'backgroundColor': 'lightgreen', 'color': 'black', 'font_size': '20px',
                                      'font_family': 'Arial, sans-serif'},
                        style_as_list_view=True
                    ),
                    dcc.Graph(id='example-graph', figure=fig),
                ],
            ),
        ],
        className='dashboard-page',
        style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center',
               'margin-top': '20px'}
    )


if __name__ == '__main__':
    dash_app.run_server(debug=True)
