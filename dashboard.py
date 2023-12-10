import tzlocal
from packaging import version
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.base import BaseTrigger
from datetime import datetime
import random
import pandas as pd
from dash import Dash, html, dcc, dash_table, callback, Input, Output, State
import plotly.express as px
from PIL import Image
from dash import callback, Input, Output, State
from io import BytesIO

# Ajuste da versão do tzlocal
try:
    tz_version = version.parse(tzlocal.__version__)
    if tz_version.major >= 3:
        print("Versão incompatível do tzlocal. Instalando agora a versão 2.1...")
        os.system("pip install tzlocal==2.1")
except AttributeError:
    # Se não houver atributo __version__, assume-se que a versão seja compatível
    pass

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

pil_img = Image.open("logo-blavk.png")
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

# Dicionário para armazenar dados
data_dict = {'Measurement': [], 'Mass (1000 x kg)': [], 'Temperature (°C)': [], 'Current Time': []}

# Sample data
dt = {"Measurement": [1, 2, 3, 4, 5, 6, 7, 8],
      "Mass (1000 x kg)": [4, 12, 13, 10, 15, 11, 10, 16]}

df = pd.DataFrame(dt)
fig = px.line(df, x="Measurement", y="Mass (1000 x kg)", markers=True, template='plotly_dark',
              width=1000, height=350, title="Real time ore pile mass")
fig.update_layout(title_x=0.5)  # Centraliza o título

# Start the scheduler for updating data every 1 minute
scheduler = BackgroundScheduler(timezone='UTC')


def get_temperature():
    # Replace this with your actual logic to get real-time temperature data
    return round(25 + (datetime.now().second / 60), 2)


def update_data():
    # Update data_dict with current time, temperature, and random Mass values
    current_time = datetime.now().strftime("%H:%M:%S")
    temperature = get_temperature()
    random_mass = random.uniform(5, 20)  # Gerar um valor aleatório entre 5 e 20

    # Verifica se a lista 'Measurement' está vazia
    if data_dict['Measurement']:
        next_time = max(data_dict['Measurement']) + 1
    else:
        next_time = 1

    # Append new data to the dictionary
    data_dict['Measurement'].append(next_time)
    data_dict['Mass (1000 x kg)'].append(random_mass)
    data_dict['Temperature (°C)'].append(temperature)
    data_dict['Current Time'].append(current_time)


# Callback para atualizar dados da tabela e do gráfico
@app.callback(
    [Output('table-virtualization', 'data'),
     Output('example-graph', 'figure')],
    [Input('interval-component', 'n_intervals')])  # Adiciona um novo Input para o intervalo
def update_data_and_graph(n_intervals):
    update_data()

    # Atualizar o gráfico com as novas informações
    new_fig = px.line(pd.DataFrame(data_dict),
                      x="Measurement", y="Mass (1000 x kg)",
                      markers=True, template='plotly_dark',
                      width=1000, height=350, title="Real time ore pile mass")
    new_fig.update_layout(title_x=0.5, plot_bgcolor='lightgreen', paper_bgcolor='lightgreen', font_color='black')
    new_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    new_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    new_fig.update_layout(font=dict(family="Arial, sans-serif", size=16))
    new_fig.update_traces(line=dict(color='black'))

    return pd.DataFrame(data_dict).to_dict('records'), new_fig


def login_layout():
    return html.Div(
        children=[
            html.Div(id='login-container', className='login-container', children=[
                html.Div(children=[
                    html.Img(src=pil_img, style={'height': '20%', 'width': '20%'}),
                    html.H1(children=' Medição de minérios de forma sustentável e inovadora.',
                            style={'color': '#333', 'margin-bottom': '20px'}),
                ]),

                html.Div(id='login-form-container', className='login-form-container', children=[
                    html.Label('Email:', className='login-label'),
                    dcc.Input(id='email-input', type='email', value='', placeholder='Enter your email',
                              className='login-input', style={'width': '100%'}),
                    html.Label('Password:', className='login-label'),
                    dcc.Input(id='password-input', type='password', value='', placeholder='Enter your password',
                              className='login-input', style={'width': '100%'}),
                    html.Button('Login', id='login-button', n_clicks=0, className='login-button'),
                    html.Div(id='login-output-container', className='login-output-container')
                ])
            ])
        ]
    )


# Layout do aplicativo Dash
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'})
])

# Callback para atualizar a página com base na URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/login':
        return login_layout()
    else:
        return login_layout()


# Executar o aplicativo
if __name__ == '__main__':
    scheduler.add_job(update_data, IntervalTrigger(seconds=60), id='update_data_job')
    scheduler.start()
    app.run_server(debug=True, use_reloader=False)
