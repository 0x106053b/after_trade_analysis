import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "assets"], use_pages=True)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#F5F5F5",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("2020s KBO Trading Analysis", className="display-4"),
        html.Hr(),
        html.P("Is the player doing well after leaving the team?", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Team Analysis", href="/team", active="exact"),
                dbc.NavLink("Case Analysis", href="/case", active="exact")
            ],
            vertical=True,
            pills=True
        )
    ],
    style=SIDEBAR_STYLE
)

content = html.Div(
    [dash.page_container],
    id="page-content",
    style=CONTENT_STYLE
)

app.layout = html.Div(
    [
        dcc.Location(id="url"), sidebar, content
    ],
    style={"display" : "flex"}
)


if __name__ == '__main__':
    app.run(debug=True)