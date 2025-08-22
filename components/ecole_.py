import streamlit as st
from components.calculer_iqa import calculer_iqa
import pandas as pd
import os
from urllib.parse import urlencode
import requests
from datetime import datetime
import random
from config.settings import token,BASE_URL,VALEURS_LIMITE,location_ids,DATA_DIR
from src.functions import fetch_current_data,calculer_iqa
import streamlit.components.v1 as components
import time


#=============================================================================================================


#=============================================================================================================
def show_daily_tips(location_id, token):
    """
    Affiche des recommandations basées sur la qualité de l'air actuelle
    """
    # En-tête simple et professionnel
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #0066cc;
    ">
        <h2 style="
            color: #2c3e50;
            font-size: 1.5rem;
            margin: 0;
            font-weight: 600;
        ">Recommandations quotidiennes</h2>
        <p style="
            color: #6c757d;
            margin: 0.5rem 0 0 0;
            font-size: 0.95rem;
        ">Conseils adaptés à la qualité de l'air actuelle</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupérer l'IQA actuel
    df = fetch_current_data(location_id, token)
    df = pd.DataFrame([df])
    iqa = calculer_iqa(df)
    
    if not iqa:
        st.error("Impossible de récupérer les données de qualité de l'air")
        return
    
    # Configuration des conseils par niveau d'IQA
    conseils_config = {
        (0, 50): {
            "conseils": [
                {"icon": "🏃", "titre": "Activités extérieures", "desc": "Conditions idéales pour les activités de plein air"},
                {"icon": "🌱", "titre": "Aération", "desc": "Aérez largement les espaces intérieurs"},
                {"icon": "🚴", "titre": "Sport en extérieur", "desc": "Profitez-en pour faire du sport dehors"}
            ],
            "couleur": "#28a745",
            "bg_color": "#d4edda",
            "niveau": "Excellent",
            "icon_niveau": "✅"
        },
        (51, 100): {
            "conseils": [
                {"icon": "🚶", "titre": "Marche privilégiée", "desc": "Favorisez la marche pour vos déplacements"},
                {"icon": "💧", "titre": "Hydratation", "desc": "Maintenez une bonne hydratation"},
                {"icon": "🪟", "titre": "Ventilation régulière", "desc": "Aérez régulièrement les locaux"}
            ],
            "couleur": "#6c757d",
            "bg_color": "#f8f9fa",
            "niveau": "Bon",
            "icon_niveau": "✓"
        },
        (101, 150): {
            "conseils": [
                {"icon": "⚠️", "titre": "Activités modérées", "desc": "Limitez les efforts physiques intenses"},
                {"icon": "🏠", "titre": "Intérieur privilégié", "desc": "Privilégiez les activités en intérieur"},
                {"icon": "⏰", "titre": "Aération courte", "desc": "Aérez par courtes périodes"}
            ],
            "couleur": "#fd7e14",
            "bg_color": "#fff3cd",
            "niveau": "Modéré",
            "icon_niveau": "⚡"
        },
        (151, 200): {
            "conseils": [
                {"icon": "😷", "titre": "Protection respiratoire", "desc": "Port du masque recommandé à l'extérieur"},
                {"icon": "📚", "titre": "Activités calmes", "desc": "Privilégiez les activités peu intenses"},
                {"icon": "🚫", "titre": "Éviter l'extérieur", "desc": "Limitez le temps passé à l'extérieur"}
            ],
            "couleur": "#dc3545",
            "bg_color": "#f8d7da",
            "niveau": "Mauvais",
            "icon_niveau": "⚠️"
        },
        (201, 300): {
            "conseils": [
                {"icon": "🏠", "titre": "Confinement", "desc": "Restez à l'intérieur autant que possible"},
                {"icon": "🧴", "titre": "Hygiène renforcée", "desc": "Lavez-vous fréquemment les mains"},
                {"icon": "📞", "titre": "Surveillance santé", "desc": "Consultez si symptômes respiratoires"}
            ],
            "couleur": "#6f42c1",
            "bg_color": "#e2e3f0",
            "niveau": "Très mauvais",
            "icon_niveau": "🚨"
        }
    }
    
    # Déterminer la configuration selon l'IQA
    config = None
    for (min_val, max_val), conf in conseils_config.items():
        if min_val <= iqa <= max_val:
            config = conf
            break
    
    if not config:
        st.error("Valeur d'IQA hors limites")
        return
    
    # Affichage du niveau de qualité
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 1rem;
        margin: 1rem 0;
        background-color: {config['bg_color']};
        border-radius: 8px;
        border: 1px solid {config['couleur']};
    ">
        <span style="font-size: 1.5rem;">{config['icon_niveau']}</span>
        <strong style="color: {config['couleur']}; margin-left: 0.5rem;">
            Qualité de l'air : {config['niveau']} (IQA: {iqa})
        </strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage des conseils
    cols = st.columns(len(config['conseils']))
    
    for i, conseil in enumerate(config['conseils']):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background-color: white;
                border: 1px solid {config['couleur']};
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
                height: 180px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 1rem;">{conseil["icon"]}</div>
                <h4 style="
                    color: {config['couleur']}; 
                    margin: 0.5rem 0; 
                    font-size: 1rem;
                    font-weight: 600;
                ">{conseil["titre"]}</h4>
                <p style="
                    color: #6c757d; 
                    font-size: 0.85rem; 
                    line-height: 1.4;
                    margin: 0;
                ">{conseil["desc"]}</p>
            </div>
            """, unsafe_allow_html=True)
#=============================================================================================================
#=============================================================================================================
def show_header(nom_ecole: str = None, logo_path: str = None):
    """
    Affiche un en-tête simple et élégant pour la page École.
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
                    Bienvenue dans ton espace Respire
                </div>
                <div class="subtitle">
                    Découvre comment va l'air de ton école aujourd'hui !
                </div>
                {school_name_html}
            </div>
            {logo_html}
        </div>
        ''', unsafe_allow_html=True)
#============================================================================================================

#============================================================================================================

def section_en_savoir_plus_air(liens):
    """
    Crée une section 'En savoir plus sur l'air' avec un carrousel de vidéos
    
    Args:
        liens (dict): Dictionnaire contenant les liens et noms des vidéos
                     Format: {"1":{"lien":"url","nom":"nom"}, ...}
    """
    
    def extract_youtube_id(url):
        """Extrait l'ID YouTube d'une URL"""
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        elif 'youtube.com' in url:
            return url.split('v=')[1].split('&')[0]
        return None
    
    # CSS pour le carrousel
    st.markdown("""
    <style>
    .air-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        margin: 30px 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    
    .air-title {
        color: white;
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    
    .video-card {
        flex: 0 0 400px;
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    .video-title {
        color: #333;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .video-frame {
        width: 100%;
        height: 405px;
        border-radius: 10px;
        border: none;
    }
    
    .carousel-controls {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
    }
    
    .control-btn {
        background: rgba(255,255,255,0.2);
        border: 2px solid white;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .control-btn:hover {
        background: white;
        color: #667eea;
    }
    
    
    .video-carousel::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }
    
    .video-carousel::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.3);
        border-radius: 4px;
    }
    
    .video-carousel::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.5);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Conteneur principal
   
    st.markdown('<h2 class="air-title"> En savoir plus sur l\'air</h2>', unsafe_allow_html=True)
    
    
    # Navigation avec boutons précédent/suivant
    if 'current_video_index' not in st.session_state:
        st.session_state.current_video_index = 0
    
    videos_list = list(liens.items())
    current_index = st.session_state.current_video_index
    
    # Contrôles de navigation
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col2:
        if st.button("⬅️ Précédent", key="prev_video"):
            if current_index > 0:
                st.session_state.current_video_index -= 1
                st.rerun()
    
    with col3:
        st.markdown(f'''
        <p style="color: white; text-align: center; font-weight: bold;">
        Vidéo {current_index + 1} sur {len(videos_list)}
        </p>
        ''', unsafe_allow_html=True)
    
    with col4:
        if st.button("Suivant ➡️", key="next_video"):
            if current_index < len(videos_list) - 1:
                st.session_state.current_video_index += 1
                st.rerun()
    
    # Affichage de la vidéo courante
    if videos_list:
        key, video_info = videos_list[current_index]
        video_id = extract_youtube_id(video_info["lien"])
        
        if video_id:
            st.markdown(f'''
            <div style="display: flex; justify-content: center;">
                <div class="video-card" style="flex: 0 0 900px;">
                    <div class="video-title">{video_info["nom"]}</div>
                    <iframe class="video-frame" 
                            src="https://www.youtube.com/embed/{video_id}"
                            frameborder="0" 
                            allowfullscreen>
                    </iframe>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    
    st.markdown('</div>', unsafe_allow_html=True)


#=============================================================================================================
 
#=============================================================================================================
def show_air_quality(location_id, token):
    st.markdown("## Comment va l'air de notre école ?")
    
    df = fetch_current_data(location_id, token)
    df = pd.DataFrame([df])
    iqa = calculer_iqa(df)
    
    if not iqa:
        st.error("Impossible de calculer l'IQA.")
        return
    
    # Détermination du niveau avec emojis adaptés et nouveaux seuils AQI
    if iqa <= 50:
        niveau = "Excellente"
        emoji = "😊"
        message = "Super ! L'air est pur, tu peux profiter de l'extérieur sans souci !"
        couleur_bg = "#e8f5e8"
        couleur_border = "#4caf50"
    elif iqa <= 100:
        niveau = "Bonne"
        emoji = "🙂"
        message = "L'air est acceptable. Un peu d'aération ne ferait pas de mal !"
        couleur_bg = "#f1f8e9"
        couleur_border = "#8bc34a"
    elif iqa <= 150:
        niveau = "Moyenne"
        emoji = "😐"
        message = "L'air est moyen. Évite les efforts intenses à l'extérieur."
        couleur_bg = "#fff8e1"
        couleur_border = "#ffb300"
    elif iqa <= 200:
        niveau = "Mauvaise"
        emoji = "😷"
        message = "L'air est pollué. Reste à l'intérieur et ferme les fenêtres."
        couleur_bg = "#ffebee"
        couleur_border = "#e53935"
    else:
        niveau = "Très mauvaise"
        emoji = "😨"
        message = "Attention ! L'air est très pollué. Aucune activité en extérieur recommandée."
        couleur_bg = "#fce4ec"
        couleur_border = "#8e24aa"
    
    # Disposition en colonnes : bloc de qualité à gauche, explication à droite
    col1, col2 = st.columns([1, 1])
    
    # Colonne de gauche : Bloc de qualité de l'air
    with col1:
        st.markdown(
            f"""
            <div style='
                background: {couleur_bg};
                border: 3px solid {couleur_border};
                border-radius: 20px;
                padding: 30px;
                text-align: center;
                margin: 10px 0;
                height: 350px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            '>
                <div style='font-size: 80px; margin-bottom: 10px;'>{emoji}</div>
                <h1 style='color: {couleur_border}; font-size: 28px; margin: 10px 0;'>{niveau}</h1>
                <h3 style='color: #555; font-size: 18px; line-height: 1.4;'>{message}</h3>
                <p style='color: #777; margin-top: 15px; font-size: 14px;'>
                    IQA : <strong>{int(iqa)}</strong><br>
                    Dernière mesure : {datetime.now().strftime("%H:%M")}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Colonne de droite : Explication de l'IQA pour les élèves
    with col2:
        # Utilisation de st.components.v1.html pour un rendu HTML propre
        import streamlit.components.v1 as components
        
        components.html(f"""
        <div style='
            background: #f8f9ff;
            border: 2px solid  {couleur_border};
            border-radius: 15px;
            padding: 25px;
            font-family: "Source Sans Pro", sans-serif;
            height: 300px;
            overflow-y: auto;
        '>
            <h3 style='color: {couleur_border}; text-align: center; margin-bottom: 20px; margin-top: 0;'>
                 C'est quoi l'IQA ?
            </h3>
            
            <p style='margin: 10px 0; color: #333;'>
                <strong>IQA</strong> = <strong>I</strong>ndice de <strong>Q</strong>ualité de l'<strong>A</strong>ir
            </p>
            
            <p style='margin: 15px 0; color: #333; line-height: 1.5;'>
                C'est comme un thermomètre pour l'air ! Il nous dit si l'air qu'on respire est bon ou pas.
            </p>
            
            <p style='margin: 15px 0; color: #333; font-weight: bold;'> L'échelle de l'air :</p>
            
            <div style='margin: 15px 0;'>
                <div style='display: flex; align-items: center; margin: 8px 0;'>
                    <span style='font-size: 20px; margin-right: 10px;'>😊</span>
                    <span style='color: #333;'><strong>0-50 :</strong> Air excellent</span>
                </div>
                <div style='display: flex; align-items: center; margin: 8px 0;'>
                    <span style='font-size: 20px; margin-right: 10px;'>🙂</span>
                    <span style='color: #333;'><strong>51-100 :</strong> Air bon</span>
                </div>
                <div style='display: flex; align-items: center; margin: 8px 0;'>
                    <span style='font-size: 20px; margin-right: 10px;'>😐</span>
                    <span style='color: #333;'><strong>101-150 :</strong> Air moyen</span>
                </div>
                <div style='display: flex; align-items: center; margin: 8px 0;'>
                    <span style='font-size: 20px; margin-right: 10px;'>😷</span>
                    <span style='color: #333;'><strong>151-200 :</strong> Air mauvais</span>
                </div>
                <div style='display: flex; align-items: center; margin: 8px 0;'>
                    <span style='font-size: 20px; margin-right: 10px;'>😨</span>
                    <span style='color: #333;'><strong>200+ :</strong> Air très mauvais</span>
                </div>
            </div>
            
            <div style='
                background: #e3f2fd; 
                padding: 12px; 
                border-radius: 8px; 
                margin-top: 15px;
                border-left: 4px solid #2196f3;
            '>
                <p style='margin: 0; color: #333; font-size: 14px;'>
                    💡 <strong>Le savais-tu ?</strong> L'IQA mesure les particules invisibles dans l'air qui peuvent nous faire tousser ou nous rendre malades.
                </p>
            </div>
        </div>
        """, height=400)
    

#==============================================================================================================


def show_animation(video_url: str = None):
    """
    Affiche le bloc de sensibilisation avec une vidéo ou, à défaut, une image et un texte explicatif.
    :param video_url: URL de la vidéo YouTube ou intégrée. Si None, affiche une alternative statique.
    """
    
    # En-tête attractif avec animation
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        "></div>
        <h1 style="
            color: white;
            font-size: 2.3rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        ">🎬 Tu veux savoir comment l'air devient pollué ?</h1>
        <p style="
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
            position: relative;
            z-index: 1;
        ">Découvre les secrets invisibles de notre atmosphère !</p>
    </div>
    
    <style>
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.3; }
            50% { transform: scale(1.1); opacity: 0.1; }
        }
    </style>
    """, unsafe_allow_html=True)
    


    if video_url:
        
        col1, col2, col3 = st.columns([1, 7, 1])
        
        with col2:
            import re
    
            def extract_youtube_id(url: str) -> str | None:
                # gère https://youtu.be/ID, https://www.youtube.com/watch?v=ID, & t=, etc.
                m = re.search(r"(?:youtu\.be/|v=)([A-Za-z0-9_-]{6,})", url)
                return m.group(1) if m else None
    
            def default_youtube_thumb(vid: str) -> str:
                # essaie maxres, sinon hq
                return f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg"
    
            def get_video_html(url: str, poster: str | None = None) -> str:
                yt_id = extract_youtube_id(url)
    
                # ---- YOUTUBE : iframe (le poster est géré par YouTube, mais on peut afficher une image cliquable si besoin) ----
                if yt_id:
                    # si pas de thumbnail fourni, on prend celui de YouTube
                    poster_final = poster or default_youtube_thumb(yt_id)
                    # miniature cliquable -> remplace par iframe au clic (lazy)
                    return f"""
                    <div style="background: white; padding: 16px; border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 2px solid #667eea;">
                      <div id="yt-wrapper" style="position:relative; width:100%; padding-top:56.25%; border-radius:12px; overflow:hidden; background:#000;">
                        <img id="yt-poster" src="{poster_final}" alt="thumbnail" 
                             style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; cursor:pointer;">
                        <div onclick="var p=document.getElementById('yt-player'); p.innerHTML='<iframe src=\\'https://www.youtube.com/embed/{yt_id}?autoplay=1\\' frameborder=\\'0\\' allow=\\'autoplay; encrypted-media\\' allowfullscreen style=\\'position:absolute;top:0;left:0;width:100%;height:100%\\'></iframe>'; this.parentElement.querySelector('#yt-poster').style.display='none'; this.style.display='none';" 
                             style="position:absolute; top:0; left:0; width:100%; height:100%; display:flex; align-items:center; justify-content:center; cursor:pointer;">
                          <div style="width:78px; height:78px; border-radius:50%; background:rgba(0,0,0,0.55); display:flex; align-items:center; justify-content:center;">
                            <svg viewBox="0 0 68 48" width="48"><path d="M66.52 7.58a8 8 0 0 0-5.64-5.66C55.55 0 34 0 34 0S12.45 0 7.12 1.92a8 8 0 0 0-5.64 5.66A83.1 83.1 0 0 0 0 24a83.1 83.1 0 0 0 1.48 16.42 8 8 0 0 0 5.64 5.66C12.45 48 34 48 34 48s21.55 0 26.88-1.92a8 8 0 0 0 5.64-5.66A83.1 83.1 0 0 0 68 24a83.1 83.1 0 0 0-1.48-16.42z" fill="#f00"/><path d="M45 24 27 14v20" fill="#fff"/></svg>
                          </div>
                        </div>
                        <div id="yt-player" style="position:absolute; top:0; left:0; width:100%; height:100%;"></div>
                      </div>
                    </div>
                    """
    
                # ---- FICHIER DIRECT (mp4/webm) : on utilise <video> avec poster ----
                poster_attr = f' poster="{poster}"' if poster else ""
                return f"""
                <div style="background: white; padding: 16px; border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 2px solid #667eea;">
                    <video width="100%" height="auto" controls playsinline preload="metadata"{poster_attr} style="border-radius:10px;">
                    <source src="{url}" type="video/mp4">
                    Votre navigateur ne supporte pas la lecture de cette vidéo.
                    </video>
                </div>
                """

            # on passe thumbnail_url si présent (sinon None)
            st.markdown(get_video_html(video_url,None), unsafe_allow_html=True)
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

       
       
    
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            components.html("""
            <div style='
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                font-family: "Source Sans Pro", sans-serif;
                box-shadow: 0 8px 25px rgba(255, 154, 158, 0.3);
                cursor: pointer;
                transition: transform 0.3s ease;
            ' onmouseover="this.style.transform='translateY(-5px)'"
               onmouseout="this.style.transform='translateY(0)'">
                <div style='font-size: 40px; margin-bottom: 10px;'>🤔</div>
                <h4 style='margin: 10px 0; font-size: 16px;'>As-tu appris quelque chose ?</h4>
                <p style='font-size: 12px; margin: 0; opacity: 0.9;'>La pollution est partout autour de nous !</p>
            </div>
            """, height=150)
        
        with col2:
            components.html("""
            <div style='
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                font-family: "Source Sans Pro", sans-serif;
                box-shadow: 0 8px 25px rgba(17, 153, 142, 0.3);
                cursor: pointer;
                transition: transform 0.3s ease;
            ' onmouseover="this.style.transform='translateY(-5px)'"
               onmouseout="this.style.transform='translateY(0)'">
                <div style='font-size: 40px; margin-bottom: 10px;'>💡</div>
                <h4 style='margin: 10px 0; font-size: 16px;'>Maintenant tu sais !</h4>
                <p style='font-size: 12px; margin: 0; opacity: 0.9;'>Tu peux agir pour protéger l'air !</p>
            </div>
            """, height=150)
        
        with col3:
            components.html("""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                font-family: "Source Sans Pro", sans-serif;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                cursor: pointer;
                transition: transform 0.3s ease;
            ' onmouseover="this.style.transform='translateY(-5px)'"
               onmouseout="this.style.transform='translateY(0)'">
                <div style='font-size: 40px; margin-bottom: 10px;'>🌟</div>
                <h4 style='margin: 10px 0; font-size: 16px;'>Partage tes idées !</h4>
                <p style='font-size: 12px; margin: 0; opacity: 0.9;'>Raconte à tes amis ce que tu as appris !</p>
            </div>
            """, height=150)
    
    
#=============================================================================================================






