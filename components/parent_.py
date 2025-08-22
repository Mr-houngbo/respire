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
from config.settings import token,BASE_URL,VALEURS_LIMITE,location_ids,DATA_DIR,liens
from src.functions import fetch_current_data,calculer_iqa,afficher_iqa_plot,calculer_iqa_journalier,get_past_measures,calculate_air_quality_status




# Configuration 
location_id = location_ids[6]
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data/air_quality')


#=============================================================================================================

def show_header(nom_ecole, logo_path: str = None):
    """
    Affiche un en-tête simple et élégant pour la page Parents.
    :param nom_ecole: Nom de l'école à afficher (optionnel)
    :param logo_path: Chemin vers le logo de l'école (optionnel)
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
        margin: 0 0 0.5rem 0;
        font-weight: 400;
        line-height: 1.4;
    }
    
    .school-name {
        font-size: 1.1rem;
        color: #495057;
        font-weight: 500;
        margin: 0;
    }
    
    .logo-container {
        flex-shrink: 0;
        margin-left: 2rem;
    }
    
    .logo-container img {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        max-width: 80px;
        height: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        # Création du contenu HTML complet dans une seule div
        logo_html = ""
        if logo_path:
            logo_html = f'<div class="logo-container"><img src="{logo_path}" alt="Logo école" /></div>'
        
        school_name_html = ""
        if nom_ecole:
            school_name_html = f'<div class="school-name">{nom_ecole}</div>'
        
        st.markdown(f'''
        <div class="header-container">
            <div class="header-content">
                <div class="title-main">
                    Bienvenue sur l'espace parents de Respire
                </div>
                <div class="subtitle">
                    Découvrez comment va l'air de l'école de votre enfant aujourd'hui !
                </div>
                {school_name_html}
            </div>
            {logo_html}
        </div>
        ''', unsafe_allow_html=True)


def show_air_status_summary(school_name="École Multinationale des Télécommunications"):
    """
    BLOC I: Affiche l'état de l'air aujourd'hui - Version parents
    Grande carte récap' simplifiée, compréhensible en 5 secondes
    """
    
    st.markdown("## État de l'air aujourd'hui à l'école")
    
    # Récupération des données
    df = fetch_current_data(location_id, token)
    air_status = calculate_air_quality_status(df)
    
    if not air_status:
        st.error("❌ Impossible de récupérer les données de qualité de l'air")
        return
    
    # CSS pour la grande carte
    st.markdown("""
    <style>
    .air-status-card {{
        background: linear-gradient(135deg, {color}15, {color}08);
        border: 3px solid {color}40;
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 10px 30px {color}20;
        position: relative;
        overflow: hidden;
    }}
    
    .status-icon {{
        font-size: 4rem;
        margin-bottom: 10px;
        animation: pulse 2s ease-in-out infinite;
    }}
    
    .status-title {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {color};
        margin-bottom: 5px;
    }}
    
    .status-message {{
        font-size: 1.3rem;
        color: #333;
        margin-bottom: 10px;
        line-height: 1.5;
    }}
    
    .status-advice {{
        font-size: 1.1rem;
        color: #666;
        font-style: italic;
        margin-bottom: 15px;
    }}
    
    .school-info {{
        background: inherit;
        padding: 15px;
        border-radius: 15px;
        margin-top: 10px;
    }}
    
    .last-update {{
        font-size: 0.9rem;
        color: #888;
        margin-top: 5px;
    }}
    
    @keyframes pulse {{
        0%%, 100%% {{ transform: scale(1); }}
        50%% {{ transform: scale(1.1); }}
    }}
    </style>
    """.format(color=air_status["color"]), unsafe_allow_html=True)
    
    # Grande carte de statut
    st.markdown(f'''
    <div class="air-status-card" style="
        background: linear-gradient(135deg, {air_status["color"]}15, {air_status["color"]}08);
        border: 3px solid {air_status["color"]}40;
        box-shadow: 0 10px 30px {air_status["color"]}20;
    ">
        <div class="status-icon">{air_status["icon"]}</div>
        <div class="status-title" style="color: {air_status["color"]};">
            Qualité: {air_status["status"]}
        </div>
        <div class="status-message">
            {air_status["message"]}
            {air_status["advice"]}
        </div>
        <div class="school-info">
            <div style="font-size: 1.1rem; color: #333; font-weight: 600;">
                 {school_name}
            </div>
            <div class="last-update">
                🕐 Dernière mesure: {air_status["last_update"]}
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Indicateurs rapides en bas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        
        
        
        pm25_color = "#4caf50" if air_status["pm25"] <= 15 else "#ff9800" if air_status["pm25"] <= 35 else "#f44336"
        st.markdown(f'''
        <div style="background: {pm25_color}20; padding: 15px; border-radius: 15px; text-align: center;">
            <div style="font-size: 1.5rem;">🌫️</div>
            <div style="font-weight: bold; color: {pm25_color};">PM2.5</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{air_status["pm25"]:.1f}</div>
            <div style="font-size: 0.8rem; color: #666;">µg/m³</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        co2_color = "#4caf50" if air_status["co2"] <= 800 else "#ff9800" if air_status["co2"] <= 1000 else "#f44336"
        st.markdown(f'''
        <div style="background: {co2_color}20; padding: 15px; border-radius: 15px; text-align: center;">
            <div style="font-size: 1.5rem;">💨</div>
            <div style="font-weight: bold; color: {co2_color};">CO₂</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{air_status["co2"]:.0f}</div>
            <div style="font-size: 0.8rem; color: #666;">ppm</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        temp_color = "#4caf50" if 18 <= air_status["temp"] <= 26 else "#ff9800"
        st.markdown(f'''
        <div style="background: {temp_color}20; padding: 15px; border-radius: 15px; text-align: center;">
            <div style="font-size: 1.5rem;">🌡️</div>
            <div style="font-weight: bold; color: {temp_color};">Temp.</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{air_status["temp"]:.1f}°C</div>
            <div style="font-size: 0.8rem; color: #666;">intérieur</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        humidity_color = "#4caf50" if 40 <= air_status["humidity"] <= 60 else "#ff9800"
        st.markdown(f'''
        <div style="background: {humidity_color}20; padding: 15px; border-radius: 15px; text-align: center;">
            <div style="font-size: 1.5rem;">💧</div>
            <div style="font-weight: bold; color: {humidity_color};">Humidité</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{air_status["humidity"]:.0f}%</div>
            <div style="font-size: 0.8rem; color: #666;">relative</div>
        </div>
        ''', unsafe_allow_html=True)
        
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)

def show_health_parameters():
    """
    BLOC II: Paramètres de santé critiques
    Indicateurs clés avec seuils explicites et explications pour les parents
    """
    
    st.markdown("## Paramètres de santé à surveiller")
    st.markdown("*Comprendre les indicateurs qui affectent la santé de votre enfant*")
    
    # Récupération des données
    df = fetch_current_data(location_id, token)
    df = pd.DataFrame([df])
    if df.empty:
        st.warning("Données non disponibles pour le moment")
        return
    
    # Extraction des valeurs
    
    pm25 = df["pm25"].iloc[0]
    co2 = df["co2"].iloc[0] 
    temp = df["temp"].iloc[0]
    humidity = df["humidity"].iloc[0]
    
    # CSS pour les cartes de paramètres
    st.markdown("""
    <style>
    .health-param-card {
        background: white;
        border-radius: 20px;
        padding: 15px;
        margin: 0px 0;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
        border-left: 6px solid;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .health-param-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 35px rgba(0,0,0,0.15);
    }
    
    .param-header {
        display: flex;
        align-items: center;
        margin-bottom: 5px;
    }
    
    .param-icon {
        font-size: 2.5rem;
        margin-right: 15px;
    }
    
    .param-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .param-value {
        font-size: 2rem;
        font-weight: 900;
        margin: 5px 0;
    }
    
    .param-status {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 8px 15px;
        border-radius: 25px;
        display: inline-block;
        margin: 10px 0;
    }
    
    .param-explanation {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .param-advice {
        background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 4px solid #2196f3;
    }
    
    .threshold-indicator {
        display: flex;
        justify-content: space-between;
        background: #f5f5f5;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Fonction pour déterminer le statut d'un paramètre
    def get_param_status(value, thresholds, unit=""):
        if value <= thresholds[0]:
            return {"status": "Excellent", "color": "#4caf50", "bg": "#e8f5e8"}
        elif value <= thresholds[1]:
            return {"status": "Bon", "color": "#8bc34a", "bg": "#f1f8e9"}
        elif value <= thresholds[2]:
            return {"status": "Moyen", "color": "#ff9800", "bg": "#fff3e0"}
        else:
            return {"status": "Préoccupant", "color": "#f44336", "bg": "#ffebee"}
    
    
    col1,col2 = st.columns(2)
    
    with col1:
            
        # 1. PM2.5 - Particules fines
        pm25_status = get_param_status(pm25, [12, 25, 35])
        st.markdown(f'''
        <div class="health-param-card" style="border-left-color: {pm25_status["color"]};">
            <div class="param-header">
                <div>
                    <div class="param-title" style="color: {pm25_status["color"]};">PM2.5 - Particules fines</div>
                    <div style="color: #666; font-size: 0.9rem;">Poussières invisibles dans l'air</div>
                </div>
            </div>
            <div class="param-explanation">
                <h4> Qu'est-ce que c'est ?</h4>
                Les PM2.5 sont des particules si petites qu'elles peuvent pénétrer profondément dans les poumons de votre enfant. 
                Elles proviennent de la pollution des véhicules, de la poussière, ou des fumées.
                <h4> Effets sur la santé</h4>
                <b>Exposition faible:</b> Aucun problème<br>
                <b>Exposition moyenne:</b> Peut causer toux, irritation des yeux<br>
                <b>Exposition élevée:</b> Difficultés respiratoires, fatigue
            </div>
            <div class="threshold-indicator">
                <span style="color: #4caf50;">🟢 Excellent: 0-12</span>
                <span style="color: #ff9800;">🟡 Moyen: 12-35</span>
                <span style="color: #f44336;">🔴 Élevé: >35</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # st.markdown("---")
    
    with col2:
          
        # 2. CO₂ - Qualité de l'air intérieur
        co2_status = get_param_status(co2, [600, 800, 1000])
        st.markdown(f'''
        <div class="health-param-card" style="border-left-color: {co2_status["color"]};">
            <div class="param-header">
                <div>
                    <div class="param-title" style="color: {co2_status["color"]};">CO₂ - Dioxyde de carbone</div>
                    <div style="color: #666; font-size: 0.9rem;">Indicateur de ventilation en classe</div>
                </div>
            </div>
            <div class="param-explanation">
                <h4> Qu'est-ce que c'est ?</h4>
                Le CO₂ nous indique si la classe est bien aérée. Quand il y a beaucoup d'élèves dans une pièce fermée, 
                le taux de CO₂ augmente et l'oxygène diminue.
                <h4>Effets sur la santé</h4>
                <b>Taux normal:</b> Concentration et apprentissage optimaux<br>
                <b>Taux élevé:</b> Fatigue, somnolence, difficultés de concentration<br>
                <b>Taux très élevé:</b> Maux de tête, sensation d'étouffement
            </div>
            <div class="threshold-indicator">
                <span style="color: #4caf50;">🟢 Excellent: <600</span>
                <span style="color: #ff9800;">🟡 Moyen: 600-1000</span>
                <span style="color: #f44336;">🔴 Élevé: >1000</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
    
    
    col1,col2 = st.columns(2)
    
    with col1:
        
        # 3. Température
        temp_status = get_param_status(abs(temp - 22), [2, 4, 6]) # Écart par rapport à 22°C idéal
        st.markdown(f'''

        <div class="health-param-card" style="border-left-color: {temp_status["color"]};"> 
            <div class="param-header">
                <div> 
                    <div class="param-title" style="color: {temp_status["color"]};">Température extérieure</div> 
                    <div style="color: #666; font-size: 0.9rem;">Température mesurée dans la cour de l’école</div>
                </div> 
            </div>
            <div class="param-explanation">
                <h4> Pourquoi c'est important ?</h4>
                Une température agréable dans l’enceinte de l’école permet aux élèves de profiter pleinement des temps de pause et des activités extérieures.
                Une chaleur excessive ou un froid trop intense peut affecter leur confort général. 
                <h4> Effets possibles</h4> <b>18-24°C:</b> Conditions optimales en extérieur<br> 
                <b>Trop chaud (>26°C):</b> Risque de fatigue, déshydratation<br> <b>Trop froid (<18°C):</b> Inconfort, besoin de se couvrir
            </div> 
            <div class="threshold-indicator">
                <span style="color: #4caf50;">🟢 Idéal: 20-24°C</span> 
                <span style="color: #ff9800;">🟡 Acceptable: 18-26°C</span> <span style="color: #f44336;">🔴 Inconfortable: &lt;18 ou &gt;26°C</span>
            </div> 
        </div> ''', unsafe_allow_html=True)
                
        # st.markdown("---")
    
    with col2:
         
        # 4. Humidité
        humidity_status = get_param_status(abs(humidity - 50), [10, 20, 30])  # Écart par rapport à 50% idéal
        st.markdown(f'''
        <div class="health-param-card" style="border-left-color: {humidity_status["color"]};">
            <div class="param-header">
                <div>
                    <div class="param-title" style="color: {humidity_status["color"]};">Humidité relative</div>
                    <div style="color: #666; font-size: 0.9rem;">Taux d'humidité dans l'air</div>
                </div>
            </div>
            <div class="param-explanation">
                <h4> Qu'est-ce que c'est ?</h4>
                L'humidité influence la propagation des virus et le confort respiratoire. 
                Un air trop sec ou trop humide peut causer des problèmes.
                <h4>Effets sur la santé</h4>
                <b>40-60%:</b> Idéal pour la santé respiratoire<br>
                <b>Trop sec (<40%):</b> Irritation des voies respiratoires, nez sec<br>
                <b>Trop humide (>60%):</b> Favorise moisissures et virus<br>
            </div>
            <div class="threshold-indicator">
                <span style="color: #4caf50;">🟢 Idéal: 40-60%</span>
                <span style="color: #ff9800;">🟡 Acceptable: 30-70%</span>
                <span style="color: #f44336;">🔴 Problématique: <30% ou >70%</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

@st.cache_data(ttl=60) # expire au bout de 5 min
def render_bloc_tendances(location_id: str = location_id, school_name="ESMT"):
    """
    Bloc III - Tendances pour la page Parent
    Utilise les fonctions existantes et les données CSV locales
    """
    
    st.markdown("### **Évolution cette semaine**")
    
    # Container principal avec style
    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                    border: 1px solid #dee2e6;">
        """, unsafe_allow_html=True)
        
        # === RÉCUPÉRATION DES DONNÉES ===
        csv_filename = f"{DATA_DIR}/{location_id}.csv"
        
        # Vérifier si le fichier CSV existe
        if os.path.exists(csv_filename):
            try:
                df_historical = pd.read_csv(csv_filename)
                df_historical['date'] = pd.to_datetime(df_historical['Local Date/Time'])
                
                # Prendre les 7 derniers jours
                recent_data = df_historical.tail(7).copy()
                
                if len(recent_data) == 0:
                    st.warning("Aucune donnée historique disponible pour cette école.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    return
                    
            except Exception as e:
                st.error(f"Erreur lors du chargement des données : {e}")
                st.markdown("</div>", unsafe_allow_html=True)
                return
        else:
            st.warning(f"Fichier de données non trouvé : {csv_filename}")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        
        # Colonnes pour organiser l'affichage
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # === MINI GRAPHIQUE D'ÉVOLUTION ===
            st.markdown("#### **Qualité de l'air - 7 derniers jours**")
            
            # Utiliser les vraies colonnes de tes données
            pm25_col = 'PM2.5 (μg/m³) corrected' if 'PM2.5 (μg/m³) corrected' in recent_data.columns else 'pm25'
            co2_col = 'CO2 (ppm) corrected' if 'CO2 (ppm) corrected' in recent_data.columns else 'co2'
            temp_col = 'Temperature (°C) corrected' if 'Temperature (°C) corrected' in recent_data.columns else 'temperature'
            humidity_col = 'Humidity (%) corrected' if 'Humidity (%) corrected' in recent_data.columns else 'humidity'
            
            # Fonction pour déterminer le statut (utilise ta logique existante)
            def get_air_quality_status_from_pm25(pm25):
                if pm25 <= 10:
                    return "Excellente", "#4caf50"
                elif pm25 <= 15:
                    return "Bonne", "#8bc34a"
                elif pm25 <= 35:
                    return "Moyenne", "#ff9800"
                elif pm25 <= 55:
                    return "Mauvaise", "#f44336"
                else:
                    return "Très mauvaise", "#d32f2f"
            
            # Vérifier que la colonne PM2.5 existe
            if pm25_col in recent_data.columns:
                # Calcul des statuts pour chaque jour
                recent_data['status'], recent_data['color'] = zip(*recent_data[pm25_col].apply(get_air_quality_status_from_pm25))
                
                # Graphique sparkline avec Plotly
                fig = go.Figure()
                
                # Ligne principale
                fig.add_trace(go.Scatter(
                    x=recent_data['date'],
                    y=recent_data[pm25_col],
                    mode='lines+markers',
                    line=dict(color='#007bff', width=3),
                    marker=dict(size=8, color=recent_data['color']),
                    name='PM2.5 (µg/m³)',
                    hovertemplate='<b>%{x|%d/%m}</b><br>' +
                                 'PM2.5: %{y:.1f} µg/m³<br>' +
                                 '<extra></extra>'
                ))
                
                # Zones de seuils (selon ta logique)
                fig.add_hline(y=10, line_dash="dash", line_color="#4caf50", 
                             annotation_text="Seuil Excellent", annotation_position="right")
                fig.add_hline(y=15, line_dash="dash", line_color="#8bc34a", 
                             annotation_text="Seuil Bon", annotation_position="right")
                fig.add_hline(y=35, line_dash="dash", line_color="#ff9800", 
                             annotation_text="Seuil Moyen", annotation_position="right")
                
                fig.update_layout(
                    height=300,
                    margin=dict(l=0, r=0, t=20, b=0),
                    showlegend=False,
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='lightgray',
                        tickformat='%d/%m'
                    ),
                    yaxis=dict(
                        title="PM2.5 (µg/m³)",
                        showgrid=True,
                        gridcolor='lightgray'
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # === RÉSUMÉ DE LA SEMAINE ===
                st.markdown("#### **Résumé de la semaine**")
                
                # Calculs statistiques sur les vraies données
                avg_pm25 = recent_data[pm25_col].mean()
                max_pm25 = recent_data[pm25_col].max()
                days_over_threshold = len(recent_data[recent_data[pm25_col] > 35])
                
                # Affichage en colonnes
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    status_avg = "Correct" if avg_pm25 <= 25 else "Élevé"
                    delta_color = "normal" if avg_pm25 <= 25 else "inverse"
                    st.metric(
                        label=" Moyenne PM2.5", 
                        value=f"{avg_pm25:.1f} µg/m³",
                        delta=status_avg,
                        delta_color=delta_color
                    )
                
                with col_stat2:
                    status_max = "Acceptable" if max_pm25 <= 35 else "Préoccupant"
                    delta_color = "normal" if max_pm25 <= 35 else "inverse"
                    st.metric(
                        label=" Pic maximum", 
                        value=f"{max_pm25:.1f} µg/m³",
                        delta=status_max,
                        delta_color=delta_color
                    )
                
                with col_stat3:
                    status_days = "Aucun souci" if days_over_threshold == 0 else "À surveiller"
                    delta_color = "normal" if days_over_threshold == 0 else "inverse"
                    st.metric(
                        label=" Jours d'alerte", 
                        value=f"{days_over_threshold} jour(s)",
                        delta=status_days,
                        delta_color=delta_color
                    )
            else:
                st.error(f"Colonne PM2.5 non trouvée dans les données. Colonnes disponibles : {list(recent_data.columns)}")
        
        with col2:
            
            # === PLAGES HORAIRES CRITIQUES ===
            st.markdown("#### **Analyse par jour**")
            
            # Analyser chaque jour des données réelles
            if pm25_col in recent_data.columns:
                for idx, row in recent_data.iterrows():
                    
                    jours_fr = {                                      # Pour la convertion du Nom du jour en francais 
                            "Monday": "Lundi",
                            "Tuesday": "Mardi",
                            "Wednesday": "Mercredi",
                            "Thursday": "Jeudi",
                            "Friday": "Vendredi",
                            "Saturday": "Samedi",
                            "Sunday": "Dimanche"
                            }
                    date_str = jours_fr[row['date'].strftime('%A')]   # Nom du jour
                                                
                    
                    pm25_val = row[pm25_col]
                    # Déterminer le statut du jour
                    if pm25_val <= 15:
                        icon = ""
                        level = "Bon"
                        color = "#28a745"
                        message = f"{date_str} : {icon} Journée saine (PM2.5: {pm25_val:.1f})"
                    elif pm25_val <= 35:
                        icon = ""
                        level = "Moyen"
                        color = "#ffc107"
                        message = f"{date_str} : {icon} Qualité correcte (PM2.5: {pm25_val:.1f})"
                    else:
                        icon = ""
                        level = "Élevé"
                        color = "#dc3545"
                        message = f"{date_str} : {icon} Pollution détectée (PM2.5: {pm25_val:.1f})"
                    st.markdown(f"""
                    <div style="background-color: {color}15; 
                               border-left: 4px solid {color}; 
                               padding: 8px 12px; margin: 5px 0; border-radius: 5px;">
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
            
            # === ALERTES AUTOMATIQUES ===
            st.markdown("#### Alertes de la semaine")
            
            if pm25_col in recent_data.columns:
                days_over_threshold = len(recent_data[recent_data[pm25_col] > 35])
                
                if days_over_threshold > 0:
                    max_pollution_day = recent_data.loc[recent_data[pm25_col].idxmax()]
                    st.markdown(f"""
                    <div style="background-color: #dc354520; border: 1px solid #dc3545; 
                               border-radius: 8px; padding: 15px; margin: 10px 0;">
                        <strong> {days_over_threshold} jour(s) avec dépassement de seuil</strong><br>
                        <small>Pic de {max_pollution_day[pm25_col]:.1f} µg/m³ le {max_pollution_day['date'].strftime('%d/%m')}. 
                        Surveillez les symptômes respiratoires.</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background-color: #28a74520; border: 1px solid #28a745; 
                               border-radius: 8px; padding: 15px; margin: 10px 0;">
                        <strong> Aucune alerte cette semaine</strong><br>
                        <small>La qualité de l'air est restée dans les normes acceptables.</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # === INTERPRÉTATION AUTOMATIQUE (utilise ta logique existante) ===
        st.markdown("#### **Ce que cela signifie pour votre enfant**")
        
        if pm25_col in recent_data.columns:
            avg_pm25 = recent_data[pm25_col].mean()
            
            # Générer des conseils basés sur ta logique calculate_air_quality_status
            if avg_pm25 <= 15:
                interpretation = """
                 Excellente nouvelle ! L'air à l'école a été globalement de très bonne qualité cette semaine. 
                Votre enfant peut participer à toutes les activités sans contrainte particulière.
                """
                advice_color = "#4caf50"
            elif avg_pm25 <= 35:
                interpretation = """
                 Qualité correcte mais à surveiller. Quelques variations ont été observées. 
                Encouragez votre enfant à bien s'hydrater et surveillez d'éventuels symptômes (toux, fatigue).
                """
                advice_color = "#ff9800"
            else:
                interpretation = """
                 Attention requise. La qualité de l'air a été préoccupante plusieurs jours. 
                Consultez un médecin si votre enfant présente toux persistante, maux de tête ou fatigue inhabituelle.
                """
                advice_color = "#f44336"
            st.markdown(f"""
            <div style="background-color: {advice_color}15; border: 2px solid {advice_color}; 
                       border-radius: 10px; padding: 20px; margin: 15px 0;">
                {interpretation}
            </div>
            """, unsafe_allow_html=True)

@st.cache_data(ttl=60) # expire au bout de 5 min
def render_bloc_conseils(location_id: str = location_id, token: str = token, school_name="ESMT"):
    """
    Bloc IV - Conseils/Actions préventives pour la page Parent
    Conseils personnalisés selon la qualité de l'air à l'école de l'enfant
    """
    
    st.markdown("### **Conseils & Actions préventives**")
    
    # Récupérer les données actuelles de l'école
    current_data = fetch_current_data(location_id, token)
    air_status = calculate_air_quality_status(current_data) if not current_data.empty else None
    
    # Container principal
    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%); 
                    padding: 25px; border-radius: 15px; margin-bottom: 20px; 
                    border: 1px solid #b3d9ff;">
        """, unsafe_allow_html=True)
        
        if air_status:
            # === SECTION 1: QUE PUIS-JE FAIRE À LA MAISON ? ===
            st.markdown("#### **Que puis-je faire à la maison ?**")
            
            # Conseils personnalisés selon la qualité de l'air à l'école
            pm25 = air_status['pm25']
            co2 = air_status['co2']
            status = air_status['status']
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("##### **Préparation du matin**")
                
                if pm25 <= 15:  # Air de bonne qualité à l'école
                    morning_tips = [
                        " <strong>Petit-déjeuner copieux</strong> - Votre enfant peut dépenser son énergie normalement",
                        " <strong>Fenêtres ouvertes</strong> - Aérez sa chambre avant le départ pour l'école",
                        " <strong>Habits légers</strong> - Pas de protection particulière nécessaire",
                        " <strong>Gourde d'eau</strong> - Hydratation normale suffit"
                    ]
                    tips_color = "#d4edda"
                    border_color = "#28a745"
                elif pm25 <= 35:  # Air moyen à l'école
                    morning_tips = [
                        " <strong>Petit-déjeuner riche</strong> - Donnez-lui des forces pour la journée",
                        " <strong>Aération matinale</strong> - Ouvrez 5-10 min quand l'air extérieur est plus frais",
                        " <strong>Veste légère</strong> - Au cas où l'école limite les sorties",
                        " <strong>Grande gourde</strong> - Encouragez à boire plus que d'habitude"
                    ]
                    tips_color = "#fff3cd"
                    border_color = "#ffc107"
                else:  # Air pollué à l'école
                    morning_tips = [
                        " <strong>Petit-déjeuner énergétique</strong> - Fruits, céréales pour renforcer ses défenses",
                        " <strong>Fenêtres fermées</strong> - Gardez l'air intérieur propre avant le départ",
                        " <strong>Masque dans le sac</strong> - Si l'école le demande ou si trajet à pied",
                        " <strong>Double hydratation</strong> - Prévoyez une grande gourde + thermos"
                    ]
                    tips_color = "#f8d7da"
                    border_color = "#dc3545"
                
                # Affichage des conseils
                for tip in morning_tips:
                    st.markdown(f"""
                    <div style="background-color: {tips_color}; border-left: 4px solid {border_color}; 
                               padding: 10px; margin: 8px 0; border-radius: 5px;">
                        {tip}
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#####  **Après l'école**")
                
                if pm25 <= 15:  # Air de bonne qualité
                    evening_tips = [
                        " <strong>Activités extérieures</strong> - Parfait pour jouer dehors après l'école",
                        " <strong>Douche normale</strong> - Pas de précautions particulières",
                        " <strong>Repas équilibré</strong> - Alimentation normale suffit",
                        " <strong>Coucher habituel</strong> - Son organisme n'est pas stressé"
                    ]
                    tips_color = "#d4edda"
                    border_color = "#28a745"
                elif pm25 <= 35:  # Air moyen
                    evening_tips = [
                        " <strong>Activités à l'intérieur</strong> - Privilégiez les jeux calmes en rentrant",
                        " <strong>Douche rapide</strong> - Rincez le visage et les mains",
                        " <strong>Fruits vitaminés</strong> - Oranges, kiwis pour renforcer l'immunité",
                        " <strong>Écoutez-le</strong> - Demandez s'il a ressenti de la fatigue ou gêne"
                    ]
                    tips_color = "#fff3cd"
                    border_color = "#ffc107"
                else:  # Air pollué
                    evening_tips = [
                        " <strong>Rentrez vite</strong> - Évitez les détours et jeux extérieurs",
                        " <strong>Douche obligatoire</strong> - Cheveux et visage pour éliminer les particules",
                        " <strong>Alimentation anti-oxydante</strong> - Légumes colorés, thé léger",
                        " <strong>Surveillance</strong> - Vérifiez toux, maux de tête ou fatigue inhabituelle"
                    ]
                    tips_color = "#f8d7da"
                    border_color = "#dc3545"
                
                # Affichage des conseils du soir
                for tip in evening_tips:
                    st.markdown(f"""
                    <div style="background-color: {tips_color}; border-left: 4px solid {border_color}; 
                               padding: 10px; margin: 8px 0; border-radius: 5px;">
                        {tip}
                    </div>
                    """, unsafe_allow_html=True)
            
            # === SECTION 2: QUAND DOIS-JE M'INQUIÉTER ? ===
            st.markdown("---")
            st.markdown("#### **Quand dois-je m'inquiéter ?**")
            
            # Seuils d'alerte personnalisés selon l'école
            col_alert1, col_alert2 = st.columns([1, 1])
            
            with col_alert1:
                st.markdown("##### **Symptômes à surveiller**")
                
                if pm25 <= 15:
                    alert_message = """
                    <div style="background-color: #d4edda; border: 2px solid #28a745; 
                               border-radius: 10px; padding: 15px;">
                        <strong>😊 Situation rassurante</strong><br>
                        L'air à l'école est de bonne qualité. Les symptômes suivants sont peu probables 
                        mais restez attentif à :
                        <ul>
                            <li>Toux persistante (+ de 2 jours)</li>
                            <li>Fatigue inhabituelle</li>
                            <li>Maux de tête fréquents</li>
                        </ul>
                    </div>
                    """
                elif pm25 <= 35:
                    alert_message = """
                    <div style="background-color: #fff3cd; border: 2px solid #ffc107; 
                               border-radius: 10px; padding: 15px;">
                        <strong>⚠️ Vigilance modérée</strong><br>
                        L'air à l'école est correct mais surveillez ces signaux :
                        <ul>
                            <li><strong>Toux sèche</strong> en rentrant de l'école</li>
                            <li><strong>Yeux qui piquent</strong> ou nez qui coule</li>
                            <li><strong>Fatigue</strong> après les récréations</li>
                            <li><strong>Difficultés de concentration</strong> en classe</li>
                        </ul>
                    </div>
                    """
                else:
                    alert_message = """
                    <div style="background-color: #f8d7da; border: 2px solid #dc3545; 
                               border-radius: 10px; padding: 15px;">
                        <strong>🚨 Surveillance renforcée</strong><br>
                        L'air à l'école est pollué. Consultez un médecin si votre enfant présente :
                        <ul>
                            <li><strong>Toux persistante</strong> (surtout le soir)</li>
                            <li><strong>Essoufflement</strong> inhabituel</li>
                            <li><strong>Maux de tête</strong> fréquents</li>
                            <li><strong>Irritation des yeux/gorge</strong></li>
                            <li><strong>Fatigue extrême</strong> au retour</li>
                        </ul>
                    </div>
                    """
                
                st.markdown(alert_message, unsafe_allow_html=True)
            
            with col_alert2:
                st.markdown("#####  **Actions à entreprendre**")
                
                # Actions spécifiques selon le niveau de pollution à l'école
                if pm25 <= 15:
                    action_items = [
                        ("", "<strong>Dialogue avec l'enfant</strong>", "Demandez-lui comment il se sent à l'école"),
                        ("", "<strong>Suivi scolaire normal</strong>", "Aucune restriction d'activité nécessaire"),
                        ("", "<strong>Médecin si nécessaire</strong>", "Seulement si symptômes inhabituels persistent pendant plusieurs jours ")
                    ]
                    action_color = "#28a745"
                elif pm25 <= 35:
                    action_items = [
                        ("", "<strong>Contact avec l'école</strong>", "Demandez si d'autres enfants ont des symptômes"),
                        ("", "<strong>Hydratation renforcée</strong>", "Encouragez à boire plus pendant les pauses"),
                        ("", "<strong>Médecin si symptoms</strong>", "Consultation si toux + fatigue > 3 jours"),
                        ("", "<strong>Journal des symptômes</strong>", "Notez les moments où l'enfant tousse")
                    ]
                    action_color = "#ffc107"
                else:
                    action_items = [
                        ("", "<strong>Contact école immédiat</strong>", "Signalez les symptômes à l'enseignant"),
                        ("", "<strong>Médecin rapidement</strong>", "Consultation si symptômes > 24h"),
                        ("", "<strong>Alertes pollution</strong>", "Installez une app météo avec qualité de l'air"),
                        ("", "<strong>Adaptation à domicile</strong>", "Purificateur d'air si possible"),
                        ("", "<strong>Suivi quotidien</strong>", "Température, toux, énergie de l'enfant")
                    ]
                    action_color = "#dc3545"
                
                for icon, title, description in action_items:
                    st.markdown(f"""
                    <div style="border-left: 4px solid {action_color}; padding: 10px; margin: 8px 0;">
                        <strong>{icon} {title}</strong><br>
                        <small>{description}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # === SECTION 3: RESSOURCES ET CONTACTS ===
            st.markdown("---")
            st.markdown("#### 📚 **Ressources utiles**")
            
            col_resource1, col_resource2 = st.columns([1, 1])
            
            with col_resource1:
                st.markdown("""
                ##### 📖 **En savoir plus**
                
                - 🫁 **Qu'est-ce que le PM2.5 ?** → Particules fines qui pénètrent dans les poumons
                - 🏫 **Pourquoi surveiller à l'école ?** → Les enfants y passent 6-8h par jour
                - 💨 **CO₂ et concentration** → Trop de CO₂ fatigue et réduit l'attention
                - 🌡️ **Température et confort** → Impact sur l'apprentissage
                """)
            
            with col_resource2:
                st.markdown(f"""
                ##### 📞 **Contacts d'urgence**
                
                - 🏫 <strong>École</strong> : {school_name}
                - 📞 <strong>Direction</strong> : [Ici on mets le numero de Bernard T.]
                - 🚑 <strong>SAMU</strong> : 15 (urgences médicales)
                - 🏥 <strong>Centre de santé local</strong> : [Ici on mets le numero de M. Laminou S L.]
                
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <strong>💡 Conseil :</strong> Gardez ces numéros dans votre téléphone !
                </div>
                """, unsafe_allow_html=True)
        
        else:
            # Si pas de données disponibles
            st.warning("⚠️ Données de qualité de l'air non disponibles pour le moment.")
            st.markdown("""
            **En attendant, voici quelques conseils généraux :**
            - 💧 Encouragez votre enfant à bien s'hydrater à l'école
            - 🧼 Rappellez-lui de se laver les mains régulièrement
            - 👂 Demandez-lui comment il se sent après l'école
            - 📞 Contactez l'école si vous avez des préoccupations
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)

    
def graphique_iqa(location_id,token):

    if st.button("Decouvrir l'evolution de l'IQA sur les 7 derniers jours",key="graphique_iqa_button"):
        with st.spinner("🔄 Récupération des données..."):
            df = get_past_measures(location_id, token)
            if not df.empty:
                iqa_jour = calculer_iqa_journalier(df,location_id)
                afficher_iqa_plot(iqa_jour, df['locationName'].iloc[0])


#====================================================================================================================================

