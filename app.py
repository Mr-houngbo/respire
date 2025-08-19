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


# --------- SIDEBAR PERSONNALISÉE ---------
# CSS personnalisé pour la sidebar

st.markdown("""
            <style>
                /* Styling global de la sidebar */
                .css-1d391kg {
                    background: linear-gradient(180deg, #e8f5e8 0%, #c8e6c9 50%, #a5d6a7 100%) !important;
                    border-radius: 20px !important;
                }

                /* Container de la sidebar */
                .css-1cypcdb {
                    background: linear-gradient(180deg, #e8f5e8 0%, #c8e6c9 100%) !important;
                    border-right: 3px solid rgba(46, 125, 50, 0.2) !important;
                    
                }

                /* Style pour le menu option_menu */
                .nav-link {
                    background-color: rgba(255, 255, 255, 0.7) !important;
                    color: #2e7d32 !important;
                    border-radius: 20px !important;
                    margin: 8px 5px !important;
                    padding: 12px 20px !important;
                    transition: all 0.3s ease !important;
                    border: 2px solid transparent !important;
                    font-weight: 600 !important;
                    backdrop-filter: blur(10px) !important;
                    
                }

                .nav-link:hover {
                    background-color: rgba(46, 125, 50, 0.1) !important;
                    color: #1b5e20 !important;
                    border: 2px solid rgba(46, 125, 50, 0.3) !important;
                    transform: translateX(5px) !important;
                    box-shadow: 0 4px 15px rgba(46, 125, 50, 0.2) !important;
                }

                .nav-link-selected {
                    background: linear-gradient(135deg, #4caf50, #66bb6a) !important;
                    color: white !important;
                    border: 2px solid rgba(255, 255, 255, 0.3) !important;
                    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
                    transform: translateX(8px) !important;
                }

                /* Animation pour les icônes */
                .nav-link i {
                    transition: transform 0.3s ease !important;
                }

                .nav-link:hover i {
                    transform: scale(1.2) !important;
                }

                .nav-link-selected i {
                    transform: scale(1.1) !important;
                }


                @keyframes breathe {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                }

            </style>
            """, unsafe_allow_html=True)

#===================================================================================================

with st.sidebar:
    # Logo 
    # Affichage du logo cool 
    
    st.image("assets/images/logo_vert.png",output_format="auto")
    
    # Menu principal avec style personnalisé
    selected_main = option_menu(
        menu_title=None,  # On enlève le titre car on en a mis un stylisé
        options = ["Accueil", "Eleves", "Parents", "Autorités", "Sensibilisation"],
        icons = ["house-fill", "building", "people-fill", "shield-fill", "camera-video-fill"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {
                "padding": "10px",
                "background-color": "inherit",
                "border-radius": "20px"
            },
            "icon": {
                "color": "#2e7d32", 
                "font-size": "18px",
                "margin-right": "10px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "8px 0px",
                "padding": "12px 15px",
                "border-radius": "15px",
                "background-color": "rgba(255, 255, 255, 0.7)",
                "color": "#2e7d32",
                "border": "2px solid transparent",
                "transition": "all 0.3s ease",
                "backdrop-filter": "blur(10px)"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #4caf50, #66bb6a)",
                "color": "white",
                "border": "2px solid rgba(255, 255, 255, 0.3)",
                "box-shadow": "0 6px 20px rgba(76, 175, 80, 0.4)",
                "transform": "translateX(5px)"
            }
        }
    )
    
    # Séparateur décoratif
    st.markdown(
        """
        <div style="
            height: 3px; 
            background: linear-gradient(90deg, #4caf50, #81c784, #a5d6a7, #4caf50);
            border-radius: 2px; 
            margin: 25px 10px;
            animation: shimmer 2s infinite;
        "></div>
        """, 
        unsafe_allow_html=True
    )
    
    # Section informative
    st.markdown(
        """
        <div style="
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 15px;
            margin: 20px 5px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        ">
            <div style="color: #2e7d32; font-weight: bold; font-size: 0.9rem;">
                Données en temps réel
            </div>
            <div style="color: #666; font-size: 0.8rem;">
                Capteurs AirGradient
            </div>
        </div>
        
        <div style="
            background: rgba(255,255,255,0.85);
            border-radius: 12px;
            padding: 15px;
            margin-top: 20px;
            font-size: 0.85rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            color: #2e7d32;
        ">
            <b>Respirer, c’est vivre.</b><br>
            Chaque souffle compte. <br>Agissons aujourd’hui pour un air plus pur demain.
        </div>
        
        """, 
        unsafe_allow_html=True
    )
    

# ---------------------- SECTIONS FIXES POUR LA PAGE D'ACCUEIL -------------------------------

if selected_main == "Accueil":
    show_header_playful()

    tab1,tab2,tab3,tab4 = st.tabs(["Home","Parametres", "A Propos ","KaiKai"])

    with tab1:

        # Carte du Sénégal (à remplacer plus tard par vraie carte interactive)
        # st.markdown("### 🗺️ Carte du Sénégal")
        # st.info("Ici s’affichera la carte interactive avec les zones de pollution.")
        # st.image("assets/images/carte_senegal.png", caption="Carte du senegal placeholder", use_container_width=True)
        
        # ---------------------- # ---------------------- Carte des capteurs   # ---------------------- # ---------------------- 

        st.title("Carte des capteurs installés dans les écoles au Sénégal")

        # Liste de capteurs avec coordonnées
        
        locations = pd.read_csv("locations_info.csv")
        
        # Déclenche un refresh automatique toutes les 60s
        # count = st_autorefresh(interval=60000, limit=100, key="fizzbuzzcounter")

        # Recuperation des donnees actuelles de toutes les locations 
        @st.cache_data(show_spinner=False,ttl=60) # expire au bout de 1 min
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
        section_en_savoir_plus_air(liens)                   # Bloc de videos sur la qualite de l'air

        # ---------------------- # ---------------------- # ---------------------- # ---------------------- 
    with tab2:
        # Onglet : Parametres 
        from components import parametres
        parametres.parametre()

    with tab3 :
        
        # Onglet : A propos

        from components import apropos
        apropos.afficher_page_about()
        
            
        
    with tab4 :

        # Onglet : KaiKai

        from components.kaikai import render_kaikai_page
        
        render_kaikai_page()
        
# --------------------- CONTENU PRINCIPAL -----------------------------------

# ---------------------- ACTIONS DES MENUS PRINCIPAUX -----------------------
        
if selected_main == "Eleves":
    from components import ecole
    ecole.show()

elif selected_main == "Parents":
    from components import parent
    parent.show()

elif selected_main == "Autorités":
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


elif selected_main == "Sensibilisation":
    from components import sensibilisation

    sensibilisation.show_sensibilisation_page()



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


show_footer()



