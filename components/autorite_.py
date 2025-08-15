import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from plotly.subplots import make_subplots
import os
import requests
from urllib.parse import urlencode,quote_plus
import json
from twilio.rest import Client
import time
from config.settings import token,BASE_URL,VALEURS_LIMITE
import streamlit.components.v1 as components
from src.functions import fetch_current_data,calculer_iqa
import streamlit.components.v1 as components
from config.settings import token,BASE_URL,VALEURS_LIMITE,location_ids,DATA_DIR,liens
import smtplib
from email.message import EmailMessage



# Configuration (à adapter selon vos données)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data/air_quality')

# ========================================
# CONFIGURATION GMAIL API
# ========================================
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(45deg, #81c784, #aed581, #c5e1a5, #dcedc8);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .status-excellent { border-left-color: #22c55e !important; }
    .status-good { border-left-color: #84cc16 !important; }
    .status-moderate { border-left-color: #eab308 !important; }
    .status-poor { border-left-color: #f97316 !important; }
    .status-dangerous { border-left-color: #ef4444 !important; }
    
    .prediction-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #cbd5e1;
    }
    
    .action-button {
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .alert-banner {
        background: linear-gradient(90deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
    }
    
    .stMetric > div > div > div > div {
        font-size: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)


#=============================================================================================================

def show_header():
    """
    Affiche un en-tête moderne et attractif pour la page École.
    :param nom_ecole: Nom de l'école à afficher (optionnel)
    :param logo_path: Chemin vers le logo de l'école (optionnel)
    """
    
    # CSS personnalisé pour l'animation et le style
    st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 50%, #a5d6a7 100%);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 10px;
        box-shadow: 0 8px 32px rgba(46, 125, 50, 0.1);
        border: 2px solid rgba(46, 125, 50, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .title-main {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1b5e20;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 0px;
        animation: fadeInUp 1s ease-out;
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #2e7d32;
        margin-bottom: 0px;
        font-weight: 500;
        animation: fadeInUp 1.2s ease-out;
    }
    
    
    .air-emoji {
        font-size: 2rem;
        animation: float 3s ease-in-out infinite;
        margin: 0 10px;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    .decorative-line {
        height: 4px;
        background: linear-gradient(90deg, #4caf50, #81c784, #a5d6a7, #4caf50);
        border-radius: 2px;
        margin: 10px 0;
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200px 0;
        }
        100% {
            background-position: 200px 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Conteneur principal avec design moderne
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Titre principal avec emojis animés
            st.markdown(
                """
                <div class="title-main">
                    Bienvenue sur l'espace Autorité de Respire
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Sous-titre engageant
            st.markdown(
                '<div class="subtitle">Découvrez comment va l\'air de l\'école dans les ecoles de votre ville aujourd\'hui et prenez des décisions. </div>',
                unsafe_allow_html=True
            )
            
        st.markdown('</div>', unsafe_allow_html=True)


def show_line():
    # Ligne décorative animée
    st.markdown('<div class="decorative-line"></div>', unsafe_allow_html=True)
#=============================================================================================================

@st.cache_data(ttl=300) # expire au bout de 5 min
def alerts(iqa):    
    if iqa > 100:
        st.markdown("""
        <div class="alert-banner">
            <strong>⚠️ ALERTE QUALITÉ DE L'AIR</strong><br>
            Niveau préoccupant détecté. Actions recommandées : ventilation renforcée, réduction des activités extérieures.
        </div>
        """, unsafe_allow_html=True)
#=============================================================================================================

def descript(iqa):
    """
    Décrit la signification de l'iqa et interprète la valeur donnée
    """

    description_generale = """
    <strong>L'iqa</strong> (Air Quality Index) est un indicateur normalisé qui mesure la qualité de l'air sur une échelle de 0 à 500.
    Il combine plusieurs polluants atmosphériques comme les particules fines (PM2.5, PM10), l’ozone, le dioxyde d’azote, etc.
    """

    # Interprétation dynamique + couleur
    if iqa <= 50:
        couleur_border = "#4caf50"
        niveau = "Excellente qualité d’air "
        interpretation = f"""
         Avec un iqa de <strong>{iqa}</strong>, l'air est de qualité excellente.<br>
        Aucun risque pour la santé : toutes les activités peuvent être menées normalement.<br>
        Environnement idéal pour les élèves, enseignants et personnel.
        """
    elif iqa <= 100:
        couleur_border = "#ffeb3b"
        niveau = "Bonne qualité d’air "
        interpretation = f"""
         Votre iqa de <strong>{iqa}</strong> indique une qualité d'air acceptable.<br>
        La majorité des personnes ne ressentiront aucun effet, mais les individus très sensibles peuvent éprouver un léger inconfort.
        """
    elif iqa <= 150:
        couleur_border = "#ff9800"
        niveau = "Qualité d’air moyenne "
        interpretation = f"""
         Un iqa de <strong>{iqa}</strong> indique une pollution modérée.<br>
        Les enfants, les personnes âgées et les asthmatiques peuvent ressentir des effets légers.<br>
        Il est conseillé de limiter les activités physiques intenses à l'extérieur.
        """
    elif iqa <= 200:
        couleur_border = "#f44336"
        niveau = "Qualité d’air mauvaise "
        interpretation = f"""
         L’iqa de <strong>{iqa}</strong> révèle un air pollué.<br>
        Tous les individus peuvent ressentir des effets, les personnes vulnérables étant les plus exposées.<br>
        Éviter les activités extérieures prolongées.
        """
    else:
        couleur_border = "#b71c1c"
        niveau = "Qualité d’air très mauvaise "
        interpretation = f"""
         L’iqa de <strong>{iqa}</strong> est critique.<br>
        Risques élevés pour la santé de tous. Des mesures immédiates sont nécessaires :<br>
         Restez à l’intérieur, fermez les fenêtres et portez un masque si besoin.
        """

    # HTML amélioré
    components.html(f"""
    <div style='
        background: #f8f9ff;
        border: 3px solid {couleur_border};
        border-radius: 15px;
        padding: 25px;
        font-family: "Segoe UI", sans-serif;
        height: auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        overflow-y: auto;
    '>
        <h2 style='color: {couleur_border}; margin-top: 0; text-align: center;'>{niveau}</h2>
        
        <div style='margin-top: 20px; color: #333; line-height: 1.6; font-size: 15px;'>
            <h4 style='color: #444;'> Qu’est-ce que l’iqa ?</h4>
            <p>{description_generale}</p>

            <h4 style='color: #444;'> Interprétation</h4>
            <p>{interpretation}</p>
        </div>
    </div>
    """, height=400)

    
#=============================================================================================================

@st.cache_data(ttl=300) # expire au bout de 5 min
def get_iqa_status(iqa):
    """Retourne le statut et la couleur selon l'iqa"""

    if iqa <= 50:
        return "Excellente", "#4caf50", "😊"
    elif iqa <= 100:
        return "Bonne", "#8bc34a", "🙂"
    elif iqa <= 150:
        return "Moyenne", "#ff9800", "😐"
    elif iqa <= 200:
        return "Mauvaise", "#f44336", "😟"
    else:
        return "Très mauvaise", "#d32f2f", "😷"
#=============================================================================================================

@st.cache_data(ttl=300) # expire au bout de 5 min
def create_gauge_chart(iqa, variation_24h=0, max_val=200):
    """Crée un graphique en forme de jauge IQA avec légendes claires"""

    status, color, emoji = get_iqa_status(iqa)

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=iqa,
        number={'valueformat': '.1f', 'font': {'size': 36}},
        delta={'reference': iqa - variation_24h, 'relative': False, 'valueformat': '.1f',
               'increasing': {'color': "red"}, 'decreasing': {'color': "green"},
               'position': "bottom", 'suffix': " (variation 24h)"},
        gauge={
            'axis': {'range': [0, max_val]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "rgba(34, 197, 94, 0.3)", 'name': 'Bon'},
                {'range': [50, 100], 'color': "rgba(234, 179, 8, 0.3)", 'name': 'Modéré'},
                {'range': [100, 150], 'color': "rgba(249, 115, 22, 0.3)", 'name': 'Mauvais'},
                {'range': [150, 200], 'color': "rgba(239, 68, 68, 0.3)", 'name': 'Très mauvais'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.8,
                'value': iqa
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=30, b=20),
    )

    return fig

#=============================================================================================================

@st.cache_data(ttl=300) # expire au bout de 5 min
def calculate_air_quality_status(df,iqa):
    """Calcule le statut global de la qualité de l'air pour les autorités avec tous les indicateurs"""
    
    if df.empty:
        return None


    # Classification finale (version autorités)
    if iqa <= 50:
        status = "Excellente"
        color = "#4caf50"
        icon = "✅"
        message = "Qualité de l'air optimale. Aucun impact attendu sur la santé ou les activités scolaires."
        advice = "Aucune mesure particulière requise."

    elif iqa <= 100:
        status = "Bonne"
        color = "#8bc34a"
        icon = "✔️"
        message = "Qualité de l'air satisfaisante. Situation stable pour l’ensemble des élèves et personnels."
        advice = "Surveillance environnementale régulière recommandée."

    elif iqa <= 150:
        status = "Moyenne"
        color = "#ff9800"
        icon = "⚠️"
        message = "Légère dégradation de la qualité de l'air. Possibles inconforts chez les groupes sensibles."
        advice = "Envisager des mesures d’atténuation pour les personnes vulnérables (asthmatiques, jeunes enfants)."

    elif iqa <= 200:
        status = "Mauvaise"
        color = "#f44336"
        icon = "❗"
        message = "Qualité de l'air préoccupante. Risques sanitaires modérés à élevés pour les populations sensibles."
        advice = "Limiter les activités physiques extérieures. Informer les établissements scolaires."

    else:
        status = "Très mauvaise"
        color = "#d32f2f"
        icon = "🚨"
        message = "Pollution de l'air à un niveau critique. Risques sanitaires sérieux pour tous les groupes."
        advice = "Déclencher les protocoles d'urgence : fermeture temporaire des locaux, communication aux familles, alerte aux autorités sanitaires."

    
    
    pm25 = df["pm25"].iloc[0] if 'pm25' in df.columns else 0
    co2 = df["co2"].iloc[0] if 'co2' in df.columns else 400
    temp = df["temp"].iloc[0] if 'temp' in df.columns else 25
    humidity = df["humidity"].iloc[0] if 'humidity' in df.columns else 50
    pm10 = df["pm10"].iloc[0] if 'pm10' in df.columns else 0
    pm1 = df["pm1"].iloc[0] if 'pm1' in df.columns else 0
    pm03 = df["pm03"].iloc[0] if 'pm03' in df.columns else 0
    tvoc = df["tvoc"].iloc[0] if 'tvoc' in df.columns else 0
    nox = df["nox"].iloc[0] if 'nox' in df.columns else 0
    
    

    # Résultat complet
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
        "pm10": pm10,
        "pm1": pm1,
        "pm03": pm03,
        "tvoc": tvoc,
        "nox": nox,
        "last_update": datetime.now().strftime("%H:%M")
    }
#=============================================================================================================

def show_air_status_summary(df,iqa):
    """
    BLOC I: Affiche tous les pollunts mesures en temps reel
    """
    
    st.markdown("## Polluants collectés en temps réel ")
    
    # Récupération des données
    air_status = calculate_air_quality_status(df,iqa)
    
    if not air_status:
        st.error("❌ Impossible de récupérer les données de qualité de l'air")
        return
    
   # Section KPIs Principaux  (Tier 1)
   
    col1, col2, col3, col4 = st.columns(4)
    
    
    metrics = [
        {
            "col": col1,
            "name": "PM2.5", 
            "value": air_status["pm25"], 
            "unit": "μg/m³",
            "icon": "🌫️",
            "description": "Particules fines",
            "impact": "Respiratoire"
        },
        {
            "col": col2,
            "name": "CO₂", 
            "value": air_status["co2"], 
            "unit": "ppm",
            "icon": "💨",
            "description": "Dioxyde de carbone",
            "impact": "Concentration"
        },
        {
            "col": col3,
            "name": "PM10", 
            "value": air_status["pm10"], 
            "unit": "μg/m³",
            "icon": "🌁",
            "description": "Particules grossières",
            "impact": "Voies respiratoires"
        },
        {
            "col": col4,
            "name": "TVOC", 
            "value": air_status["tvoc"], 
            "unit": "μg/m³",
            "icon": "🧪",
            "description": "Composés organiques",
            "impact": "Qualité air intérieur"
        }
    ]
         
    for metric in metrics:
        value = metric["value"]
        color =  "#1e3a8a"
        
        formatted_value = f"{value:.1f}" if value < 100 else f"{int(value)}"

        with metric["col"]:
            components.html(f"""
            <div style="
                background: linear-gradient(145deg, white, #f8f9fa);
                border: 1px solid {color}30;
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 8px 25px {color}15;
                transition: all 0.3s ease;
                cursor: pointer;
                height: 170px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                font-family: 'SF Pro Display', -apple-system, system-ui, sans-serif;
            " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 35px {color}25'"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 25px {color}15'">
                
                <div style="
                    width: 50px;
                    height: 50px;
                    background: {color}15;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 15px auto;
                    font-size: 1.5rem;
                ">{metric["icon"]}</div>
                
                <div>
                    <div style="font-size: 0.85rem; color: {color}; font-weight: 600; margin-bottom: 5px;">
                        {metric["name"]}
                    </div>
                    <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 5px;">
                        {formatted_value}
                    </div>
                    <div style="font-size: 0.75rem; color: #666; margin-bottom: 10px;">
                        {metric["unit"]}
                    </div>
                </div>
                
                <div style="
                    background: {color}08;
                    border-radius: 8px;
                    padding: 5px 8px;
                    border-left: 3px solid {color};
                ">
                    <div style="font-size: 0.7rem; color: #333; font-weight: 500;">
                        {metric["description"]}
                    </div>
                </div>
            </div>
            """, height=220)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # Section KPIs Secondaires (Tier 2)
    
    col5, col6, col7, col8, col9 = st.columns(5)
    
    secondary_metrics = [
        {
            "col": col5,
            "name": "Température", 
            "value": air_status["temp"], 
            "unit": "°C",
            "category": "Confort thermique"
        },
        {
            "col": col6,
            "name": "Humidité", 
            "value": air_status["humidity"], 
            "unit": "%",
            "category": "Confort hygrométrique"
        },
        {
            "col": col7,
            "name": "PM1", 
            "value": air_status["pm1"], 
            "unit": "μg/m³",
            "icon": "⚫",
            "category": "Particules ultrafines"
        },
        {
            "col": col8,
            "name": "NOx", 
            "value": air_status["nox"], 
            "unit": "μg/m³",
            "category": "Polluants véhiculaires"
        },
        {
            "col": col9,
            "name": "PM0.3", 
            "value": air_status["pm03"], 
            "unit": "cnt/L",
            "category": "Particules nanoscopiques"
        }
    ]
    
    for metric in secondary_metrics:
        value = metric["value"]
        
        formatted_value = f"{value:.1f}" if value < 100 else f"{int(value)}"
        
        color = "#1e3a8a"
        
        with metric["col"]:
            components.html(f"""
            <div style="
                background: white;
                border: 1px solid #e0e0e0;
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                font-family: 'SF Pro Display', -apple-system, system-ui, sans-serif;
                height: 170px;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.12)'"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.08)'">
                
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div style="
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background: {color};
                    "></div>
                </div>
                
                <div style="margin-bottom: 8px;">
                    <div style="font-size: 0.8rem; color: #666; font-weight: 500;">
                        {metric["name"]}
                    </div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: {color};">
                        {formatted_value}
                        <span style="font-size: 0.9rem; font-weight: 400; color: #888;">
                            {metric["unit"]}
                        </span>
                    </div>
                </div>
                
                <div style="
                    font-size: 0.7rem;
                    color: #777;
                    background: #f5f5f5;
                    padding: 5px 8px;
                    border-radius: 6px;
                ">
                    {metric["category"]}
                </div>
            </div>
            """, height=220)
    
#=============================================================================================================


def generate_report(location_id):
    """
    Génère le rapport PDF complet pour une école.
    Utilise les données actuelles, prédictions J+1 et J+7.
    Retourne le chemin du fichier PDF généré.
    """
    # ... Génération du PDF avec les polluants, prédictions, IQA ...
    # Utilise fpdf, reportlab ou autre lib PDF
    pdf_path = f"rapport_{location_id}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"Contenu fictif du rapport PDF...")
    # ... code de génération du PDF ...
    return pdf_path


#=============================================================================================================