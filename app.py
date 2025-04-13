import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "AS Laval M - Dashboard"
server = app.server

# Chargement des données
heatmap_df = pd.read_excel("Tesst_But.xlsx")
resultats_df = pd.read_excel("graphe3_data.xlsx")
performances_df = pd.read_excel("graphe4.xlsx")
performances_df.columns = performances_df.columns.str.strip()

# Définition des pages
pages = {
    "Accueil": html.Div([
        html.H2("Bienvenue sur le tableau de bord de l'\u00e9quipe AS Laval M !", style={"textAlign": "center"}),
        html.P("Utilisez le menu ci-dessus pour explorer les statistiques.", style={"textAlign": "center"})
    ]),

    "Heatmap": html.Div([
        html.H2("\ud83d\udcca Heatmap des buts par match"),
        dcc.Graph(figure=px.imshow(
            heatmap_df.pivot(index="Joueur", columns="Match", values="Buts").fillna(0),
            labels=dict(x="Match", y="Joueur", color="Buts marqu\u00e9s"),
            color_continuous_scale="Blues"
        ))
    ]),

    "R\u00e9sultats": html.Div([
        html.H2("\ud83d\uddd5\ufe0f Historique des r\u00e9sultats"),
        dcc.Graph(figure=go.Figure([
            go.Bar(name="Victoires", x=resultats_df["Journ\u00e9e"],
                   y=[1 if r == "Victoire" else 0 for r in resultats_df["R\u00e9sultat"]], marker_color="green"),
            go.Bar(name="\u00c9galit\u00e9s", x=resultats_df["Journ\u00e9e"],
                   y=[1 if r == "\u00c9galit\u00e9" else 0 for r in resultats_df["R\u00e9sultat"]], marker_color="orange"),
            go.Bar(name="D\u00e9faites", x=resultats_df["Journ\u00e9e"],
                   y=[1 if r == "D\u00e9faite" else 0 for r in resultats_df["R\u00e9sultat"]], marker_color="red"),
        ]).update_layout(barmode="stack", title="Historique des r\u00e9sultats"))
    ]),

    "Performances": html.Div([
        html.H2("\ud83d\udcc8 \u00c9volution des performances"),
        dcc.Graph(figure=px.line(
            performances_df,
            x="Journ\u00e9e",
            y=["Buts Marqu\u00e9s", "Buts Encaiss\u00e9s", "Clean Sheets"],
            markers=True,
            title="\u00c9volution des performances"
        ))
    ])
}

# Barre de navigation styl\u00e9e
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.Img(src="https://img.icons8.com/color/48/combo-chart--v1.png", height="30px")),
                dbc.Col(html.Div("AS Laval M - Tableau de Bord", className="navbar-title")),
            ], align="center", className="g-2"),
            href="/",
            style={"textDecoration": "none"},
        ),
        dbc.Nav(
            [
                dbc.NavLink("Accueil", href="/", id="Accueil-link", active="exact"),
                dbc.NavLink("Heatmap", href="/heatmap", id="Heatmap-link", active="exact"),
                dbc.NavLink("R\u00e9sultats", href="/resultats", id="R\u00e9sultats-link", active="exact"),
                dbc.NavLink("Performances", href="/performances", id="Performances-link", active="exact"),
            ],
            className="ml-auto",
            navbar=True,
        )
    ]),
    color="light",
    dark=False,
    className="shadow-sm mb-4"
)

# Layout principal
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    html.Div(id="page-content", style={"padding": "20px"})
])

@callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/heatmap":
        return pages["Heatmap"]
    elif pathname == "/resultats":
        return pages["R\u00e9sultats"]
    elif pathname == "/performances":
        return pages["Performances"]
    return pages["Accueil"]

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
