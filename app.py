import dash
from dash import html, dcc, Input, Output
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
    victoires = [int(s.split("-")[0]) > int(s.split("-")[1]) for s in res["Score"]]
    egalites = [int(s.split("-")[0]) == int(s.split("-")[1]) for s in res["Score"]]
    defaites = [int(s.split("-")[0]) < int(s.split("-")[1]) for s in res["Score"]]

    fig = go.Figure([
        go.Bar(name="Victoires", x=res["Journée"], y=victoires, marker_color="green"),
        go.Bar(name="Égalités", x=res["Journée"], y=egalites, marker_color="yellow"),
        go.Bar(name="Défaites", x=res["Journée"], y=defaites, marker_color="red"),
    ])
    
    # Ajustement de l'axe Y pour éviter les décimales et n'afficher que des entiers
    fig.update_layout(barmode="stack", title="Historique des résultats",
                      xaxis_title="Journée", yaxis_title="Matchs",
                      yaxis=dict(tickmode='array', tickvals=[0, 1, 2, 3]),  # Valeurs entières uniquement
                      margin=dict(l=20, r=20, t=60, b=20))
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
        html.P("FC Laval a connu une saison exceptionnelle cette année, en accumulant un total impressionnant de victoires. "
               "L'équipe a su se maintenir au top avec des performances remarquables, que ce soit en attaque ou en défense. "
               "Nous avons suivi chaque match et analysé les performances pour mieux comprendre l'évolution de l'équipe.",
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
        html.P("Analyse de l'évolution des résultats par journée. Les couleurs indiquent les victoires (vert), les égalités (jaune) et les défaites (rouge).", className="mt-2")
    ]),

    "Performances": html.Div([
        dcc.Graph(figure=get_performances_fig()),
        html.P("Cette graphique montre l'évolution des performances de l'équipe au fil des matchs. "
               "Les lignes indiquent les buts marqués, les buts encaissés, les clean sheets et la différence de buts.",
               className="mt-2")
    ]),
}

# Layout principal
app.layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("Dashboard FC Laval M", href="/"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Accueil", href="/")),
                dbc.NavItem(dbc.NavLink("Heatmap", href="/heatmap")),
                dbc.NavItem(dbc.NavLink("Résultats", href="/resultats")),
                dbc.NavItem(dbc.NavLink("Performances", href="/performances")),
            ])
        ]),
        color="dark", dark=True
    ),
    html.Div(id="page-content")
])

# Navigation
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname in ["/", "/accueil"]:
        return pages["Accueil"]
    elif pathname == "/heatmap":
        return pages["Heatmap"]
    elif pathname == "/resultats":
        return pages["Résultats"]
    elif pathname == "/performances":
        return pages["Performances"]
    else:
        return "404 Page Not Found"

if __name__ == "__main__":
    app.run_server(debug=True)
