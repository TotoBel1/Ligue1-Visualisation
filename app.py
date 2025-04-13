import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os  # N'oublie pas d'importer os

# Initialisation de l'application Dash
app = dash.Dash(__name__)
server = app.server  # Nécessaire pour Render

# Exemple de graphique (ajuste-le à ton projet)
df = pd.DataFrame({
    "x": [1, 2, 3],
    "y": [4, 5, 6]
})
fig = px.line(df, x="x", y="y")

# Mise en page de l'application
app.layout = html.Div([
    html.H1("Exemple de graphique"),
    dcc.Graph(figure=fig)
])

# Démarrer l'application avec la configuration du port de Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Utiliser le port spécifié par Render (ou 8050 par défaut)
    app.run(host='0.0.0.0', port=port, debug=False)  # Utiliser app.run à la place de app.run_server



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

### 🌐 LAYOUT DE L'APP ###
app.layout = html.Div([
    html.H1("Visualisation de la Ligue 1 du Québec - AS Laval M", style={"textAlign": "center"}),

    html.Div([
        html.H2("1️⃣ Heatmap des buts par match"),
        dcc.Graph(figure=fig_heatmap)
    ], style={"marginBottom": "50px"}),

    html.Div([
        html.H2("2️⃣ Historique des Résultats"),
        dcc.Graph(figure=fig_resultats)
    ], style={"marginBottom": "50px"}),

    html.Div([
        html.H2("3️⃣ Évolution des performances"),
        dcc.Graph(figure=fig_perf)
    ])
])

if __name__ == "__main__":
    app.run()
