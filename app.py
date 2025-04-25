import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "AS Laval M - Dashboard"
server = app.server

# Chargement des données
heatmap_df = pd.read_excel("Tesst_But.xlsx")
resultats_df = pd.read_excel("graphe3_data.xlsx")
performances_df = pd.read_excel("graphe4.xlsx")

# Nettoyage des données
resultats_df.columns = resultats_df.columns.str.strip()
performances_df.columns = performances_df.columns.str.strip()
if "Buts Marqués" in performances_df.columns and "Buts Encaissés" in performances_df.columns:
    performances_df["Diff_Buts"] = performances_df["Buts Marqués"] - performances_df["Buts Encaissés"]

# Graphiques avec filtres et annotations
def get_heatmap_fig(joueur=None):
    df = heatmap_df.copy()
    if joueur:
        df = df[df["Joueur"] == joueur]
    pivot = df.pivot(index="Joueur", columns="Match", values="Buts").fillna(0)
    fig = px.imshow(pivot, labels={"color": "Buts marqués"}, color_continuous_scale="Blues")
    fig.update_layout(title="Heatmap des buts par joueur", margin=dict(l=20, r=20, t=60, b=20))
    return fig

# Points par match dans la page Résultats
def get_resultats_fig():
    res = resultats_df.copy()

    def points_et_resultat(score):
        try:
            a, b = map(int, score.strip().split("-"))
            if a > b:
                return 3, "Victoire"
            elif a == b:
                return 1, "Égalité"
            else:
                return 0, "Défaite"
        except:
            return 0, "Inconnu"

    res[["Points", "Résultat"]] = res["Score"].apply(
        lambda s: pd.Series(points_et_resultat(s))
    )

    couleur_map = {"Victoire": "#28a745", "Égalité": "#ffc107", "Défaite": "#dc3545"}

    fig = go.Figure()

    for resultat in ["Victoire", "Égalité", "Défaite"]:
        subset = res[res["Résultat"] == resultat]
        fig.add_trace(go.Bar(
            x=subset["Journée"],
            y=subset["Points"],
            name=resultat,
            marker_color=couleur_map[resultat],
            hovertemplate="<b>Journée %{x}</b><br>Résultat: " + resultat + "<br>Points: %{y}<br>Score: %{customdata}",
            customdata=subset["Score"],
        ))

    fig.update_layout(
        barmode="group",
        title="Points par match selon le résultat",
        xaxis_title="Journée",
        yaxis_title="Points obtenus",
        margin=dict(l=20, r=20, t=60, b=40),
        legend=dict(title="Résultat", orientation="h", x=0.5, xanchor="center"),
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font=dict(size=12, color="#555")
    )
    return fig

# Graphique Performances
def get_performances_fig():
    df = performances_df.copy()
    fig = go.Figure([
        go.Scatter(x=df["Journée"], y=df["Buts Marqués"], mode="lines+markers", name="Buts Marqués", line=dict(color="green")),
        go.Scatter(x=df["Journée"], y=df["Buts Encaissés"], mode="lines+markers", name="Buts Encaissés", line=dict(color="red")),
        go.Scatter(x=df["Journée"], y=df["Clean Sheets"], mode="lines+markers", name="Clean Sheets", line=dict(color="blue", dash="dot")),
        go.Scatter(x=df["Journée"], y=df["Diff_Buts"], mode="lines+markers", name="Différence", line=dict(color="purple", dash="dash"))
    ])
    fig.update_layout(title="Évolution des performances", xaxis_title="Journée", yaxis_title="Valeurs",
                      margin=dict(l=20, r=20, t=60, b=20), plot_bgcolor="#f9f9f9", paper_bgcolor="#ffffff")
    return fig

# Pages
pages = {
    "Accueil": html.Div([
        html.H2("Bienvenue sur le Dashboard de l'équipe FC Laval M", className="text-center"),
        html.P("Ce tableau de bord vous permet d'explorer les statistiques clés de l'équipe.", className="text-center"),
        
        # Description détaillée de FC Laval M
        html.H3("À propos de l'équipe FC Laval M", className="text-center mt-4"),
        html.P("L'équipe FC Laval M a eu une saison exceptionnelle avec une détermination sans faille sur chaque match. "
               "Elle a su se distinguer grâce à sa cohésion, son esprit d'équipe et ses stratégies efficaces. "
               "Les joueurs ont montré une belle évolution tout au long de la saison, en accumulant de nombreuses victoires et en faisant preuve "
               "d'une solide défense, notamment grâce à un nombre important de Clean Sheets. "
               "Les performances offensives ont été marquées par des buts décisifs, tandis que la défense a su maintenir une stabilité. "
               "L'équipe a particulièrement brillé lors des matchs cruciaux où elle a su rester calme et concentrée, "
               "atteignant ses objectifs de manière stratégique et en force.", 
               className="text-center"),
        
        html.Img(src="/assets/fclaval_champions.jpeg", style={"width": "25%", "margin": "auto", "display": "block", "borderRadius": "10px"}),
        html.Hr(),
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

# Lancer l'application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)
