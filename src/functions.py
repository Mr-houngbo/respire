import streamlit as st
import pandas as pd
import requests
from urllib.parse import urlencode,quote_plus
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
import json
from twilio.rest import Client
import time
from config.settings import token,BASE_URL,VALEURS_LIMITE,DATA_DIR
import matplotlib.pyplot as plt

#=============================================================================================================
@st.cache_data(ttl=60) # expire au bout de 5 min
def fetch_current_data(location_id: str, token: str) -> pd.DataFrame:
    """Récupère les données actuelles de qualité de l'air et 
       les retourne sous fome de dictionnaire contenant les 
       differentes valeurs des polluants """
       
    endpoint = f"/locations/{location_id}/measures/current"
    params = {"token": token}
    full_url = f"{BASE_URL}{endpoint}?{urlencode(params)}"
    
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict):
            if "measures" in data:
                df = pd.DataFrame([data["measures"]])
            else:
                df = pd.DataFrame([data])
        elif isinstance(data, list):
                df =  pd.DataFrame(data)
        else:
            return {}
            
        
        pm25 = df.get('pm02_corrected', [0]).iloc[0] if 'pm02_corrected' in df.columns else 0
        co2 = df.get('rco2_corrected', [400]).iloc[0] if 'rco2_corrected' in df.columns else 400
        temp = df.get('atmp_corrected', [25]).iloc[0] if 'atmp_corrected' in df.columns else 25
        humidity = df.get('rhum_corrected', [50]).iloc[0] if 'rhum_corrected' in df.columns else 50
        pm10 = df.get('pm10_corrected', [0]).iloc[0] if 'pm10_corrected' in df.columns else 0
        pm1 = df.get('pm01_corrected', [0]).iloc[0] if 'pm01_corrected' in df.columns else 0
        pm03 = df.get('pm003Count', [0]).iloc[0] if 'pm003Count' in df.columns else 0
        tvoc = df.get('tvoc', [0]).iloc[0] if 'tvoc' in df.columns else 0
        nox = df.get('noxIndex', [0]).iloc[0] if 'noxIndex' in df.columns else 0

        return {
            "pm25": pm25,
            "co2": co2,
            "temp": temp,
            "humidity": humidity,
            "pm10": pm10,
            "pm1": pm1,
            "pm03": pm03,
            "tvoc": tvoc,
            "nox": nox,
            "last_update": datetime.now().strftime("%H:%M")
        }
    except Exception as e:
            st.error(f"Erreur lors de la récupération des données: {e}")

#=============================================================================================================
@st.cache_data(ttl=60) # expire au bout de 5 min
def calculer_iqa(df: pd.DataFrame):
    """
    Calcule l'IQA global de l'école à partir du df des données actuelles obtenues plus haut.
    :param df : Le DataFrame des données courantes de l'école
    :return: dict avec 'iqa_principal', 'polluant_principal', 'iqa_moyen'
    """

    # Calculer l'IQA pour chaque polluant
    iqa_values = {}
    for pollutant, limite in VALEURS_LIMITE.items():
        if pollutant in df.columns:
            concentration = df[pollutant].mean()  # moyenne du polluant
            iqa_values[pollutant] = (concentration / limite) * 100

    if not iqa_values:
        st.error("❌ Aucun polluant valide trouvé dans le fichier.")
        return None

    # Polluant le plus critique
    pollutant_principal = max(iqa_values, key=iqa_values.get)
    iqa_principal = iqa_values[pollutant_principal]

    return round(iqa_principal, 2)

#=============================================================================================================

def get_aqi_status(aqi):
    """Retourne un statut (string) selon l'AQI"""
    if aqi <= 50:
        return "Excellente"
    elif aqi <= 100:
        return "Bonne"
    elif aqi <= 150:
        return "Moyenne"
    elif aqi <= 200:
        return "Mauvaise"
    else:
        return "Très mauvaise"

#=============================================================================================================
@st.cache_data(ttl=60) # expire au bout de 5 min
def get_past_measures(location_id: int, token: str) -> pd.DataFrame:
    """
    Récupère les données des 7 derniers jours pour un `location_id` donné.
    """
    base_url = "https://api.airgradient.com/public/api/v1/locations"
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=7)

    url = f"{base_url}/{location_id}/measures/past"
    params = {
        "token": token,
        "from": from_date.strftime('%Y%m%dT%H%M%SZ'),
        "to": to_date.strftime('%Y%m%dT%H%M%SZ'),
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # conversion pour groupby
        
        file_path = os.path.join(DATA_DIR, f"data-7-jours-{location_id}.csv")
        df.to_csv(file_path, index=False)
        return df
    else:
        st.error(f"Erreur API : {response.status_code}")
        return pd.DataFrame()

#=============================================================================================================
@st.cache_data(ttl=60) # expire au bout de 5 min
def calculer_iqa_journalier(df: pd.DataFrame,location_id) -> pd.DataFrame:
    """
    Calcule l’IQA par jour pour un DataFrame donné.
    Retourne un DataFrame avec une colonne 'iqa_jour' par jour.
    """
    if df.empty:
        return pd.DataFrame()

    iqa_jours = []

    df['date'] = df['timestamp'].dt.date
    for jour, group in df.groupby('date'):
        valeurs = {}
        for pollutant, limite in VALEURS_LIMITE.items():
            if pollutant in group.columns:
                concentration = group[pollutant].mean()
                valeurs[pollutant] = (concentration / limite) * 100

        if valeurs:
            polluant_principal = max(valeurs, key=valeurs.get)
            iqa_principal = round(valeurs[polluant_principal], 2)
            iqa_jours.append({"date": jour, "iqa": iqa_principal})
    
    iqa_tab = pd.DataFrame(iqa_jours)
    file_path = os.path.join(DATA_DIR, f"iqa-7-jours-{location_id}.csv")
    iqa_tab.to_csv(file_path, index=False)
        
    return iqa_tab

#=============================================================================================================

def afficher_iqa_plot(iqa_df: pd.DataFrame, location_name: str):
    """
    Affiche un graphique Plotly de l'évolution de l'IQA sur 7 jours.
    """
    if iqa_df.empty:
        st.warning("Aucune donnée IQA à afficher.")
        return

    fig = px.line(iqa_df, x='date', y='iqa', title=f"📈 Évolution de l'IQA - {location_name}",
                  markers=True, labels={"iqa": "IQA", "date": "Date"})
    fig.update_traces(line=dict(color="green", width=3), marker=dict(size=8))
    fig.update_layout(yaxis=dict(title="Indice de Qualité de l'Air (IQA)"),
                      xaxis=dict(title="Date"), title_x=0.5)
    st.plotly_chart(fig)

#=============================================================================================================

#=============================================================================================================
def classify_by_iqa(location_ids, token, school_names):
    """
    Calcule l'IQA pour chaque location et affiche un graphique en barres horizontales élégant.
    """
    
    # Bouton d'actualisation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🔄 Actualiser les données", type="primary", use_container_width=True):
            st.rerun()    
    
    
    # Calcul des IQA
    iqas = {}
    for location_id, school_name in zip(location_ids, school_names):
        df = fetch_current_data(location_id, token)
        df = pd.DataFrame([df])
        iqa = calculer_iqa(df)
        iqas[school_name] = float(iqa)

    # Transformation en DataFrame
    df_iqa = pd.DataFrame(list(iqas.items()), columns=["École", "IQA"])
    
    # Fonction pour déterminer la couleur selon la qualité de l'air
    def get_air_quality_color(iqa_value):
        if iqa_value <= 50:
            return '#00E400'  # Vert - Bon
        elif iqa_value <= 100:
            return '#FFFF00'  # Jaune - Modéré
        elif iqa_value <= 150:
            return '#FF7E00'  # Orange - Mauvais pour groupes sensibles
        elif iqa_value <= 200:
            return '#FF0000'  # Rouge - Mauvais
        elif iqa_value <= 300:
            return '#8F3F97'  # Violet - Très mauvais
        else:
            return '#7E0023'  # Marron - Dangereux

    # Fonction pour déterminer le niveau de qualité
    def get_air_quality_level(iqa_value):
        if iqa_value <= 50:
            return 'Excellente'
        elif iqa_value <= 100:
            return 'Bonne'
        elif iqa_value <= 150:
            return 'Moyenne . Mauvaise pour groupes sensibles'
        elif iqa_value <= 200:
            return 'Mauvaise'
        elif iqa_value <= 300:
            return 'Très mauvaise'
        else:
            return 'Dangereuse'

    # Ajout des couleurs et niveaux
    df_iqa['Couleur'] = df_iqa['IQA'].apply(get_air_quality_color)
    df_iqa['Niveau'] = df_iqa['IQA'].apply(get_air_quality_level)
    
    # Tri pour une meilleure lisibilité
    df_sorted = df_iqa.sort_values(by="IQA", ascending=True)

    # Graphique en barres horizontales amélioré
    fig = px.bar(
        df_sorted,
        x="IQA",
        y="École",
        orientation="h",
        text="IQA",
        color="IQA",
        color_continuous_scale=[
            [0.0, '#00E400'],    # Bon (0-50)
            [0.167, '#FFFF00'],  # Modéré (51-100)
            [0.333, '#FF7E00'],  # Mauvais pour groupes sensibles (101-150)
            [0.5, '#FF0000'],    # Mauvais (151-200)
            [0.667, '#8F3F97'],  # Très mauvais (201-300)
            [1.0, '#7E0023']     # Dangereux (301+)
        ],
        title="Indice de Qualité de l'Air (IQA) par École",
        hover_data={'Niveau': True}
    )

    # Mise à jour des traces pour un meilleur affichage
    fig.update_traces(
        texttemplate="<b>%{text:.0f}</b>", 
        textposition="outside",
        textfont=dict(size=12, color="black"),
        marker_line_color='rgba(0,0,0,0.3)',
        marker_line_width=1
    )
    
    # Configuration du layout pour un rendu plus professionnel
    fig.update_layout(
        xaxis_title="<b>Indice de Qualité de l'Air (IQA)</b>",
        yaxis_title="<b>Écoles</b>",
        plot_bgcolor="white",
        paper_bgcolor="#f8f9fa",
        title_font=dict(size=24, color="#2c3e50"),
        title_x=0.5,  # Centrer le titre
        
        # Configuration des axes
        xaxis=dict(
            showgrid=True, 
            gridcolor="rgba(200,200,200,0.3)",
            gridwidth=1,
            tickfont=dict(size=11),
            title_font=dict(size=14)
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11),
            title_font=dict(size=14)
        ),
        
        # Marges et dimensions
        margin=dict(l=20, r=80, t=80, b=60),
        height=max(400, len(df_iqa) * 60),  # Hauteur dynamique selon le nombre d'écoles
        
        # Barre de couleur personnalisée
        coloraxis_colorbar=dict(
            title="<b>Niveau IQA</b>",
            title_font=dict(size=12),
            tickvals=[25, 75, 125, 175, 250, 350],
            ticktext=["Bon", "Modéré", "Mauvais*", "Mauvais", "Très mauvais", "Dangereux"],
            tickfont=dict(size=10),
            len=0.7
        )
    )
    
    # Ajout d'annotations pour les seuils critiques
    max_iqa = df_iqa['IQA'].max()
    if max_iqa > 150:
        fig.add_vline(x=150, line_dash="dash", line_color="orange", 
                     annotation_text="Seuil critique", annotation_position="top")
    
    # Affichage avec Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander(" Voir le récapitulatif détaillé", expanded=False):
        st.subheader("Récapitulatif détaillé")
        
        # Formatage du tableau pour un meilleur rendu
        df_display = df_iqa.copy()
        df_display = df_display.sort_values('IQA', ascending=False)
        df_display['IQA'] = df_display['IQA'].round(1)
        df_display = df_display[['École', 'IQA', 'Niveau']]
        
        # Affichage du tableau
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "École": st.column_config.TextColumn("École", width="medium"),
                "IQA": st.column_config.NumberColumn("IQA", format="%.1f"),
                "Niveau": st.column_config.TextColumn("Niveau de qualité", width="large")
            }
        )

#=============================================================================================================

#=============================================================================================================
@st.cache_data(ttl=60) # expire au bout de 5 min
def calculate_air_quality_status(df):
    """Calcule le statut global de la qualité de l'air pour les parents"""
    df = pd.DataFrame([df])
    
    if df.empty:
        return None
    
    
    iqa = calculer_iqa(df)
        
    # Classification finale
    if iqa <= 50:
        status = "Excellente"
        color = "#4caf50"
        icon = "😊"
        message = "L'air est pur ! Votre enfant respire dans de bonnes conditions."
        advice = "Parfait pour toutes les activités à l'école."
    elif iqa <= 100:
        status = "Bonne"
        color = "#8bc34a"
        icon = "🙂"
        message = "La qualité de l'air est satisfaisante."
        advice = "Conditions normales, rien à signaler."
    elif iqa <= 150:
        status = "Moyenne"
        color = "#ff9800"
        icon = "😐"
        message = "L'air pourrait être mieux. Surveillez les symptômes chez votre enfant."
        advice = "Encouragez votre enfant à bien s'hydrater."
    elif iqa <= 200:
        status = "Mauvaise"
        color = "#f44336"
        icon = "😷"
        message = "Air pollué. Soyez vigilant aux signes de gêne respiratoire."
        advice = "Contactez l'école si votre enfant tousse ou a du mal à respirer."
    else:
        status = "Très mauvaise"
        color = "#d32f2f"
        icon = "😨"
        message = "Air très pollué ! Surveillez attentivement votre enfant."
        advice = "Consultez un médecin si votre enfant présente des symptômes."
        
        
        
    pm25 = df["pm25"].iloc[0] if 'pm25' in df.columns else 0
    co2 = df["co2"].iloc[0] if 'co2' in df.columns else 400
    temp = df["temp"].iloc[0] if 'temp' in df.columns else 25
    humidity = df["humidity"].iloc[0] if 'humidity' in df.columns else 50
    
    return {
        "status": status,
        "color": color,
        "icon": icon,
        "message": message,
        "advice": advice,
        "pm25": pm25,
        "co2": co2,
        "temp": temp,
        "humidity": humidity,
        "last_update": datetime.now().strftime("%H:%M")
    }



