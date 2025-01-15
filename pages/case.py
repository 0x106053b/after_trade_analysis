import dash
from dash import html

dash.register_page(__name__, path='/case')

layout = html.Div(
    [
        html.P("Case Page!")
    ]
)