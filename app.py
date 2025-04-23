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

# KPI Résumé
def get_kpi_cards():
    total_buts = performances_df["Buts Marqués"].sum()
    clean_sheets = performances_df["Clean Sheets"].sum()
    victoires = sum(int(s.split("-")[0]) > int(s.split("-")[1]) for s in resultats_df["Score"])

    return dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("⚽ Total Buts", className="card-title"),
                                         html.H2(total_buts, className="card-text")])]), md=4),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("🧤 Clean Sheets", className="card-title"),
                                         html.H2(clean_sheets, className="card-text")])]), md=4),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("✅ Victoires", className="card-title"),
                                         html.H2(victoires, className="card-text")])]), md=4),
    ], className="mb-4")

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
    victoires = [int(s.split("-")[0]) > int(s.split("-")[1]) for s in res["Score"]]
    egalites = [int(s.split("-")[0]) == int(s.split("-")[1]) for s in res["Score"]]
    defaites = [int(s.split("-")[0]) < int(s.split("-")[1]) for s in res["Score"]]
    fig = go.Figure([
        go.Bar(name="Victoires", x=res["Journée"], y=victoires, marker_color="green"),
        go.Bar(name="Égalités", x=res["Journée"], y=egalites, marker_color="orange"),
        go.Bar(name="Défaites", x=res["Journée"], y=defaites, marker_color="red"),
    ])
    fig.update_layout(barmode="stack", title="Historique des résultats", 
                      xaxis_title="Journée", yaxis_title="Résultat", 
                      margin=dict(l=20, r=20, t=60, b=20),
                      annotations=[
                          dict(x=10, y=1, text="Série de victoires ici", showarrow=True, arrowhead=1)
                      ])
    return fig

def get_performances_fig():
    df = performances_df.copy()
    fig = go.Figure([
        go.Scatter(x=df["Journée"], y=df["Buts Marqués"], mode="lines+markers", name="Buts Marqués", line=dict(color="green")),
        go.Scatter(x=df["Journée"], y=df["Buts Encaissés"], mode="lines+markers", name="Buts Encaissés", line=dict(color="red")),
        go.Scatter(x=df["Journée"], y=df["Clean Sheets"], mode="lines+markers", name="Clean Sheets", line=dict(color="blue", dash="dot")),
        go.Scatter(x=df["Journée"], y=df["Diff_Buts"], mode="lines+markers", name="Différence", line=dict(color="purple", dash="dash"))
    ])
    fig.update_layout(title="Évolution des performances", xaxis_title="Journée", yaxis_title="Valeurs",
                      margin=dict(l=20, r=20, t=60, b=20))
    return fig

# Mise en page des pages
pages = {
    "Accueil": html.Div([
        html.H2("Bienvenue sur le Dashboard de l'équipe FC Laval M", className="text-center"),
        html.P("Ce tableau de bord vous permet d'explorer les statistiques clés de l'équipe.", className="text-center"),
        html.Img(src="/assets/fclaval_champions.jpeg", style={"width": "25%", "margin": "auto", "display": "block", "borderRadius": "10px"}),
        html.Hr(),
        get_kpi_cards()
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
        html.P("Analyse de l'évolution des résultats par journée.", className="mt-2")
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

if __name__ == "__main__":
    app.run(debug=True, port=8000)
