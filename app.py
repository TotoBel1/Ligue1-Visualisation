import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "AS Laval M - Dashboard"
server = app.server

# Chargement des données
resultats_df = pd.read_excel("graphe3_data.xlsx")

# Nettoyage des données
resultats_df.columns = resultats_df.columns.str.strip()

# Fonction pour calculer les points de chaque match
def calculer_points(score):
    if int(score.split("-")[0]) > int(score.split("-")[1]):
        return 3, 0, 0  # Victoire = 3 points
    elif int(score.split("-")[0]) == int(score.split("-")[1]):
        return 1, 0, 0  # Égalité = 1 point
    else:
        return 0, 0, 1  # Défaite = 0 point

# Appliquer la fonction pour calculer les points
resultats_df["Victoire"], resultats_df["Egalite"], resultats_df["Defaite"] = zip(*resultats_df["Score"].apply(calculer_points))

# Graphique des résultats
def get_resultats_fig():
    res = resultats_df.copy()
    
    # Calcul des points pour chaque résultat
    fig = go.Figure([
        go.Bar(
            name="Victoire", 
            x=res["Journée"], 
            y=res["Victoire"], 
            marker_color="green",
            hoverinfo="x+y+name"
        ),
        go.Bar(
            name="Égalité", 
            x=res["Journée"], 
            y=res["Egalite"], 
            marker_color="yellow",
            hoverinfo="x+y+name"
        ),
        go.Bar(
            name="Défaite", 
            x=res["Journée"], 
            y=res["Defaite"], 
            marker_color="red",
            hoverinfo="x+y+name"
        ),
    ])

    # Mise en page
    fig.update_layout(
        title="Résultats de l'équipe par journée",
        xaxis_title="Journée",
        yaxis_title="Nombre de matchs",
        barmode="stack",  # On empile les barres pour chaque journée
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title="Résultats",
        annotations=[
            dict(x=5, y=2, text="Victoire", showarrow=True, arrowhead=1, font=dict(size=12, color="green")),
            dict(x=5, y=1, text="Égalité", showarrow=True, arrowhead=1, font=dict(size=12, color="yellow")),
            dict(x=5, y=0, text="Défaite", showarrow=True, arrowhead=1, font=dict(size=12, color="red"))
        ]
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

    "Résultats": html.Div([
        dcc.Graph(figure=get_resultats_fig()),
        html.P("Analyse des victoires, égalités et défaites de l'équipe sur chaque journée.", className="mt-2")
    ]),
}

# Navbar
navbar = dbc.NavbarSimple(
    brand="AS Laval M - Tableau de Bord",
    brand_href="/",
    color="light",
    dark=False,
    children=[
        dbc.NavItem(dbc.NavLink("Accueil", href="/")),
        dbc.NavItem(dbc.NavLink("Résultats", href="/resultats")),
    ]
)

# Layout
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    dbc.Container(id="page-content", style={"paddingTop": "30px"})
])

# Callback routing
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname == "/resultats":
        return pages["Résultats"]
    return pages["Accueil"]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)
