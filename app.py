import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
    victoires = [1 if int(s.split("-")[0]) > int(s.split("-")[1]) else 0 for s in res["Score"]]
    egalites = [1 if int(s.split("-")[0]) == int(s.split("-")[1]) else 0 for s in res["Score"]]
    defaites = [1 if int(s.split("-")[0]) < int(s.split("-")[1]) else 0 for s in res["Score"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Victoires", x=res["Journée"], y=victoires, marker_color="#28a745",
                         hovertemplate="Victoire le jour %{x}"))
    fig.add_trace(go.Bar(name="Égalités", x=res["Journée"], y=egalites, marker_color="#ffc107",
                         hovertemplate="Égalité le jour %{x}"))
    fig.add_trace(go.Bar(name="Défaites", x=res["Journée"], y=defaites, marker_color="#dc3545",
                         hovertemplate="Défaite le jour %{x}"))

    fig.update_layout(barmode="stack", title="Historique des résultats",
                      xaxis_title="Journée", yaxis_title="Nombre de matchs",
                      margin=dict(l=20, r=20, t=60, b=20),
                      template="plotly_white",
                      legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
    return fig

def get_performances_fig():
    df = performances_df.copy()
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df["Journée"], y=df["Buts Marqués"], mode="lines+markers", name="Buts Marqués",
                             line=dict(color="#28a745", width=3), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=df["Journée"], y=df["Buts Encaissés"], mode="lines+markers", name="Buts Encaissés",
                             line=dict(color="#dc3545", width=3), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=df["Journée"], y=df["Clean Sheets"], mode="lines+markers", name="Clean Sheets",
                             line=dict(color="#007bff", width=3, dash="dot"), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=df["Journée"], y=df["Diff_Buts"], mode="lines+markers", name="Différence",
                             line=dict(color="#6f42c1", width=3, dash="dash"), marker=dict(size=7)))

    max_diff = df["Diff_Buts"].idxmax()
    fig.add_annotation(x=df["Journée"][max_diff], y=df["Diff_Buts"][max_diff],
                       text="📈 Meilleure diff. de buts", showarrow=True, arrowhead=1)

    fig.update_layout(title="Évolution des performances",
                      xaxis_title="Journée", yaxis_title="Valeurs",
                      margin=dict(l=20, r=20, t=60, b=20),
                      template="plotly_white",
                      legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
    return fig

# Pages
pages = {
    "Accueil": html.Div([  
        html.H2("Bienvenue sur le Dashboard de l'équipe FC Laval M", className="text-center"),
        html.P("Ce tableau de bord vous permet d'explorer les statistiques clés de l'équipe.", className="text-center"),
        
        # Description détaillée de FC Laval M
        html.H3("À propos de l'équipe FC Laval M", className="text-center mt-4"),
        html.P("L'équipe FC Laval M est une équipe de football passionnée et compétitive évoluant dans les ligues régionales du Québec. "
               "Connue pour son esprit d'équipe et sa détermination, l'équipe s'efforce de se distinguer par des performances exceptionnelles à chaque match. "
               "Les joueurs, sous la direction de leur coach expérimenté, allient talent, stratégie et travail acharné pour atteindre leurs objectifs et "
               "remporter des titres. Chaque match est une occasion de repousser leurs limites et de faire briller les couleurs de leur équipe.", 
               className="text-center"),
        
        html.Img(src="/assets/fclaval_champions.jpeg", style={"width": "25%", "margin": "auto", "display": "block", "borderRadius": "10px"}),
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
        html.P("Analyse de l'évolution des résultats par journée avec un visuel amélioré.", className="mt-2")
    ]),

    "Performances": html.Div([
        dcc.Graph(figure=get_performances_fig()),
        html.P("Vue d'ensemble des performances offensives et défensives de l'équipe avec points clés surlignés.", className="mt-2")
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
