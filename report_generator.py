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
from config.settings import token,BASE_URL,VALEURS_LIMITE,DATA_DIR,location_ids


# Configuration existante (gardée de votre code)

location_id = "164928"

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


def generate_report(location_id: str) -> str:
    """
    Génère un rapport PDF et retourne le chemin du fichier créé.
    """
    try:
        generator = HTMLReportGenerator(location_id, token)
        html_content = generator.generate_html_report()
        pdf_filename = generator.generate_pdf_from_html(html_content)
        return pdf_filename if pdf_filename and os.path.exists(pdf_filename) else None
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF: {e}")
        return None


