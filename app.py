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

# Nettoyage des colonnes
resultats_df.columns = resultats_df.columns.str.replace(r"\s+", " ", regex=True).str.strip()
performances_df.columns = performances_df.columns.str.replace(r"\s+", " ", regex=True).str.strip()

# Ajout de la colonne Différence de buts
if "Buts Marqués" in performances_df.columns and "Buts Encaissés" in performances_df.columns:
    performances_df["Diff_Buts"] = performances_df["Buts Marqués"] - performances_df["Buts Encaissés"]

if "Buts Marqués" in resultats_df.columns and "Buts Encaissés" in resultats_df.columns:
    resultats_df["Diff_Buts"] = resultats_df["Buts Marqués"] - resultats_df["Buts Encaissés"]

# Fonctions de figures protégées

def get_heatmap_fig():
    try:
        return px.imshow(
            heatmap_df.pivot(index="Joueur", columns="Match", values="Buts").fillna(0),
            labels=dict(x="Match", y="Joueur", color="Buts marqués"),
            color_continuous_scale="Blues"
        )
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erreur: {e}", showarrow=False, x=0.5, y=0.5)
        return fig

def get_resultats_fig():
    try:
        return go.Figure([
            go.Bar(name="Victoires", x=resultats_df["Journée"],
                   y=[int(s.split("-")[0]) > int(s.split("-")[1]) for s in resultats_df["Score"]], marker_color="green"),
            go.Bar(name="Égalités", x=resultats_df["Journée"],
                   y=[int(s.split("-")[0]) == int(s.split("-")[1]) for s in resultats_df["Score"]], marker_color="orange"),
            go.Bar(name="Défaites", x=resultats_df["Journée"],
                   y=[int(s.split("-")[0]) < int(s.split("-")[1]) for s in resultats_df["Score"]], marker_color="red"),
        ]).update_layout(barmode="stack", title="Résultats de l'équipe par journée",
                         xaxis_title="Journée", yaxis_title="Résultat (1=True, 0=False)")
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erreur: {e}", showarrow=False, x=0.5, y=0.5)
        return fig

def get_performances_fig():
    try:
        return go.Figure([
            go.Scatter(x=performances_df["Journée"], y=performances_df["Buts Marqués"],
                       mode="lines+markers", name="Buts Marqués", line=dict(color="green")),
            go.Scatter(x=performances_df["Journée"], y=performances_df["Buts Encaissés"],
                       mode="lines+markers", name="Buts Encaissés", line=dict(color="red")),
            go.Scatter(x=performances_df["Journée"], y=performances_df["Clean Sheets"],
                       mode="lines+markers", name="Clean Sheets", line=dict(color="blue", dash="dot")),
            go.Scatter(x=performances_df["Journée"], y=performances_df["Diff_Buts"],
                       mode="lines+markers", name="Différence de Buts", line=dict(color="purple", dash="dash"))
        ]).update_layout(title="Évolution des performances",
                         xaxis_title="Journée", yaxis_title="Nombre", legend_title="Indicateurs")
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erreur: {e}", showarrow=False, x=0.5, y=0.5)
        return fig

# Pages
pages = {
    "Accueil": dbc.Card([
        dbc.CardHeader(html.H2("Bienvenue sur le tableau de bord de l'équipe FC Laval M !", className="text-center")),
        dbc.CardBody([
            html.P("Utilisez le menu ci-dessus pour explorer les statistiques.", className="text-center"),
            html.Hr(),
            html.H3("\ud83c\udfc6 FC Laval - Champions de la Ligue1 Québec 2024", className="text-center"),
            html.Img(src="/assets/fclaval_champions.jpeg", style={"display": "block", "margin": "auto", "width": "25%", "borderRadius": "10px"}),
            html.P("Le FC Laval a remporté...", style={"textAlign": "justify", "margin": "0 10%"})
        ])
    ], className="mb-4 shadow-sm rounded"),

    "Heatmap": dbc.Card([
        dbc.CardHeader(html.H2("\ud83d\udcca Heatmap des buts par match", className="text-center")),
        dbc.CardBody([
            dcc.Graph(figure=get_heatmap_fig()),
            html.P("Cette heatmap montre le nombre de buts...", style={"textAlign": "justify", "margin": "0 10%"}),
        ])
    ], className="mb-4 shadow-sm rounded"),

    "Résultats": dbc.Card([
        dbc.CardHeader(html.H2("\ud83d\udd75\ufe0f\u200d Historique des résultats", className="text-center")),
        dbc.CardBody([
            dcc.Graph(figure=get_resultats_fig()),
            html.P("Ce graphique montre les résultats par match...", style={"textAlign": "justify", "margin": "0 10%"})
        ])
    ], className="mb-4 shadow-sm rounded"),

    "Performances": dbc.Card([
        dbc.CardHeader(html.H2("\ud83d\udcc8 Évolution des performances", className="text-center")),
        dbc.CardBody([
            dcc.Graph(figure=get_performances_fig()),
            html.P("Ce graphique montre l’évolution...", style={"textAlign": "justify", "margin": "0 10%"})
        ])
    ], className="mb-4 shadow-sm rounded")
}

# Barre de navigation
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.Img(src="https://img.icons8.com/color/48/combo-chart--v1.png", height="30px")),
                dbc.Col(html.Div("AS Laval M - Tableau de Bord", className="navbar-title")),
            ], align="center"),
            href="/",
            style={"textDecoration": "none"},
        ),
        dbc.Nav([
            dbc.NavLink("Accueil", href="/", id="Accueil-link", active="exact"),
            dbc.NavLink("Heatmap", href="/heatmap", id="Heatmap-link", active="exact"),
            dbc.NavLink("Résultats", href="/resultats", id="Résultats-link", active="exact"),
            dbc.NavLink("Performances", href="/performances", id="Performances-link", active="exact"),
        ], className="ml-auto", navbar=True)
    ]),
    color="light",
    dark=False,
    className="shadow-sm mb-4"
)

# Layout principal
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    dbc.Container(id="page-content", style={"paddingTop": "20px"}, fluid=False),
    html.Footer("Projet réalisé par Ton Nom - M.Sc.A Génie Info - Polytechnique Montréal", 
                style={"textAlign": "center", "padding": "20px", "fontSize": "14px", "color": "#888"})
])

# Routing callback
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
    app.run(debug=True, host="0.0.0.0", port=8000)
