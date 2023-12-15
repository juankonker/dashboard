from dash import Dash, html
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, redirect, url_for
from flask_dance.contrib.azure import azure, make_azure_blueprint
import os

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
    client_secret="add431f1-e527-48ec-9b5c-049eaddb9ec1",
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

dash_app.layout = html.Div(children=[
  html.H1(children='Hello Dash'),
  html.Div(children="You are logged in!")
])

if __name__ == '__main__':
    dash_app.run_server(debug=True)
