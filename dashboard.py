from dash import Dash, html, dcc, dash_table, callback, Input, Output, State
import plotly.express as px
import pandas as pd
from PIL import Image
from dash import callback, Input, Output, State
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pyowm
import base64
from io import BytesIO
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

pil_img = Image.open("logo-blavk.png")
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

owm = pyowm.OWM('fa47fceaf9e211df22cedbb5c4f2b456')  # Substitua pela sua chave real do OWM
mgr = owm.weather_manager()

# Dicionário para armazenar dados
data_dict = {'Measurement': [], 'Mass (1000 x kg)': [], 'Temperature (°C)': [], 'Current Time': []}

# Sample data
dt = {"Measurement": [1, 2, 3, 4, 5, 6, 7, 8],
      "Mass (1000 x kg)": [4, 12, 13, 10, 15, 11, 10, 16]}

df = pd.DataFrame(dt)
fig = px.line(df, x="Measurement", y="Mass (1000 x kg)", markers=True, template='plotly_dark',
              width=1000, height=350, title="Real-time ore pile mass")

# Start the scheduler for updating data every 1 minute
scheduler = BackgroundScheduler()

def get_temperature():
    observation = mgr.weather_at_place("Belo Horizonte,BR")
    w = observation.weather
    return w.temperature('celsius')['temp']

def update_data():
    # Update data_dict with current time, temperature, and random Mass values
    current_time_zero=datetime.now()
    new_time=current_time_zero - timedelta(hours=3)
    current_time = new_time.strftime("%H:%M:%S")
    temperature = get_temperature()
    random_mass = round(np.random.uniform(5, 20), 2)  # Substitua isso pelo seu método real de obtenção de massa aleatória

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
                      width=1000, height=350, title="Real-time ore pile mass")

    # Altera a cor de fundo do novo gráfico para verde claro e o texto para preto
    new_fig.update_layout(plot_bgcolor='lightgreen', paper_bgcolor='lightgreen', font_color='black')

    # Adiciona as linhas de grade do eixo x e y
    new_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='gray')
    new_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='gray')

    # Altera a fonte das letras do gráfico e aumenta o tamanho da fonte
    new_fig.update_layout(font=dict(family="Arial, sans-serif", size=16))

    # Altera a cor da linha do gráfico para preto
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
                    html.Button('Entrar', id='login-button', className='login-button'),
                    html.Div(id='login-output', className='login-output'),
                ]),
            ]),
        ],
        className='login-page',
        style={'height': '100vh', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center',
               'justify-content': 'center'}
    )

def dashboard_layout():
    return html.Div(
        children=[
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

# Inline CSS styles
app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # em milissegundos, atualiza a cada 30 segundos
        n_intervals=0
    ),
    dcc.Interval(
        id='table-interval-component',
        interval=60*1000,  # em milissegundos, atualiza a cada minuto
        n_intervals=0
    ),
    html.Div(id='page-content', style={'max-width': '800px', 'margin': '0 auto'})
])

# Callback for handling login
@app.callback(
    [Output('login-output', 'children'),
     Output('url', 'pathname')],
    [Input('login-button', 'n_clicks')]
)
def handle_login(n_clicks):
    # Replace with your actual authentication logic
    # No lógica de autenticação aqui, apenas redireciona para o dashboard ao clicar no botão
    if n_clicks is not None:
        return 'Login successful!', '/dashboard'

    return '', '/'

# Callback to display the appropriate page based on the URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard_layout()
    else:
        return login_layout()

# Callback to update the data download link
@app.callback(
    Output("download-link", "href"),
    [Input("download-button", "n_clicks")]
)
def download_data(n_clicks):
    if n_clicks:
        df = pd.DataFrame(data_dict)
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        href_value = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}"
        return href_value

# Start the scheduler
scheduler.add_job(update_data, IntervalTrigger(seconds=60), id='update_data_job')
scheduler.start()

if __name__ == '__main__':
    app.run_server(debug=True)
