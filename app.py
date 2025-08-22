import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from src.header import show_header_playful
from src.footer import show_footer
import folium
from streamlit_folium import st_folium
from src.functions import *
from config.settings import token,BASE_URL
from src.carte import *
from config.settings import token,BASE_URL,VALEURS_LIMITE,location_ids,DATA_DIR,liens,school_names,logo_paths,sender
from components.ecole_ import section_en_savoir_plus_air
from pathlib import Path
from components.autorite_ import show_header
import warnings
warnings.filterwarnings("ignore")
from streamlit_autorefresh import st_autorefresh
import json
from sms_system import SMSAlertSystem


# CSS pour cacher la barre Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Configuration générale de la page
st.set_page_config(page_title="RESPiRE – Accueil", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
            <style> 
                .st-emotion-cache-zy6yx3 {
                    width: 100%;
                    padding: 1rem 3rem 0rem;
                    margin-bottom : 0rem;
                    max-width: initial;
                    min-width: auto;
                    }
                section[data-testid="stSidebar"] {
                    background-color: #2E7D32;  /* vert  */
                    margin-bottom : 0;
                    padding-bottom : 0rem;
                    }
                .block-container {
                    padding-top: 1rem;
                    margin-bottom: 0;
                    }
            </style>
            
            """,unsafe_allow_html=True)


#=========================================== NOUVELLE SIDEBAR =====================================

# --------- CSS global ---------
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            background-color: #F9FAFB !important;
            border-right: 1px solid #E5E7EB !important;
        }
        .block-container { padding-top: 1rem; }
        /* Hover doux + barre active (menu unique) */
        #nav-all_menu .nav-link:hover {
            background-color: rgba(74, 222, 128, 0.08) !important;
            color: #047857 !important;
        }
        #nav-all_menu .nav-link.active { position: relative; }
        #nav-all_menu .nav-link.active::before {
            content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
            width: 4px; height: 20px; background: #4ade80; border-radius: 0 2px 2px 0;
        }
    </style>
""", unsafe_allow_html=True)

# --------- Styles option_menu ---------
donezo_styles = {
    "container": {"padding": "0", "background-color": "transparent"},
    "icon": {"color": "inherit", "font-size": "16px"},
    "nav-link": {
        "color": "#6B7280",
        "font-size": "14px",
        "text-align": "left",
        "margin": "2px 8px",
        "border-radius": "8px",
        "padding": "12px 16px",
        "font-weight": "500",
    },
    "nav-link-selected": {
        "background-color": "#F3F4F6",
        "color": "#4ade80",
        "border-radius": "8px",
        "padding": "12px 16px",
        "margin": "2px 8px",
        "font-weight": "600",
        "box-shadow": "0 2px 4px rgba(74, 222, 128, 0.12)"
    }
}


#===================================================================================================


# =============================== STATE ===============================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Accueil"

# =============================== SIDEBAR (MENU UNIQUE) ===============================
with st.sidebar:
    st.image("assets/images/logo_vert_.png", output_format="auto")

    # --- styles communs ---
    donezo_styles = {
        "container": {"padding": "0", "background-color": "transparent"},
        "icon": {"color": "inherit", "font-size": "16px"},
        "nav-link": {
            "color": "#6B7280",
            "font-size": "14px",
            "text-align": "left",
            "margin": "2px 8px",
            "border-radius": "8px",
            "padding": "12px 16px",
            "font-weight": "500",
        },
        "nav-link-selected": {
            "background-color": "#F3F4F6",
            "color": "#4ade80",
            "border-radius": "8px",
            "padding": "12px 16px",
            "margin": "2px 8px",
            "font-weight": "600",
            "box-shadow": "0 2px 4px rgba(74, 222, 128, 0.12)"
        }
    }

    # --- CSS : titres non cliquables + hover doux + barre active ---
    st.markdown("""
    <style>
      /* hover doux */
      #nav-all_menu .nav-link:hover { background-color: rgba(74,222,128,.08) !important; color:#047857 !important; }
      /* barre verte à gauche quand actif */
      #nav-all_menu .nav-link.active { position: relative; }
      #nav-all_menu .nav-link.active::before {
        content:''; position:absolute; left:0; top:50%; transform:translateY(-50%);
        width:4px; height:20px; background:#4ade80; border-radius:0 2px 2px 0;
      }
      /* Titres non cliquables (pseudo-éléments avant le 1er et le 6e item) */
      #nav-all_menu ul { margin:0; padding:0; }
      #nav-all_menu ul li:nth-child(1)::before,
      #nav-all_menu ul li:nth-child(6)::before {
        display:block; content:attr(data-section);
        text-transform:uppercase; letter-spacing:.05em; font-weight:600; font-size:12px;
        color:#9CA3AF; padding:16px 16px 8px 16px; margin:0;
      }
      /* on enlève le padding top du 1er item réel après chaque titre pour coller visuellement */
      #nav-all_menu ul li:nth-child(1) a, #nav-all_menu ul li:nth-child(6) a { margin-top:0 !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- Menu unique : 5 items "MENU" puis 3 items "GENERAL" (pas d'items factices) ---
    all_options = ["Accueil", "Eleves", "Parents", "Autorités", "Sensibilisations",
                   "Paramètres", "KaiKai", "À propos"]
    all_icons   = ["house-fill", "building", "people-fill", "shield-fill", "camera-video-fill",
                   "gear-fill", "layers", "info-circle-fill"]

    # default_index basé sur la page courante
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Accueil"
    default_index = all_options.index(st.session_state.current_page) \
                    if st.session_state.current_page in all_options else 0

    # rendu des <li> avec attributs data-section pour injecter "MENU" et "GENERAL"
    # astuce : on entoure l'option_menu par un conteneur pour pouvoir poser les data-section
    st.markdown('<div id="nav-all_menu">', unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=all_options,
        icons=all_icons,
        default_index=default_index,
        orientation="vertical",
        styles=donezo_styles,
        key="all_menu"  # id nécessaire pour cibler le menu en CSS
    )
    # ajoute les attributs data-section via JS léger (autorisé dans le markdown HTML)
    st.markdown("""
    <script>
      const ul = window.parent.document.querySelector('#nav-all_menu ul');
      if (ul) {
        const li = ul.querySelectorAll('li');
        if (li.length >= 8) {
          li[0].setAttribute('data-section','MENU');      // avant Accueil (1er item)
          li[5].setAttribute('data-section','GENERAL');   // avant Paramètres (6e item)
        }
      }
    </script>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # maj page courante
    if selected in all_options:
        st.session_state.current_page = selected

    # bloc message
    st.markdown(
        """
        <div style="
            background: rgba(255,255,255,0.6);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 8px;
            font-size: 12px;
            text-align: left;
            border: 1px solid #E5E7EB;
            color: #6B7280;
        ">
            <b>Respirer, c'est vivre.</b><br>
            Chaque souffle compte. <br>Agissons aujourd'hui pour un air plus pur demain.
        </div>
        """, unsafe_allow_html=True
    )

# =============================== ROUTING (reprend ta logique) ===============================
page = st.session_state.current_page

# ---------------------- SECTIONS FIXES POUR LA PAGE D'ACCUEIL -------------------------------

if page == "Accueil":
    
    #show_header_playful()
        
    # ---------------------- # ---------------------- Carte des capteurs   # ---------------------- # ---------------------- 
    # En-tête simple et efficace
    st.markdown("""
    <div style="
        background-color: #6c757d;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
    ">
        <h1 style="
            color: white;
            font-size: 1.8rem;
            margin: 0;
            font-weight: 600;
        ">🌍 Carte des capteurs installés dans les écoles au Sénégal</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Liste de capteurs avec coordonnées
    locations = pd.read_csv("locations_info.csv")
    
    # Déclenche un refresh automatique toutes les 60s
    # count = st_autorefresh(interval=60000, limit=100, key="fizzbuzzcounter")
    
    # Recuperation des donnees actuelles de toutes les locations 
    @st.cache_data(show_spinner=False, ttl=60)  # expire au bout de 1 min
    def get_all_locations_data(locations_df, token):
        results = {}
        for _, loc in locations_df.iterrows():
            results[loc["location_id"]] = fetch_current_data(str(loc["location_id"]), token)
        return results
    
    data_by_location = get_all_locations_data(locations, token)
    
    # Creer la variable qui contient le statut selon la location
    status = []
    for _, loc in locations.iterrows():
        data = data_by_location[loc["location_id"]]
        data = pd.DataFrame([data])
        status.append(get_aqi_status(calculer_iqa(pd.DataFrame(data))))
    locations["status"] = status
    
    # Carte centrée sur le Sénégal
    display_map_with_school_selector(locations, data_by_location)
    # section_en_savoir_plus_air(liens)             A remplacer par notre video de presentation du projet
    # ---------------------- # ---------------------- # ---------------------- # ---------------------- 
   
# --------------------- CONTENU PRINCIPAL -----------------------------------

# ---------------------- ACTIONS DES MENUS PRINCIPAUX -----------------------
        
elif page == "Eleves":
    from components import ecole
    ecole.show()

elif page == "Parents":
    from components import parent
    parent.show()

elif page == "Autorités":
    from components import autorite
    
    show_header()

    # Création d'une liste de tuples pour regrouper les infos
    ecoles = list(zip(location_ids, logo_paths, school_names))

    # CSS personnalisé pour styliser la selectbox
    st.markdown("""
    <style>
        /* Container principal */
        
        /* Stylisation de la selectbox Streamlit */
        .stSelectbox > div > div {
            background: white;
            border: 2px solid #a8e6cf;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            padding: 0.5rem;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #a8e6cf;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            transform: translateY(-2px);
        }
        
        /* Stylisation du texte de la selectbox */
        .stSelectbox > div > div > div {
            padding: 0.5rem;
            font-weight: 500;
        }
        
        
        /* Animation au focus */
        .stSelectbox > div > div:focus-within {
            border-color: #a8e6cf;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }
        
        /* Stylisation du dropdown menu */
        .stSelectbox ul {
            border-radius: 15px;
            border: 2px solid #e0e7ff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 0rem;
        }
        
        .stSelectbox li {
            padding: 0rem;
            transition: all 0.2s ease;
            border-bottom: 0.2px solid #f3f4f6;
        }
        
        .stSelectbox li:hover {
            background: linear-gradient(90deg, #f0f7ff, #e0e7ff);
            color: #667eea;
            font-weight: 600;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .school-selector {
                margin: 0.5rem;
                padding: 1.5rem;
                border-radius: 15px;
            }
            
            
        }
    </style>
    """, unsafe_allow_html=True)


    # Selectbox stylisée pour choisir l'école
    ecole_selectionnee = st.selectbox(
        "Sélectionnez une École",  # Label vide car on utilise le titre personnalisé
        options=ecoles,
        format_func=lambda e: f"📚 {e[2]}",  # Ajouter une icône devant le nom
        help="Choisissez l'établissement scolaire qui vous intéresse",
        key="school_selector"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Quand une école est choisie, exécuter ton code
    if ecole_selectionnee:
        
        location_id, logo_path, nom_ecole = ecole_selectionnee
        col1,col2 = st.columns([4,1])
        
        with col1:
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
                padding: 0.5rem;
                border-radius: 15px;
                margin-top: 0rem;
                margin-bottom: 0rem;
                margin-right: 0rem;
                color: white;
                text-align: center;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0; font-weight: 600;">
                    École sélectionnée : {}
                </h4>
            </div>
            """.format(ecole_selectionnee[2]), unsafe_allow_html=True)
        
        with col2:
            st.image(logo_path, width=100, use_container_width=False)        
        
        autorite.show(location_id, logo_path, nom_ecole)

    classify_by_iqa(location_ids, token,school_names)


elif page == "Sensibilisations":
    from components import sensibilisation
    sensibilisation.show_sensibilisation_page()

elif page == "Paramètres":
    from components import parametres
    parametres.parametre()

elif page == "KaiKai":
    from components.kaikai import render_kaikai_page
    render_kaikai_page()

elif page == "À propos":
    from components import apropos
    apropos.afficher_page_about()



def main():
    
    # Vérifier déclenchement automatique via URL
    query_params = st.query_params
    
    if "auto_trigger" in query_params:
        secret = query_params.get("secret", "")
        expected_secret = st.secrets.get("WEBHOOK_SECRET", "default_secret")
        
        if secret == expected_secret:
            with st.spinner("🔄 Envoi des alertes automatiques..."):
                sms_system = SMSAlertSystem()
                results, sent_count = sms_system.check_and_send_automatic_alerts(
                    "École Primaire Mamadou Calixte Dia"
                )
                
                st.success(f"✅ Alertes automatiques envoyées: {sent_count} SMS")
                st.json({
                    "timestamp": datetime.now().isoformat(),
                    "sent_count": sent_count,
                    "summary": f"{sent_count} parents contactés"
                })
                
                # Afficher les résultats détaillés
                if results:
                    st.subheader("📋 Détails des envois")
                    for result in results:
                        icon = "✅" if result['status'] == 'Envoyé' else "❌"
                        st.write(f"{icon} {result['parent']} ({result['child']}) - {result['reason']}")
                
                return  # Arrêter ici pour l'auto-trigger
    

main()





#=========================== SECTION TOUT EN BAS RESERVEE AU FOOTER =================================


# show_footer()
#Footer subtle
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid var(--neutral-200); color: var(--neutral-500); font-size: 0.875rem;">
    Breath4Life © 2024 • Pour un air plus sain dans nos écoles
</div>
""", unsafe_allow_html=True)











