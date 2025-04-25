import dash
from dash import html, dcc, Input, Output, callback
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

# Nettoyage
resultats_df.columns = resultats_df.columns.str.strip()
performances_df.columns = performances_df.columns.str.strip()
if "Buts Marqués" in performances_df.columns and "Buts Encaissés" in performances_df.columns:
    performances_df["Diff_Buts"] = performances_df["Buts Marqués"] - performances_df["Buts Encaissés"]

# Graphes avec filtres et annotations
def get_heatmap_fig(joueur=None):
    df = heatmap_df.copy()
    if joueur:
        df = df[df["Joueur"] == joueur]
    pivot = df.pivot(index="Joueur", columns="Match", values="Buts").fillna(0)
    fig = px.imshow(pivot, labels={"color": "Buts marqués"}, color_continuous_scale="Blues")
    fig.update_layout(title="Heatmap des buts par joueur", margin=dict(l=20, r=20, t=60, b=20))
    return fig

def get_resultats_fig():
    res = resultats_df.copy()
    points = []
    for score in res["Score"]:
        if int(score.split("-")[0]) > int(score.split("-")[1]):
            points.append(3)  # Victoire = 3 points
        elif int(score.split("-")[0]) == int(score.split("-")[1]):
            points.append(1)  # Égalité = 1 point
        else:
            points.append(0)  # Défaite = 0 points
    
    fig = go.Figure([go.Bar(
        name="Points par match", x=res["Journée"], y=points, marker_color="blue")])

    fig.update_layout(
        barmode="stack", 
        title="Points par match de l'équipe",
        xaxis_title="Journée", 
        yaxis_title="Points",
        margin=dict(l=20, r=20, t=60, b=20),
        annotations=[
            dict(x=10, y=3, text="Série de victoires ici", showarrow=True, arrowhead=1)
        ]
    )
    return fig

def get_performances_fig():
    df = performances_df.copy()
    fig = go.Figure([
        go.Scatter(x=df["Journée"], y=df["Buts Marqués"], mode="lines+markers", name="Buts Marqués", line=dict(color="green")),
        go.Scatter(x=df["Journée"], y=df["Buts Encaissés"], mode="lines+markers", name="Buts Encaissés", line=dict(color="red")),
        go.Scatter(x=df["Journée"], y=df["Clean Sheets"], mode="lines+markers", name="Clean Sheets", line=dict(color="blue", dash="dot")),
        go.Scatter(x=df["Journée"], y=df["Diff_Buts"], mode="lines+markers", name="Différence", line=dict(color="purple", dash="dash"))
    ])
    fig.update_layout(
        title="Évolution des performances", 
        xaxis_title="Journée", 
        yaxis_title="Valeurs",
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig

# Mise en page des pages
pages = {
    "Accueil": html.Div([
        html.H2("Bienvenue sur le Dashboard de l'équipe FC Laval M", className="text-center"),
        html.P(
            """L'équipe FC Laval M a connu une saison remarquable en Ligue 1 du Québec. 
            Grâce à un travail d'équipe exceptionnel, l'équipe a su surmonter les défis et 
            se démarquer par sa cohésion sur le terrain. En cumulant plusieurs victoires 
            impressionnantes, FC Laval M a été une équipe redoutable tout au long de la saison. 
            Découvrez ci-dessous les performances et résultats détaillés de l'équipe pour cette saison.""",
            className="text-center"
        ),
        html.Img(
            src="/assets/fclaval_champions.jpeg", 
            style={"width": "25%", "margin": "auto", "display": "block", "borderRadius": "10px"}
        ),
        html.Hr()
    ]),

    "Heatmap": html.Div([
        html.H4("Filtrer par joueur :"),
        dcc.Dropdown(
            options=[{"label": j, "value": j} for j in sorted(heatmap_df["Joueur"].unique())],
            id="joueur-dropdown", placeholder="Choisir un joueur"
        ),
        dcc.Graph(id="heatmap-graph"),
        html.P("Cette heatmap montre les performances individuelles des joueurs par match.", className="mt-2")
    ]),

    "Résultats": html.Div([
        dcc.Graph(figure=get_resultats_fig()),
        html.P("Analyse des points par match de l'équipe sur chaque journée.", className="mt-2")
    ]),

    "Performances": html.Div([
        dcc.Graph(figure=get_performances_fig()),
        html.P("Vue d'ensemble des performances offensives et défensives de l'équipe.", className="mt-2")
    ])
}

# Navbar
navbar = dbc.NavbarSimple(
    brand="AS Laval M - Tableau de Bord",
    brand_href="/",
    color="light",
    dark=False,
    children=[
        dbc.NavItem(dbc.NavLink("Accueil", href="/")),
        dbc.NavItem(dbc.NavLink("Heatmap", href="/heatmap")),
        dbc.NavItem(dbc.NavLink("Résultats", href="/resultats")),
        dbc.NavItem(dbc.NavLink("Performances", href="/performances")),
    ]
)

# Layout
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    dbc.Container(id="page-content", style={"paddingTop": "30px"})
])

# Callback routing
@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname == "/heatmap":
        return pages["Heatmap"]
    elif pathname == "/resultats":
        return pages["Résultats"]
    elif pathname == "/performances":
        return pages["Performances"]
    return pages["Accueil"]

# Callback pour heatmap dynamique
@callback(
    Output("heatmap-graph", "figure"),
    Input("joueur-dropdown", "value")
)
def update_heatmap(joueur):
    return get_heatmap_fig(joueur)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)
