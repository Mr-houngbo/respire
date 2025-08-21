from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import io
import os
import pandas as pd
import requests
from urllib.parse import urlencode, quote_plus
from datetime import datetime, timedelta
import numpy as np
import tempfile
from typing import Dict, List, Tuple, Optional
import seaborn as sns
from config.settings import token,BASE_URL,VALEURS_LIMITE,DATA_DIR,location_ids
import streamlit as st 


# Configuration pour éviter les warnings
import warnings
warnings.filterwarnings("ignore")

# Configuration matplotlib pour un rendu professionnel
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

POLLUANTS_NOMS = {
    "pm02_corrected": "PM2.5",
    "pm10_corrected": "PM10",
    "pm01_corrected": "PM1",
    "rco2_corrected": "CO2",
    "tvoc": "COV Totaux",
    "noxIndex": "NOx",
    "atmp_corrected": "Temperature",
    "rhum_corrected": "Humidite"
}

# Couleurs pour les différents niveaux
COLORS = {
    'bon': '#27AE60',          # Vert
    'modere': '#F39C12',       # Orange
    'mauvais': '#E74C3C',      # Rouge
    'critique': '#8E44AD',     # Violet
    'primary': '#2C3E50',      # Bleu foncé
    'secondary': '#34495E',    # Gris bleu
    'accent': '#3498DB'        # Bleu clair
}

location_id = "164928"






#=============================================================================================================
@st.cache_data(ttl=300)
def get_measures_range(location_id: int, token: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    """
    Récupère les données pour un `location_id` donné entre from_date et to_date (max 10 jours API).
    """
    base_url = "https://api.airgradient.com/public/api/v1/locations"
    url = f"{base_url}/{location_id}/measures/past"

    params = {
        "token": token,
        "from": from_date.strftime('%Y%m%dT%H%M%SZ'),
        "to": to_date.strftime('%Y%m%dT%H%M%SZ'),
    }


    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, params=params, headers=headers, timeout=15)

    
    # response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    else:
        st.error(f"Erreur API : {response.status_code} pour location {location_id}")
        return pd.DataFrame()

#=============================================================================================================
def get_full_history(location_id: int, token: str, days: int = 100) -> pd.DataFrame:
    """
    Récupère toutes les données d'une location_id sur 'days' jours,
    en faisant des requêtes API par tranches de 10 jours.
    """
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
        to_date = from_date  # on recule la fenêtre

    if all_data:
        df_full = pd.concat(all_data, ignore_index=True).drop_duplicates()
        file_path = os.path.join(DATA_DIR, f"full-data-{days}-jours-{location_id}.csv")
        df_full.to_csv(file_path, index=False)
        return df_full
    else:
        return pd.DataFrame()

#=============================================================================================================
def calculer_iqa_journalier(df: pd.DataFrame, location_id: int) -> pd.DataFrame:
    """
    Calcule l’IQA journalier pour un DataFrame complet.
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
    file_path = os.path.join(DATA_DIR, f"iqa-{location_id}.csv")
    iqa_tab.to_csv(file_path, index=False)
    return iqa_tab

#=============================================================================================================
def pipeline_iqa(location_ids: list, token: str, days: int = 100) -> dict:
    """
    Exécute la récupération et le calcul IQA pour plusieurs location_ids.
    Retourne un dictionnaire {location_id: DataFrame IQA}.
    """
    resultats = {}
    for loc_id in location_ids:
        st.info(f" Récupération des données pour Location {loc_id}")
        df_full = get_full_history(loc_id, token, days)
        df_iqa = calculer_iqa_journalier(df_full, loc_id)
        resultats[loc_id] = df_iqa
    return resultats

#=============================================================================================================


class RespireReportGenerator:
    def __init__(self, location_id: str, token: str):
        self.location_id = location_id
        self.token = token
        self.report_date = datetime.now()
        
    def fetch_current_data(self, _location_id: str, _token: str) -> Dict:
        """Récupère les données actuelles de qualité de l'air"""
        endpoint = f"/locations/{_location_id}/measures/current"
        params = {"token": _token}
        full_url = f"{BASE_URL}{endpoint}?{urlencode(params)}"


        headers = {"Authorization": f"Bearer {_token}"}
        

        
        try:
            #response = requests.get(full_url)
            response = requests.get(full_url, params=params, headers=headers, timeout=15)
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
                return {}
            
            result = {}
            for key in VALEURS_LIMITE.keys():
                if key in df.columns:
                    result[key] = df[key].iloc[0] if not df[key].empty else 0
                else:
                    result[key] = 0
            
            result["last_update"] = datetime.now().strftime("%H:%M")
            return result
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {e}")
            return {}

    def calculer_iqa_global(self, data: Dict) -> Tuple[float, str, str, str]:
        """Calcule l'IQA global avec couleur associée"""
        iqa_values = {}
        
        for pollutant, limite in VALEURS_LIMITE.items():
            if pollutant in data and data[pollutant] is not None:
                # ⚠️ on exclut humidité et température
                if pollutant not in ["rhum_corrected", "atmp_corrected"]:
                    concentration = data[pollutant]
                    iqa_values[pollutant] = (concentration / limite) * 100
        
        if not iqa_values:
            return 0, "Aucun", "Données indisponibles", COLORS['secondary']
        
        polluant_principal = max(iqa_values, key=iqa_values.get)
        iqa_principal = iqa_values[polluant_principal]
        
        # Détermination du statut et couleur
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


    def creer_logo_respire(self) -> str:
        """Crée un logo simple pour RESPIRE"""
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5)
        
        # Fond dégradé
        gradient = np.linspace(0, 1, 256).reshape(1, -1)
        ax.imshow(gradient, extent=[0, 10, 0, 5], aspect='auto', cmap='Blues', alpha=0.3)
        
        # Texte RESPIRE stylisé
        ax.text(5, 2.5, 'RESPIRE', fontsize=24, fontweight='bold', 
                ha='center', va='center', color=COLORS['primary'])
        ax.text(5, 1.5, 'Programme de Surveillance', fontsize=10, 
                ha='center', va='center', color=COLORS['secondary'])
        ax.text(5, 1, 'Qualite de l\'Air Scolaire', fontsize=10, 
                ha='center', va='center', color=COLORS['secondary'])
        
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.savefig(tmpfile.name, format="png", dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            return tmpfile.name

    def creer_gauge_iqa(self, iqa_value: float, color: str) -> str:
        """Crée une jauge circulaire pour l'IQA"""
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
        
        # Configuration de la jauge
        theta = np.linspace(0, np.pi, 100)
        r = np.ones_like(theta)
        
        # Zones de couleur
        zones = [(0, 50, COLORS['bon']), (50, 100, COLORS['modere']), 
                (100, 150, COLORS['mauvais']), (150, 200, COLORS['critique'])]
        
        for start, end, zone_color in zones:
            mask = (theta >= start/200 * np.pi) & (theta <= end/200 * np.pi)
            ax.fill_between(theta[mask], 0.8, 1.0, color=zone_color, alpha=0.7)
        
        # Aiguille de l'IQA
        angle = iqa_value / 200 * np.pi
        ax.arrow(angle, 0, 0, 0.7, head_width=0.05, head_length=0.05, 
                fc=color, ec=color, linewidth=3)
        
        # Point central
        ax.scatter(0, 0, c=color, s=200, zorder=5)
        
        # Configuration de l'affichage
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('S')
        ax.set_theta_direction(1)
        # ...dans creer_gauge_iqa...
        ax.set_thetagrids(np.linspace(0, 180, 7), ['200', '167', '133', '100', '67', '33', '0'])
# ...le reste inchangé...
        ax.set_rticks([])
        ax.grid(True, alpha=0.3)
        
        # Titre et valeur
        ax.text(np.pi/2, -0.3, f'IQA: {iqa_value:.1f}', fontsize=20, fontweight='bold', 
               ha='center', va='center', transform=ax.transData)
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.savefig(tmpfile.name, format="png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            return tmpfile.name

    def creer_dashboard_polluants(self, data: Dict) -> str:
        """Crée un dashboard avec tous les polluants"""
        fig, axes = plt.subplots(2, 4, figsize=(16, 10))
        fig.suptitle('TABLEAU DE BORD - QUALITE DE L\'AIR EN TEMPS REEL', 
                    fontsize=18, fontweight='bold', y=0.95)
        
        polluants = ['pm02_corrected', 'pm10_corrected', 'pm01_corrected', 'rco2_corrected',
                    'tvoc', 'noxIndex', 'atmp_corrected', 'rhum_corrected']
        
        for i, polluant in enumerate(polluants):
            row = i // 4
            col = i % 4
            ax = axes[row, col]
            
            if polluant in data:
                valeur = data[polluant]
                seuil = VALEURS_LIMITE.get(polluant, 100)
                nom = POLLUANTS_NOMS.get(polluant, polluant)
                
                # Jauge horizontale
                ratio = min(valeur / seuil, 2.0)  # Cap à 200%
                
                # Couleur selon le niveau
                if ratio <= 0.5:
                    color = COLORS['bon']
                elif ratio <= 1.0:
                    color = COLORS['modere']
                else:
                    color = COLORS['mauvais']
                
                # Barre de progression
                ax.barh([0], [ratio], color=color, alpha=0.8, height=0.5)
                ax.axvline(x=1, color='red', linestyle='--', alpha=0.7, linewidth=2)
                
                # Texte
                ax.text(0.5, 0.7, nom, fontsize=12, fontweight='bold', ha='center')
                ax.text(0.5, 0.3, f'{valeur:.1f}', fontsize=14, fontweight='bold', ha='center')
                ax.text(0.5, -0.1, f'Seuil: {seuil}', fontsize=8, ha='center', alpha=0.7)
                
                ax.set_xlim(0, 2)
                ax.set_ylim(-0.3, 1)
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Bordure colorée
                for spine in ax.spines.values():
                    spine.set_color(color)
                    spine.set_linewidth(2)
            else:
                ax.text(0.5, 0.5, 'Données\nindisponibles', ha='center', va='center')
                ax.set_xticks([])
                ax.set_yticks([])
        
        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.savefig(tmpfile.name, format="png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            return tmpfile.name


    def creer_evolution_temporelle(self, location_id: str, token: str) -> str:
        """Crée un graphique d'évolution temporelle avec données réelles"""
        df = get_full_history(location_id, token, days=7)
        df_iqa = calculer_iqa_journalier(df, int(location_id))
        
        if df_iqa.empty:
            return ""
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df_iqa['date'], df_iqa['iqa'], marker='o', linewidth=2, color=COLORS['primary'])
        ax.fill_between(df_iqa['date'], df_iqa['iqa'], alpha=0.3, color=COLORS['accent'])
        
        ax.set_title("EVOLUTION IQA - 7 DERNIERS JOURS", fontsize=16, fontweight='bold')
        ax.set_ylabel("Indice de Qualité de l'Air (IQA)")
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.xticks(rotation=45)
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.savefig(tmpfile.name, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return tmpfile.name



class ProfessionalPDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        # Fond d'en-tête coloré
        self.set_fill_color(44, 62, 80)  # Bleu foncé
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_text_color(255, 255, 255)  # Blanc
        self.set_font('Arial', 'B', 18)
        self.cell(0, 15, 'RAPPORT QUALITE DE L\'AIR - PROGRAMME RESPIRE', 0, 1, 'C')
        
        # Ligne de séparation
        self.set_draw_color(52, 152, 219)  # Bleu
        self.set_line_width(1)
        self.line(10, 32, 200, 32)
        
        self.ln(15)
        
    def footer(self):
        self.set_y(-20)
        # Ligne de séparation
        self.set_draw_color(52, 152, 219)
        self.line(10, self.get_y()-5, 200, self.get_y()-5)
        
        self.set_text_color(128, 128, 128)
        self.set_font('Arial', 'I', 9)
        self.cell(0, 10, f'Page {self.page_no()} - Genere le {datetime.now().strftime("%d/%m/%Y a %H:%M")} - Programme RESPIRE', 0, 0, 'C')
    
    def section_header(self, title: str, color_r=44, color_g=62, color_b=80):
        """En-tête de section avec fond coloré"""
        self.ln(10)
        self.set_fill_color(color_r, color_g, color_b)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, title, 0, 1, 'L', 1)
        self.ln(5)
        
    def info_box(self, title: str, value: str, status_color='green'):
        """Boîte d'information colorée"""
        # Couleurs selon le statut
        colors = {
            'green': (39, 174, 96),
            'orange': (243, 156, 18),
            'red': (231, 76, 60),
            'blue': (52, 152, 219)
        }
        
        color = colors.get(status_color, colors['blue'])
        
        # Bordure colorée
        self.set_draw_color(*color)
        self.set_line_width(0.5)
        self.rect(self.get_x(), self.get_y(), 90, 20)
        
        # Fond légèrement coloré
        self.set_fill_color(color[0], color[1], color[2])
        self.rect(self.get_x(), self.get_y(), 90, 20, 'F')
        self.set_fill_color(255, 255, 255)
        self.rect(self.get_x()+1, self.get_y()+1, 88, 18, 'F')
        
        # Texte
        self.set_text_color(*color)
        self.set_font('Arial', 'B', 10)
        self.cell(90, 10, title, 0, 1, 'C')
        self.set_font('Arial', 'B', 14)
        self.cell(90, 10, value, 0, 1, 'C')
        
        self.set_text_color(0, 0, 0)  # Reset couleur
        
    def add_styled_text(self, text: str, style='', size=11, color=(0,0,0)):
        """Ajoute du texte stylisé"""
        self.set_text_color(*color)
        self.set_font('Arial', style, size)
        self.multi_cell(0, 8, self.clean_text(text))
        self.ln(3)
        self.set_text_color(0, 0, 0)  # Reset
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte des caractères non supportés"""
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'á': 'a', 'â': 'a', 'ä': 'a',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ï': 'i', 'î': 'i', 'í': 'i', 'ì': 'i',
            'ô': 'o', 'ó': 'o', 'ò': 'o', 'ö': 'o',
            'ç': 'c', 'ñ': 'n', '₂': '2', '°': ' deg'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return ''.join(char if ord(char) < 128 else '?' for char in text)

def generate_professional_report(location_id: str, token: str) -> str:
    """Génère un rapport PDF professionnel et visuellement attractif"""
    
    generator = RespireReportGenerator(location_id, token)
    
    # 1. Récupération des données
    current_data = generator.fetch_current_data(location_id, token)
    if not current_data:
        raise Exception("Impossible de récupérer les données")
    
    iqa_value, polluant_principal, status, status_color = generator.calculer_iqa_global(current_data)
    
    # 2. Création des visuels
    logo_path = generator.creer_logo_respire()
    gauge_path = generator.creer_gauge_iqa(iqa_value, status_color)
    dashboard_path = generator.creer_dashboard_polluants(current_data)
    evolution_path = generator.creer_evolution_temporelle(location_id, token)

    
    # 3. Génération du PDF professionnel
    pdf = ProfessionalPDFReport()
    pdf.add_page()
    
    # LOGO ET INFORMATIONS GÉNÉRALES
    pdf.image(logo_path, x=10, y=50, w=60)
    
    # Informations dans des boîtes colorées à droite du logo
    pdf.set_xy(80, 60)
    pdf.info_box("ETABLISSEMENT", f"Ecole ID: {location_id}", 'blue')
    
    pdf.set_xy(80, 85)
    date_str = datetime.now().strftime("%d/%m/%Y")
    pdf.info_box("DATE RAPPORT", date_str, 'blue')
    
    # RÉSUMÉ EXÉCUTIF avec jauge IQA
    pdf.ln(20)
    pdf.section_header("RESUME EXECUTIF", 52, 152, 219)


    # TABLEAU DES POLLUANTS
    pdf.ln(10)
    pdf.section_header("DETAIL DES POLLUANTS", 52, 73, 94)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 10, "Polluant", 1, 0, 'C')
    pdf.cell(40, 10, "Valeur", 1, 0, 'C')
    pdf.cell(40, 10, "Seuil OMS", 1, 0, 'C')
    pdf.cell(60, 10, "Statut", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    for polluant, limite in VALEURS_LIMITE.items():
        if polluant in current_data and polluant not in ["rhum_corrected", "atmp_corrected"]:
            val = current_data[polluant]
            ratio = (val / limite) * 100
            if ratio <= 50:
                statut = "Bon"
            elif ratio <= 100:
                statut = "Modéré"
            else:
                statut = "Mauvais"
            
            pdf.cell(40, 10, POLLUANTS_NOMS.get(polluant, polluant), 1, 0, 'C')
            pdf.cell(40, 10, f"{val:.1f}", 1, 0, 'C')
            pdf.cell(40, 10, f"{limite}", 1, 0, 'C')
            pdf.cell(60, 10, statut, 1, 1, 'C')

    
    # Jauge IQA
    pdf.image(gauge_path, x=20, y=pdf.get_y(), w=80)
    
    # Informations à côté de la jauge
    pdf.set_xy(110, pdf.get_y() + 10)
    
    # Couleur selon le statut
    status_colors = {
        'EXCELLENT': 'green',
        'BON': 'green',
        'MODERE': 'orange',
        'MAUVAIS': 'red',
        'CRITIQUE': 'red'
    }
    color = status_colors.get(status, 'blue')
    
    pdf.info_box("STATUT GLOBAL", status, color)
    
    pdf.set_xy(110, pdf.get_y() + 10)
    pdf.info_box("POLLUANT PRINCIPAL", polluant_principal, 'orange')
    
    pdf.ln(60)
    
    # DASHBOARD POLLUANTS
    pdf.section_header("SURVEILLANCE EN TEMPS REEL", 243, 156, 18)
    pdf.image(dashboard_path, x=10, y=pdf.get_y(), w=190)
    pdf.ln(85)
    
    # NOUVELLE PAGE - EVOLUTION TEMPORELLE
    pdf.add_page()
    pdf.section_header("EVOLUTION TEMPORELLE", 39, 174, 96)
    pdf.image(evolution_path, x=10, y=pdf.get_y(), w=190)
    pdf.ln(70)
    
    # RECOMMANDATIONS avec code couleur
    pdf.section_header("RECOMMANDATIONS", 231, 76, 60)
    
    if iqa_value <= 75:
        pdf.add_styled_text("SITUATION FAVORABLE", 'B', 12, (39, 174, 96))
        pdf.add_styled_text("- Maintenir la surveillance reguliere")
        pdf.add_styled_text("- Activites exterieures normales")
        pdf.add_styled_text("- Sensibilisation continue des eleves")
    elif iqa_value <= 100:
        pdf.add_styled_text("SURVEILLANCE RENFORCEE", 'B', 12, (243, 156, 18))
        pdf.add_styled_text("- Surveiller l'evolution quotidienne")
        pdf.add_styled_text("- Limiter les activites sportives intenses")
        pdf.add_styled_text("- Ameliorer la ventilation des classes")
    else:
        pdf.add_styled_text("MESURES D'URGENCE", 'B', 12, (231, 76, 60))
        pdf.add_styled_text("- SUSPENDRE les activites exterieures")
        pdf.add_styled_text("- ALERTER immediatement les familles")
        pdf.add_styled_text("- ACTIVER le plan d'urgence")
    
    # FOOTER INFORMATIF
    pdf.ln(20)
    pdf.section_header("INFORMATIONS TECHNIQUES", 128, 128, 128)
    pdf.add_styled_text("Capteurs: AirGradient - Norme: OMS 2021", '', 9, (128, 128, 128))
    pdf.add_styled_text("Frequence: Mesures continues 24h/7j", '', 9, (128, 128, 128))
    
    # Sauvegarde
    output_path = f"rapport_professionnel_{location_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(output_path)
    
    # Nettoyage
    for path in [logo_path, gauge_path, dashboard_path, evolution_path]:
        try:
            os.unlink(path)
        except:
            pass
    
    return output_path

def test_professional_report():
    """Test de génération du rapport professionnel"""
    try:
        pdf_path = generate_professional_report(location_id, token)
        assert os.path.exists(pdf_path)
        print(f"RAPPORT PROFESSIONNEL genere avec succes: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Erreur lors de la generation: {e}")
        return None





if __name__ == "__main__":
    test_professional_report()
