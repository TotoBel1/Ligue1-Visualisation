import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Initialiser l'application Dash
app = dash.Dash(__name__)
server = app.server  # Pour le déploiement sur Render

# --- 1️⃣ Heatmap des buts ---
# Charger les données Excel pour la heatmap
file_path_heatmap = "Tesst_But.xlsx"  # Mets le fichier dans le même dossier que app.py
df_heatmap = pd.read_excel(file_path_heatmap)

# Transformer les données pour la heatmap
df_pivot = df_heatmap.pivot(index="Joueur", columns="Match", values="Buts").fillna(0)

# Créer la heatmap
fig_heatmap = px.imshow(
    df_pivot,
    labels=dict(x="Match", y="Joueur", color="Buts marqués"),
    x=df_pivot.columns,
    y=df_pivot.index,
    color_continuous_scale="Blues"
)
fig_heatmap.update_layout(title="Heatmap des buts par match", dragmode=False)

# --- 2️⃣ Graphique des résultats ---
# Charger les données Excel pour le graphique des résultats
file_path_resultats = "graphe3_data.xlsx"  # Mets le fichier dans le même dossier que app.py
df_resultats = pd.read_excel(file_path_resultats)

# Extraire les données nécessaires
match_dates = df_resultats["Journée"].tolist()
resultats = df_resultats["Résultat"].tolist()
adversaires = df_resultats["Adversaire"].tolist()
scores = df_resultats["Score"].tolist()

# Initialiser les comptages pour les résultats
victoires = [1 if r == "Victoire" else 0 for r in resultats]
egalites = [1 if r == "Égalité" else 0 for r in resultats]
defaites = [1 if r == "Défaite" else 0 for r in resultats]

# Créer le graphique des résultats
fig_resultats = go.Figure(data=[
    go.Bar(name='Victoires', x=match_dates, y=victoires, marker_color='green'),
    go.Bar(name='Égalités', x=match_dates, y=egalites, marker_color='yellow'),
    go.Bar(name='Défaites', x=match_dates, y=defaites, marker_color='red')
])

# Ajouter des annotations pour chaque match
annotations = []
for i, date in enumerate(match_dates):
    annotations.append(
        dict(
            x=date,
            y=1,  # Position de l'annotation
            text=f"{adversaires[i]}<br>{scores[i]}",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-100,  # Ajuste la position de l'annotation
            font=dict(size=10, color="black"),
            textangle=45  # Rotation pour éviter les chevauchements
        )
    )

# Personnalisation du graphique des résultats
fig_resultats.update_layout(
    title='Historique des Résultats de l\'équipe AS Laval M',
    xaxis_title='Journées',
    yaxis_title='Nombre de Résultats',
    barmode='stack',
    template='plotly_white',
    width=900,
    height=500,
    annotations=annotations
)

# --- 3️⃣ Graphique en ligne (Performance sur 20 journées) ---
# Charger les données Excel pour le graphique en ligne
file_path_line = "graphe4.xlsx"  # Mets le fichier dans le même dossier que app.py
df_line = pd.read_excel(file_path_line)

# Nettoyer les colonnes et créer le graphique en ligne
df_line.columns = df_line.columns.str.strip()
fig_line = px.line(
    df_line, 
    x="Journée", 
    y=["Buts Marqués", "Buts Encaissés", "Clean Sheets"],
    title="Performance de l'équipe sur 20 journées",
    labels={"value": "Nombre de buts", "variable": "Statistiques"},
    markers=True
)

# --- Layout de l'application Dash ---
app.layout = html.Div([
    html.H1("Visualisation Ligue 1 Québec ⚽", style={"textAlign": "center"}),

    # Section Heatmap
    html.Div([
        html.H2("🔵 Heatmap des buts marqués", style={"marginTop": "20px"}),
        dcc.Graph(figure=fig_heatmap)
    ], style={"width": "80%", "margin": "auto"}),

    # Section Graphique des résultats
    html.Div([
        html.H2("🟢 Résultats de l'équipe AS Laval M", style={"marginTop": "50px"}),
        dcc.Graph(figure=fig_resultats)
    ], style={"width": "80%", "margin": "auto"}),

    # Section Graphique en ligne
    html.Div([
        html.H2("📊 Performance de l'équipe sur 20 journées", style={"marginTop": "50px"}),
        dcc.Graph(figure=fig_line)
    ], style={"width": "80%", "margin": "auto"}),
])

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)


