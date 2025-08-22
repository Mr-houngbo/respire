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
    Affiche un en-tête simple et élégant pour la page Autorité.
    """
    
    st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        position: sticky;
        top: 0;
        z-index: 100;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-content {
        flex: 1;
    }
    
    .title-main {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: 1rem;
        color: #6c757d;
        margin: 0;
        font-weight: 400;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('''
        <div class="header-container">
            <div class="header-content">
                <div class="title-main">
                    Bienvenue sur l'espace Autorité de Respire
                </div>
                <div class="subtitle">
                    Découvrez comment va l'air de l'école dans les écoles de votre ville aujourd'hui et prenez des décisions.
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)



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
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import base64
import tempfile
import io
import os
from datetime import datetime, timedelta
from weasyprint import HTML, CSS
from jinja2 import Template
import requests
from urllib.parse import urlencode
from typing import Dict, List, Tuple, Optional

# Configuration existante (gardée de votre code)
BASE_URL = "https://api.airgradient.com/public/api/v1"
location_id = "164928"
location_id_input = location_id
token_input = token
format_output = "PDF"


VALEURS_LIMITE = {
    "pm03_count": 100000,
    "pm01_corrected": 15,
    "pm02_corrected": 75,
    "pm10_corrected": 150,
    "rco2_corrected": 1000,
    "atmp_corrected": 27,
    "rhum_corrected": 60,
    "tvoc": 500,
    "noxIndex": 100
}

POLLUANTS_NOMS = {
    "pm02_corrected": "PM2.5",
    "pm10_corrected": "PM10",
    "pm01_corrected": "PM1",
    "rco2_corrected": "CO2",
    "tvoc": "COV Totaux",
    "noxIndex": "NOx",
    "atmp_corrected": "Température",
    "rhum_corrected": "Humidité"
}

COLORS = {
    'bon': '#27AE60',
    'modere': '#F39C12',
    'mauvais': '#E74C3C',
    'critique': '#8E44AD',
    'primary': '#2C3E50',
    'secondary': '#34495E',
    'accent': '#3498DB'
}

# Vos fonctions existantes (gardées telles quelles)
def get_measures_range(location_id: int, token: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    """Récupère les données pour un location_id donné entre from_date et to_date"""
    base_url = "https://api.airgradient.com/public/api/v1/locations"
    url = f"{base_url}/{location_id}/measures/past"

    params = {
        "token": token,
        "from": from_date.strftime('%Y%m%dT%H%M%SZ'),
        "to": to_date.strftime('%Y%m%dT%H%M%SZ'),
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return pd.DataFrame()

def get_full_history(location_id: int, token: str, days: int = 7) -> pd.DataFrame:
    """Récupère toutes les données d'une location_id sur 'days' jours"""
    all_data = []
    to_date = datetime.utcnow()

    while days > 0:
        chunk_days = min(days, 10)
        from_date = to_date - timedelta(days=chunk_days)
        df_chunk = get_measures_range(location_id, token, from_date, to_date)
        
        if df_chunk.empty:
            break
        all_data.append(df_chunk)
        days -= chunk_days
        to_date = from_date

    if all_data:
        return pd.concat(all_data, ignore_index=True).drop_duplicates()
    return pd.DataFrame()

class HTMLReportGenerator:
    def __init__(self, location_id: str, token: str):
        self.location_id = location_id
        self.token = token
        self.report_date = datetime.now()
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def fetch_current_data(self) -> Dict:
        """Récupère les données actuelles de qualité de l'air"""
        endpoint = f"/locations/{self.location_id}/measures/current"
        params = {"token": self.token}
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
                df = pd.DataFrame(data)
            else:
                return self._get_default_data()
            
            result = {}
            for key in VALEURS_LIMITE.keys():
                result[key] = df[key].iloc[0] if key in df.columns and not df[key].empty else 0
            
            result["last_update"] = datetime.now().strftime("%H:%M")
            return result
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {e}")
            return self._get_default_data()
    
    def _get_default_data(self) -> Dict:
        """Données par défaut en cas d'erreur"""
        return {
            "pm02_corrected": 25.5,
            "pm10_corrected": 30.2,
            "pm01_corrected": 20.1,
            "rco2_corrected": 850,
            "tvoc": 120,
            "noxIndex": 45,
            "atmp_corrected": 22.5,
            "rhum_corrected": 55,
            "last_update": datetime.now().strftime("%H:%M")
        }

    def calculer_iqa_global(self, data: Dict) -> Tuple[float, str, str, str]:
        """Calcule l'IQA global avec couleur associée"""
        iqa_values = {}
        
        for pollutant, limite in VALEURS_LIMITE.items():
            if pollutant in data and data[pollutant] is not None:
                if pollutant not in ["rhum_corrected", "atmp_corrected"]:
                    concentration = data[pollutant]
                    if concentration > 0:
                        iqa_values[pollutant] = (concentration / limite) * 100
        
        if not iqa_values:
            return 0, "Aucun", "Données indisponibles", COLORS['secondary']
        
        polluant_principal = max(iqa_values, key=iqa_values.get)
        iqa_principal = iqa_values[polluant_principal]
        
        if iqa_principal <= 50:
            status = "EXCELLENT"
            color = COLORS['bon']
        elif iqa_principal <= 75:
            status = "BON"
            color = COLORS['bon']
        elif iqa_principal <= 100:
            status = "MODERE"
            color = COLORS['modere']
        elif iqa_principal <= 150:
            status = "MAUVAIS"
            color = COLORS['mauvais']
        else:
            status = "CRITIQUE"
            color = COLORS['critique']
        
        return round(iqa_principal, 1), POLLUANTS_NOMS.get(polluant_principal, polluant_principal), status, color

    def create_gauge_chart(self, iqa_value: float, color: str) -> str:
        """Crée une jauge IQA et retourne le base64"""
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
        
        theta = np.linspace(0, np.pi, 100)
        zones = [(0, 50, COLORS['bon']), (50, 100, COLORS['modere']), 
                (100, 150, COLORS['mauvais']), (150, 200, COLORS['critique'])]
        
        for start, end, zone_color in zones:
            mask = (theta >= start/200 * np.pi) & (theta <= end/200 * np.pi)
            ax.fill_between(theta[mask], 0.8, 1.0, color=zone_color, alpha=0.7)
        
        angle = min(iqa_value, 200) / 200 * np.pi
        ax.arrow(angle, 0, 0, 0.7, head_width=0.05, head_length=0.05, 
                fc=color, ec=color, linewidth=3)
        
        ax.scatter(0, 0, c=color, s=200, zorder=5)
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('S')
        ax.set_theta_direction(1)
        ax.set_thetagrids(np.linspace(0, 180, 7), ['200', '167', '133', '100', '67', '33', '0'])
        ax.set_rticks([])
        ax.grid(True, alpha=0.3)
        
        ax.text(np.pi/2, -0.3, f'IQA: {iqa_value:.1f}', fontsize=20, fontweight='bold', 
               ha='center', va='center', transform=ax.transData)
        
        return self._fig_to_base64(fig)

    def create_dashboard_chart(self, data: Dict) -> str:
        """Crée le dashboard des polluants et retourne le base64"""
        fig, axes = plt.subplots(2, 4, figsize=(16, 10))
        fig.suptitle('TABLEAU DE BORD - QUALITÉ DE L\'AIR EN TEMPS RÉEL', 
                    fontsize=18, fontweight='bold', y=0.95)
        
        polluants = ['pm02_corrected', 'pm10_corrected', 'pm01_corrected', 'rco2_corrected',
                    'tvoc', 'noxIndex', 'atmp_corrected', 'rhum_corrected']
        
        for i, polluant in enumerate(polluants):
            row = i // 4
            col = i % 4
            ax = axes[row, col]
            
            if polluant in data and data[polluant] is not None:
                valeur = data[polluant]
                seuil = VALEURS_LIMITE.get(polluant, 100)
                nom = POLLUANTS_NOMS.get(polluant, polluant)
                
                ratio = min(valeur / seuil, 2.0)
                
                if ratio <= 0.5:
                    color = COLORS['bon']
                elif ratio <= 1.0:
                    color = COLORS['modere']
                else:
                    color = COLORS['mauvais']
                
                ax.barh([0], [ratio], color=color, alpha=0.8, height=0.5)
                ax.axvline(x=1, color='red', linestyle='--', alpha=0.7, linewidth=2)
                
                ax.text(0.5, 0.7, nom, fontsize=12, fontweight='bold', ha='center')
                ax.text(0.5, 0.3, f'{valeur:.1f}', fontsize=14, fontweight='bold', ha='center')
                ax.text(0.5, -0.1, f'Seuil: {seuil}', fontsize=8, ha='center', alpha=0.7)
                
                ax.set_xlim(0, 2)
                ax.set_ylim(-0.3, 1)
                ax.set_xticks([])
                ax.set_yticks([])
                
                for spine in ax.spines.values():
                    spine.set_color(color)
                    spine.set_linewidth(2)
            else:
                ax.text(0.5, 0.5, 'Données\nindisponibles', ha='center', va='center')
                ax.set_xticks([])
                ax.set_yticks([])
        
        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_evolution_chart(self) -> str:
        """Crée le graphique d'évolution temporelle"""
        df = get_full_history(int(self.location_id), self.token, days=7)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if df.empty:
            ax.text(0.5, 0.5, 'Données historiques\nindisponibles', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=16)
        else:
            # Calcul IQA simplifié pour chaque jour
            df['date'] = df['timestamp'].dt.date
            iqa_daily = []
            
            for jour, group in df.groupby('date'):
                iqa_jour = 0
                for pollutant, limite in VALEURS_LIMITE.items():
                    if pollutant in group.columns and pollutant not in ["rhum_corrected", "atmp_corrected"]:
                        concentration = group[pollutant].mean()
                        if pd.notna(concentration) and concentration > 0:
                            iqa_poll = (concentration / limite) * 100
                            iqa_jour = max(iqa_jour, iqa_poll)
                
                iqa_daily.append({"date": jour, "iqa": iqa_jour})
            
            if iqa_daily:
                df_iqa = pd.DataFrame(iqa_daily)
                ax.plot(df_iqa['date'], df_iqa['iqa'], marker='o', linewidth=2, color=COLORS['primary'])
                ax.fill_between(df_iqa['date'], df_iqa['iqa'], alpha=0.3, color=COLORS['accent'])
                ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
                plt.xticks(rotation=45)
            else:
                ax.text(0.5, 0.5, 'Calcul IQA impossible', ha='center', va='center', transform=ax.transAxes)
        
        ax.set_title("ÉVOLUTION IQA - 7 DERNIERS JOURS", fontsize=16, fontweight='bold')
        ax.set_ylabel("Indice de Qualité de l'Air (IQA)")
        ax.grid(True, alpha=0.3, linestyle='--')
        
        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig) -> str:
        """Convertit une figure matplotlib en base64 sans créer de fichier temporaire"""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return img_base64


    def generate_html_report(self) -> str:
        """Génère le rapport HTML complet"""
        # Récupération des données
        current_data = self.fetch_current_data()
        iqa_value, polluant_principal, status, status_color = self.calculer_iqa_global(current_data)
        
        # Génération des graphiques
        gauge_b64 = self.create_gauge_chart(iqa_value, status_color)
        dashboard_b64 = self.create_dashboard_chart(current_data)
        evolution_b64 = self.create_evolution_chart()
        
        # Détermination des couleurs de statut
        status_colors = {
            'EXCELLENT': '#27AE60',
            'BON': '#27AE60',
            'MODERE': '#F39C12',
            'MAUVAIS': '#E74C3C',
            'CRITIQUE': '#8E44AD'
        }
        status_bg_color = status_colors.get(status, '#34495E')
        
        # Génération des recommandations
        if iqa_value <= 75:
            recommandations_title = "SITUATION FAVORABLE"
            recommandations_color = "#27AE60"
            recommandations = [
                "Maintenir la surveillance régulière",
                "Activités extérieures normales",
                "Sensibilisation continue des élèves",
                "Continuer les mesures préventives"
            ]
        elif iqa_value <= 100:
            recommandations_title = "SURVEILLANCE RENFORCÉE"
            recommandations_color = "#F39C12"
            recommandations = [
                "Surveiller l'évolution quotidienne",
                "Limiter les activités sportives intenses",
                "Améliorer la ventilation des classes",
                "Informer les parents sensibles"
            ]
        else:
            recommandations_title = "MESURES D'URGENCE"
            recommandations_color = "#E74C3C"
            recommandations = [
                "SUSPENDRE les activités extérieures",
                "ALERTER immédiatement les familles",
                "ACTIVER le plan d'urgence pollution",
                "CONSULTER les autorités sanitaires"
            ]
        
        # Génération du tableau des données
        unites = {
            "pm02_corrected": "µg/m³",
            "pm10_corrected": "µg/m³",
            "pm01_corrected": "µg/m³",
            "rco2_corrected": "ppm",
            "tvoc": "µg/m³",
            "noxIndex": "µg/m³",
            "atmp_corrected": "°C",
            "rhum_corrected": "%"
        }
        
        donnees_tableau = []
        for pollutant, limite in VALEURS_LIMITE.items():
            if pollutant in current_data:
                val = current_data[pollutant]
                nom = POLLUANTS_NOMS.get(pollutant, pollutant)
                unite = unites.get(pollutant, "")
                
                if pollutant not in ["rhum_corrected", "atmp_corrected"]:
                    ratio = (val / limite) * 100
                    if ratio <= 50:
                        evaluation = "EXCELLENT"
                        eval_color = "#27AE60"
                    elif ratio <= 75:
                        evaluation = "BON"
                        eval_color = "#27AE60"
                    elif ratio <= 100:
                        evaluation = "MODÉRÉ"
                        eval_color = "#F39C12"
                    elif ratio <= 150:
                        evaluation = "MAUVAIS"
                        eval_color = "#E74C3C"
                    else:
                        evaluation = "CRITIQUE"
                        eval_color = "#8E44AD"
                else:
                    if pollutant == "atmp_corrected":
                        evaluation = "BON" if val <= limite else "ÉLEVÉ"
                        eval_color = "#27AE60" if val <= limite else "#F39C12"
                    else:
                        evaluation = "BON" if 40 <= val <= 60 else "INADÉQUAT"
                        eval_color = "#27AE60" if 40 <= val <= 60 else "#F39C12"
                
                donnees_tableau.append({
                    'nom': nom,
                    'valeur': f"{val:.1f}",
                    'unite': unite,
                    'seuil': f"{limite}",
                    'evaluation': evaluation,
                    'eval_color': eval_color
                })
        
        # Template HTML avec CSS intégré
        html_template = Template("""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Qualité de l'Air - Programme RESPIRE</title>
    <style>
        @page {
            size: A4;
            margin: 1.5cm;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            margin-bottom: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .info-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
        }
        
        .info-card h3 {
            color: #2c3e50;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }
        
        .info-card p {
            font-size: 1.1rem;
            font-weight: bold;
            color: #34495e;
        }
        
        .section {
            background: white;
            margin-bottom: 2rem;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        }
        
        .section-header {
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            padding: 1rem 2rem;
            font-size: 1.3rem;
            font-weight: bold;
        }
        
        .section-content {
            padding: 2rem;
        }
        
        .iqa-summary {
            display: flex;
            align-items: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .iqa-badge {
            background: {{ status_bg_color }};
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            min-width: 200px;
        }
        
        .iqa-details {
            flex: 1;
        }
        
        .iqa-details h3 {
            font-size: 1.2rem;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .iqa-details p {
            color: #7f8c8d;
            margin-bottom: 0.3rem;
        }
        
        .chart-container {
            text-align: center;
            margin: 2rem 0;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        .data-table th {
            background: #ecf0f1;
            color: #2c3e50;
            padding: 1rem;
            text-align: center;
            font-weight: bold;
            border: 1px solid #bdc3c7;
        }
        
        .data-table td {
            padding: 0.8rem;
            text-align: center;
            border: 1px solid #ecf0f1;
        }
        
        .data-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .evaluation-cell {
            font-weight: bold;
            color: white;
            border-radius: 5px;
            padding: 0.5rem;
        }
        
        .recommendations {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-top: 2rem;
        }
        
        .recommendations h3 {
            color: {{ recommandations_color }};
            font-size: 1.3rem;
            margin-bottom: 1rem;
            padding-left: 20px;
            position: relative;
        }
        
        .recommendations h3:before {
            content: '⚠';
            position: absolute;
            left: 0;
            font-size: 1.5rem;
        }
        
        .recommendations ul {
            list-style: none;
            padding: 0;
        }
        
        .recommendations li {
            background: white;
            margin: 0.5rem 0;
            padding: 1rem;
            border-left: 4px solid {{ recommandations_color }};
            border-radius: 5px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.1);
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            padding: 2rem;
            text-align: center;
            margin-top: 3rem;
            border-radius: 10px;
        }
        
        .footer h4 {
            margin-bottom: 1rem;
            color: #3498db;
        }
        
        .footer p {
            margin: 0.3rem 0;
            opacity: 0.8;
        }
        
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>
    <!-- En-tête du rapport -->
    <div class="header">
        <h1>RAPPORT QUALITÉ DE L'AIR</h1>
        <p>Programme RESPIRE - Surveillance Scolaire</p>
    </div>

    <!-- Informations générales -->
    <div class="info-grid">
        <div class="info-card">
            <h3>Établissement</h3>
            <p>École ID: {{ location_id }}</p>
        </div>
        <div class="info-card">
            <h3>Date du Rapport</h3>
            <p>{{ report_date }}</p>
        </div>
        <div class="info-card">
            <h3>Dernière Mise à Jour</h3>
            <p>{{ last_update }}</p>
        </div>
        <div class="info-card">
            <h3>Statut Global</h3>
            <p style="color: {{ status_bg_color }};">{{ status }}</p>
        </div>
    </div>

    <!-- Résumé Exécutif -->
    <div class="section">
        <div class="section-header">
            📊 RÉSUMÉ EXÉCUTIF
        </div>
        <div class="section-content">
            <div class="iqa-summary">
                <div class="iqa-badge">
                    IQA: {{ iqa_value }}
                </div>
                <div class="iqa-details">
                    <h3>Statut Global: {{ status }}</h3>
                    <p>Polluant Principal: {{ polluant_principal }}</p>
                    <p>Dernière Mise à Jour: {{ last_update }}</p>
                </div>
            </div>
            
            <div class="chart-container">
                <img src="data:image/png;base64,{{ gauge_b64 }}" alt="Jauge IQA">
            </div>
        </div>
    </div>

    <!-- Données Détaillées -->
    <div class="section">
        <div class="section-header">
            📋 DONNÉES DÉTAILLÉES EN TEMPS RÉEL
        </div>
        <div class="section-content">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Paramètre</th>
                        <th>Valeur</th>
                        <th>Unité</th>
                        <th>Seuil</th>
                        <th>Évaluation</th>
                    </tr>
                </thead>
                <tbody>
                    {% for donnee in donnees_tableau %}
                    <tr>
                        <td><strong>{{ donnee.nom }}</strong></td>
                        <td>{{ donnee.valeur }}</td>
                        <td>{{ donnee.unite }}</td>
                        <td>{{ donnee.seuil }}</td>
                        <td class="evaluation-cell" style="background-color: {{ donnee.eval_color }};">
                            {{ donnee.evaluation }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Nouvelle page pour les graphiques -->
    <div class="page-break"></div>

    <!-- Dashboard Polluants -->
    <div class="section">
        <div class="section-header">
            📈 SURVEILLANCE EN TEMPS RÉEL
        </div>
        <div class="section-content">
            <div class="chart-container">
                <img src="data:image/png;base64,{{ dashboard_b64 }}" alt="Dashboard Polluants">
            </div>
        </div>
    </div>

    <!-- Évolution Temporelle -->
    <div class="section">
        <div class="section-header">
            📉 ÉVOLUTION TEMPORELLE - 7 DERNIERS JOURS
        </div>
        <div class="section-content">
            <div class="chart-container">
                <img src="data:image/png;base64,{{ evolution_b64 }}" alt="Évolution IQA">
            </div>
        </div>
    </div>

    <!-- Recommandations -->
    <div class="recommendations">
        <h3>{{ recommandations_title }}</h3>
        <ul>
            {% for recommandation in recommandations %}
            <li>{{ recommandation }}</li>
            {% endfor %}
        </ul>
    </div>

    <!-- Pied de page -->
    <div class="footer">
        <h4>INFORMATIONS TECHNIQUES</h4>
        <p>Capteurs: AirGradient - Norme: OMS 2021</p>
        <p>Fréquence: Mesures continues 24h/7j</p>
        <p>Location ID: {{ location_id }}</p>
        <p>Contact technique: support@respire.education</p>
        <p>Document généré automatiquement le {{ report_date }}</p>
    </div>
</body>
</html>
        """)
        
        # Rendu du template avec les données
        html_content = html_template.render(
            location_id=self.location_id,
            report_date=self.report_date.strftime("%d/%m/%Y à %H:%M"),
            last_update=current_data.get('last_update', 'N/A'),
            status=status,
            status_bg_color=status_bg_color,
            iqa_value=iqa_value,
            polluant_principal=polluant_principal,
            gauge_b64=gauge_b64,
            dashboard_b64=dashboard_b64,
            evolution_b64=evolution_b64,
            donnees_tableau=donnees_tableau,
            recommandations_title=recommandations_title,
            recommandations_color=recommandations_color,
            recommandations=recommandations
        )
        
        return html_content

    def generate_pdf_from_html(self, html_content: str, output_filename: str = None) -> str:
        """Convertit le HTML en PDF avec WeasyPrint"""
        if not output_filename:
            output_filename = f"rapport_qualite_air_{self.location_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        try:
            # CSS supplémentaire pour l'impression
            css_print = CSS(string="""
                @media print {
                    .chart-container img {
                        max-width: 100% !important;
                        page-break-inside: avoid;
                    }
                    .section {
                        page-break-inside: avoid;
                    }
                    .recommendations {
                        page-break-inside: avoid;
                    }
                }
            """)
            
            # Génération du PDF
            HTML(string=html_content).write_pdf(output_filename, stylesheets=[css_print])
            print(f"✅ PDF généré avec succès: {output_filename}")
            return output_filename
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération PDF: {e}")
            return None

def create_streamlit_interface():
    """Bouton Streamlit pour générer et télécharger le rapport"""

    if st.button("🚀 Générer le Rapport", type="primary", use_container_width=True):
        with st.spinner("Génération du rapport en cours..."):
            try:
                # Initialisation du générateur
                generator = HTMLReportGenerator(location_id_input, token_input)
                
                # Génération du HTML
                st.info("📝 Création du contenu HTML...")
                html_content = generator.generate_html_report()
                
                # Affichage HTML si demandé
                if format_output in ["HTML Preview", "Les deux"]:
                    st.success("✅ HTML généré avec succès!")
                    with st.expander("👀 Aperçu HTML", expanded=False):
                        st.components.v1.html(html_content, height=600, scrolling=True)
                    
                    # Téléchargement HTML
                    st.download_button(
                        label="📄 Télécharger HTML",
                        data=html_content,
                        file_name=f"rapport_html_{location_id_input}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                        mime="text/html"
                    )
                
                # Génération PDF si demandé
                if format_output in ["PDF", "Les deux"]:
                    st.info("📄 Conversion en PDF...")
                    pdf_filename = generator.generate_pdf_from_html(html_content)
                    
                    if pdf_filename and os.path.exists(pdf_filename):
                        st.success("✅ PDF généré avec succès!")
                        
                        # Informations sur le fichier
                        file_size = os.path.getsize(pdf_filename)
                        st.info(f"📏 Taille du fichier: {file_size:,} bytes")
                        
                        # Bouton de téléchargement PDF
                        with open(pdf_filename, "rb") as pdf_file:
                            st.download_button(
                                label="📄 Télécharger PDF",
                                data=pdf_file.read(),
                                file_name=pdf_filename,
                                mime="application/pdf"
                            )
                        
                        # Nettoyage
                        try:
                            os.remove(pdf_filename)
                        except:
                            pass
                    else:
                        st.error("❌ Erreur lors de la génération du PDF")
                        st.info("💡 Vous pouvez tout de même télécharger la version HTML")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
                st.info("🔧 Vérifiez vos paramètres et votre connexion internet")











