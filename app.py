import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Initialisation de l'application Dash
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

    "Résultats": html.Div([
        html.H2("\ud83d\uddd5\ufe0f Historique des résultats"),
        dcc.Graph(figure=go.Figure([
            go.Bar(
                name="Victoires", 
                x=resultats_df["Journée"], 
                y=resultats_df.groupby("Journée")["Victoire"].sum(),
                marker_color="green"
            ),
            go.Bar(
                name="Égalités", 
                x=resultats_df["Journée"], 
                y=resultats_df.groupby("Journée")["Egalite"].sum(),
                marker_color="orange"
            ),
            go.Bar(
                name="Défaites", 
                x=resultats_df["Journée"], 
                y=resultats_df.groupby("Journée")["Defaite"].sum(),
                marker_color="red"
            ),
        ]).update_layout(
            barmode="stack", 
            title="Historique des résultats",
            xaxis_title="Journée",
            yaxis_title="Nombre de Résultats",
            template="plotly_white"
        ))
    ]),

    "Performances": html.Div([
        html.H2("\ud83d\udcc8 \u00c9volution des performances"),
        dcc.Graph(figure=go.Figure([
            go.Scatter(
                x=performances_df["Journée"],
                y=performances_df["Buts Marqués"],
                mode="lines+markers",
                name="Buts Marqués",
                line=dict(color="blue", width=2)
            ),
            go.Scatter(
                x=performances_df["Journée"],
                y=performances_df["Buts Encaissés"],
                mode="lines+markers",
                name="Buts Encaissés",
                line=dict(color="red", width=2)
            ),
            go.Scatter(
                x=performances_df["Journée"],
                y=performances_df["Clean Sheets"],
                mode="lines+markers",
                name="Clean Sheets",
                line=dict(color="green", width=2),
                yaxis="y2"  # Utilisation de l'axe Y secondaire
            ),
        ]).update_layout(
            title="Évolution des performances",
            xaxis_title="Journée",
            yaxis_title="Nombre de Buts",
            yaxis2=dict(
                title="Clean Sheets",
                overlaying="y",  # L'axe Y2 va se superposer à Y
                side="right",    # Positionner l'axe Y2 à droite
                showgrid=False   # Masquer les lignes de la grille de l'axe Y2
            ),
            template="plotly_white"
        ))
    ])
}

# Barre de navigation stylée
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
                dbc.NavLink("Résultats", href="/resultats", id="Résultats-link", active="exact"),
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
        return pages["Résultats"]
    elif pathname == "/performances":
        return pages["Performances"]
    return pages["Accueil"]

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
