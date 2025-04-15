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

# Pages du dashboard
pages = {
    "Accueil": html.Div([
        html.H2("Bienvenue sur le tableau de bord de l'équipe FS Laval M !", style={"textAlign": "center"}),
        html.P("Utilisez le menu ci-dessus pour explorer les statistiques.", style={"textAlign": "center"}),

        html.Hr(),
        html.H3("🏆 FC Laval - Champions de la Ligue1 Québec 2024", style={"textAlign": "center"}),

        html.Img(
            src="/assets/fclaval_champions.jpeg",
            style={"display": "block", "margin": "auto", "width": "25%", "borderRadius": "10px", "marginBottom": "20px"}
        ),

        html.P(
            "Le FC Laval a remporté le championnat masculin de la Ligue1 Québec pour la deuxième fois de sa jeune histoire. "
            "Les Lavallois ont confirmé ce titre en août 2024, à la suite d’une victoire 1-0 contre le CS Mont-Royal Outremont. "
            "Grâce à une fiche impressionnante de 12 victoires, 3 nuls et seulement 3 défaites, le club a dominé la saison. "
            "Ce tableau de bord permet de revivre et analyser cette saison exceptionnelle à travers plusieurs indicateurs de performance.",
            style={"textAlign": "justify", "margin": "0 10%"}
        )
    ]),

    "Heatmap": html.Div([
        html.H2("📊 Heatmap des buts par match", style={"textAlign": "center"}),

        dcc.Graph(figure=px.imshow(
            heatmap_df.pivot(index="Joueur", columns="Match", values="Buts").fillna(0),
            labels=dict(x="Match", y="Joueur", color="Buts marqués"),
            color_continuous_scale="Blues"
        )),

        html.Img(
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/FC_Laval_logo_2023.svg/1200px-FC_Laval_logo_2023.svg.png",
            style={
                "width": "200px",
                "display": "block",
                "margin": "20px auto",
                "borderRadius": "10px",
                "boxShadow": "0 4px 8px rgba(0,0,0,0.2)"
            }
        ),

        html.Hr(),

        html.P(
            "Cette heatmap illustre le nombre de buts marqués par chaque joueur lors de chaque match de la saison.",
            style={"textAlign": "justify", "margin": "10px 15%", "fontSize": "16px"}
        ),
        html.P(
            "Elle permet d’identifier rapidement les joueurs clés en attaque, et les périodes de forme ou de titularisation.",
            style={"textAlign": "justify", "margin": "10px 15%", "fontSize": "16px"}
        ),
        html.P(
            "Ceci est juste un exemple des joueurs principaux(joueurs clés) de FC laval, on essayera de mettre les données de tout les autres joueurs à la remise finale",
            style={"textAlign": "justify", "margin": "10px 15%", "fontSize": "16px"}
        )
    ]),

    "Résultats": html.Div([
        html.H2("🕵️‍♂️ Historique des résultats", style={"textAlign": "center"}),

        dcc.Graph(figure=go.Figure([
            go.Bar(name="Victoires", x=resultats_df["Journée"],
                   y=[int(s.split("-")[0]) > int(s.split("-")[1]) for s in resultats_df["Score"]],
                   marker_color="green"),
            go.Bar(name="Égalités", x=resultats_df["Journée"],
                   y=[int(s.split("-")[0]) == int(s.split("-")[1]) for s in resultats_df["Score"]],
                   marker_color="orange"),
            go.Bar(name="Défaites", x=resultats_df["Journée"],
                   y=[int(s.split("-")[0]) < int(s.split("-")[1]) for s in resultats_df["Score"]],
                   marker_color="red"),
        ]).update_layout(barmode="stack", title="Résultats de l'équipe par journée",
                         xaxis_title="Journée", yaxis_title="Résultat (1=True, 0=False)")),

        html.Hr(),
        html.P(
            "Ce graphique montre la dynamique des résultats (victoires, égalités, défaites) par journée.",
            style={"textAlign": "justify", "margin": "0 10%"}
        ),
        html.P(
            "Il permet d'observer les séries de bonnes performances ou de passages plus difficiles.",
            style={"textAlign": "justify", "margin": "0 10%"}
        )
    ]),

    "Performances": html.Div([
        html.H2("📈 Évolution des performances", style={"textAlign": "center"}),

        dcc.Graph(figure=go.Figure([
            go.Scatter(x=performances_df["Journée"], y=performances_df["Buts Marqués"],
                       mode="lines+markers", name="Buts Marqués", line=dict(color="green")),
            go.Scatter(x=performances_df["Journée"], y=performances_df["Buts Encaissés"],
                       mode="lines+markers", name="Buts Encaissés", line=dict(color="red")),
            go.Scatter(x=performances_df["Journée"], y=performances_df["Clean Sheets"],
                       mode="lines+markers", name="Clean Sheets", line=dict(color="blue", dash="dot")),
            go.Scatter(x=performances_df["Journée"], y=performances_df["Diff_Buts"],
                       mode="lines+markers", name="Différence de Buts", line=dict(color="purple", dash="dash"))
        ]).update_layout(
            title="Évolution des performances par journée",
            xaxis_title="Journée",
            yaxis_title="Nombre",
            legend_title="Indicateurs"
        )),

        html.Hr(),
        html.P(
            "Ce graphique réunit les indicateurs de performance clés : buts marqués, encaissés, clean sheets, et différence de buts.", 
            style={"textAlign": "justify", "margin": "0 10%"}
        ),
        html.P(
            "Il permet d’analyser le rapport attaque/défense, la stabilité défensive, et la tendance des performances.Une différence de buts positive et croissante indique une équipe bien en place et en confiance",
            style={"textAlign": "justify", "margin": "0 10%"}
        ),
    ])
}

# Barre de navigation
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
    html.Div(id="page-content", style={"padding": "20px"})
])

# Callback de routage
@callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    print("URL détectée :", pathname)  # Pour debug
    if pathname == "/heatmap":
        return pages["Heatmap"]
    elif pathname == "/resultats":
        return pages["Résultats"]
    elif pathname == "/performances":
        return pages["Performances"]
    return pages["Accueil"]

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
