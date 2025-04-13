import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# Initialisation de l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# === FIGURES ===

### 🔵 1. HEATMAP DES BUTS ###
df_heatmap = pd.read_excel("Tesst_But.xlsx")
df_pivot = df_heatmap.pivot(index="Joueur", columns="Match", values="Buts").fillna(0)

fig_heatmap = px.imshow(
    df_pivot,
    labels=dict(x="Match", y="Joueur", color="Buts marqués"),
    x=df_pivot.columns,
    y=df_pivot.index,
    color_continuous_scale="Blues"
)
fig_heatmap.update_layout(title="Heatmap des buts par match", dragmode=False)

### 🔴 2. HISTORIQUE RÉSULTATS ###
df_resultats = pd.read_excel("graphe3_data.xlsx")
match_dates = df_resultats["Journée"].tolist()
resultats = df_resultats["Résultat"].tolist()
adversaires = df_resultats["Adversaire"].tolist()
scores = df_resultats["Score"].tolist()

victoires = [1 if r == "Victoire" else 0 for r in resultats]
egalites = [1 if r == "Égalité" else 0 for r in resultats]
defaites = [1 if r == "Défaite" else 0 for r in resultats]

fig_resultats = go.Figure(data=[
    go.Bar(name='Victoires', x=match_dates, y=victoires, marker_color='green'),
    go.Bar(name='Égalités', x=match_dates, y=egalites, marker_color='yellow'),
    go.Bar(name='Défaites', x=match_dates, y=defaites, marker_color='red')
])

annotations = []
for i, date in enumerate(match_dates):
    annotations.append(
        dict(
            x=date,
            y=1,
            text=f"{adversaires[i]}<br>{scores[i]}",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-100,
            font=dict(size=10, color="black"),
            textangle=45
        )
    )

fig_resultats.update_layout(
    title="Historique des Résultats de l'équipe AS Laval M",
    xaxis_title="Journées",
    yaxis_title="Nombre de Résultats",
    barmode="stack",
    template="plotly_white",
    annotations=annotations,
    width=900,
    height=500
)

### 🟢 3. ÉVOLUTION DE PERFORMANCE ###
df_perf = pd.read_excel("graphe4.xlsx")
df_perf.columns = df_perf.columns.str.strip()

fig_perf = px.line(df_perf, x="Journée", y=["Buts Marqués", "Buts Encaissés", "Clean Sheets"],
                   title="Performance de l'équipe sur 20 journées",
                   labels={"value": "Nombre", "variable": "Statistiques"},
                   markers=True)

# === PAGES ===

accueil_layout = html.Div([
    html.H1("🏠 Accueil - Visualisation Ligue 1 du Québec", style={"textAlign": "center", "color": "#2c3e50"}),
    html.P("Bienvenue dans l'application de visualisation de l'équipe AS Laval M. Utilisez le menu pour explorer les statistiques !",
           style={"textAlign": "center", "fontSize": "18px"})
])

heatmap_layout = html.Div([
    html.H2("1️⃣ Heatmap des buts par match", style={"color": "#2980b9"}),
    dcc.Graph(figure=fig_heatmap)
])

resultats_layout = html.Div([
    html.H2("2️⃣ Historique des Résultats", style={"color": "#c0392b"}),
    dcc.Graph(figure=fig_resultats)
])

perf_layout = html.Div([
    html.H2("3️⃣ Évolution des Performances", style={"color": "#27ae60"}),
    dcc.Graph(figure=fig_perf)
])

# === APP LAYOUT AVEC MENU ===

app.layout = html.Div([
    html.Div([
        html.H1("📊 AS Laval M - Tableau de Bord", style={"textAlign": "center", "marginBottom": "20px", "color": "#34495e"}),
        dcc.Location(id='url', refresh=False),
        html.Div([
            dcc.Link("🏠 Accueil", href='/', style={'padding': '10px'}),
            dcc.Link("🔥 Heatmap", href='/heatmap', style={'padding': '10px'}),
            dcc.Link("📅 Résultats", href='/resultats', style={'padding': '10px'}),
            dcc.Link("📈 Performances", href='/performances', style={'padding': '10px'}),
        ], style={"textAlign": "center", "marginBottom": "40px", "backgroundColor": "#ecf0f1", "padding": "10px"}),

        html.Div(id='page-content')
    ], style={"fontFamily": "Arial, sans-serif", "padding": "20px"})
])

# === CALLBACK DE NAVIGATION ===

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/heatmap':
        return heatmap_layout
    elif pathname == '/resultats':
        return resultats_layout
    elif pathname == '/performances':
        return perf_layout
    else:
        return accueil_layout

# === RUN SERVEUR ===

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
