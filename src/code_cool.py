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
        <div style="font-size: 2rem; margin-bottom: 10px;">📊</div>
        <div style="color: #2e7d32; font-weight: bold; font-size: 0.9rem;">
            Données en temps réel
        </div>
        <div style="color: #666; font-size: 0.8rem;">
            Capteurs AirGradient
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)


"""
# Menu bottom avec le même style que la sidebar
selected_bottom = option_menu(
    menu_title=None,
    options=["Contactez-nous", "Paramètres"],
    icons=["telephone-fill", "gear-fill", "trophy-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "10px",
            "background": "linear-gradient(90deg, #e8f5e8, #c8e6c9, #a5d6a7)",
            "border-radius": "20px",
            "box-shadow": "0 4px 15px rgba(46, 125, 50, 0.2)",
            "margin": "20px 20"
        },
        "icon": {
            "color": "#2e7d32", 
            "font-size": "18px",
            "margin-right": "8px"
        },
        "nav-link": {
            "font-size": "15px",
            "text-align": "center",
            "margin": "0 5px",
            "padding": "12px 20px",
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
            "box-shadow": "0 4px 15px rgba(76, 175, 80, 0.4)",
            "transform": "translateY(-2px)"
        }
    
    }
)
"""









#=========================== SECTION PRISE DEPUIS PARENT.PY =================================
#=========================== SECTION PRISE DEPUIS PARENT.PY =================================
#=========================== SECTION PRISE DEPUIS PARENT.PY =================================





# CE QUE CE CODE FAIT PRINCIPALEMENT GRACE A LA FONCTION show_now , c'est d'afficher tous les indices recueillis now now directement sur le dashboard , le test pour le visualiser est tout en bas 
# Ton boulot sera de l'adapter aux parents plutard (Vu que c'est juste un copier-coller de la vue ecole)

def show():
    st.header("📊 Vue des parents")
    st.markdown("Données spécifiques aux Parents bientot ici.")

def show_header(nom_ecole: str = None, logo_path: str = None):
    """
    Affiche l'entête de la page École.
    :param nom_ecole: Nom de l'école à afficher (optionnel)
    :param logo_path: Chemin vers le logo de l'école (optionnel)
    """

    # Conteneur d'entête
    with st.container():
        col1, col2 = st.columns([4, 1])  # Titre à gauche, logo éventuel à droite

        with col1:
            st.markdown(
                "<h1 style='color:#2E7D32;'>Bienvenue dans ton espace santé – Respire 🌿</h1>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<h4 style='color:#555;'>Découvre comment va l’air de ton école aujourd’hui !</h4>",
                unsafe_allow_html=True
            )

            if nom_ecole:
                st.markdown(f"<h5 style='color:#888;'>🏫 {nom_ecole}</h5>", unsafe_allow_html=True)

        with col2:
            if logo_path:
                st.image(logo_path, width=80)

        st.markdown("---")  # Ligne de séparation

"""
def show_air_quality(location_id: str):
    
    Affiche la qualité de l'air d'une école en se basant sur son IQA.
    :param location_id: ID de l'école (sert à lire son CSV)
    
    iqa, pollutant = calculer_iqa(location_id)

    if iqa is None:
        return

    # Déterminer la catégorie IQA
    if iqa < 50:
        couleur = "#4CAF50"  # Vert
        statut = "Bon 😃"
        message = "L’air est bon ! Tu peux jouer dehors."
    elif iqa < 100:
        couleur = "#FFC107"  # Jaune
        statut = "Moyennement dégradé 😐"
        message = "Pense à bien t’hydrater et à te laver les mains."
    elif iqa < 200:
        couleur = "#FF5722"  # Orange/Rouge
        statut = "Mauvais 😷"
        message = "Attention ! Il vaut mieux rester à l’intérieur aujourd’hui."
    else:
        couleur = "#6D4C41"  # Marron
        statut = "Très mauvais 🚫"
        message = "Ne joue pas dehors ! Il faut rester protégé."

    # Affichage
    with st.container():
        st.markdown("## 🟢 Qualité de l’air aujourd’hui")
        st.markdown(
            f""""""
            <div style="background-color:{couleur}; padding: 15px; border-radius: 10px; text-align:center; color:white;">
                <h2>IQA : {iqa}</h2>
                <h4>Polluant principal : {pollutant}</h4>
                <h3>Qualité : {statut}</h3>
            </div>
            ""","""
            unsafe_allow_html=True
        )

        st.info(f"💡 {message}")
"""

def show_now(df: pd.DataFrame):

    # Exemple de DataFrame (à remplacer par ton fetch_current_data)
    # df = fetch_current_data(location_id, token)

    # Icônes et unités pour affichage
    POLLUTANTS_INFO = {
        "rco2_corrected": {"label": "CO₂", "unit": "ppm", "icon": "🌬️"},
        "tvoc": {"label": "TVOC", "unit": "µg/m³", "icon": "🧪"},
        "pm01_corrected": {"label": "PM1.0", "unit": "µg/m³", "icon": "🌫️"},
        "pm02_corrected": {"label": "PM2.5", "unit": "µg/m³", "icon": "🌁"},
        "pm10_corrected": {"label": "PM10", "unit": "µg/m³", "icon": "🏭"},
        "noxIndex": {"label": "NOx", "unit": "µg/m³", "icon": "🚗"},
    }

    st.subheader("🔬 Polluants mesurés actuellement")

    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    cols = st.columns(3)  # Crée 3 colonnes pour affichage

    index = 0
    for key, info in POLLUTANTS_INFO.items():
        if key in df.columns:
            value = df[key].mean()
            if pd.isna(value):
                continue

            col = cols[index % 3]
            with col:
                st.markdown(f"""
                    <div style="background-color: #f0f9ff; padding: 1rem; border-radius: 0.5rem; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <h4 style="margin-bottom: 0.5rem;">{info['icon']} {info['label']}</h4>
                        <p style="font-size: 24px; font-weight: bold; margin: 0;">{round(value, 1)} {info['unit']}</p>
                    </div>
                """, unsafe_allow_html=True)
            index += 1
        else:
            st.info(f"🛈 Donnée manquante pour {info['label']}")

    # Exemple d’appel
    # afficher_polluants(df)



#===============================================================================   TEST   ============================================================================

import streamlit as st
from components.ecole_ import show_header,show_now
from components.calculer_iqa import calculer_iqa,fetch_current_data
import pandas as pd 


location_id = "164928"
token = "77a25676-a9ec-4a99-9137-f33e6776b590"


def show():
    # Bloc I - Titre
    show_header(nom_ecole="École Multinationale des Telecommunications de Dakar", logo_path="assets/images/logo_esmt.jpeg")

    # Bloc II - Qualité de l'air (valeur fictive pour test)
    # show_air_quality(pm25_value=76)


# Test pour voir si les donnees actuellees recues sont justes

df = fetch_current_data(location_id,token)
show_now(df)


#=========================== SECTION PRISE DEPUIS PARENT.PY =================================












def send_sms_orange_senegal(self, phone_number, message):
    """Envoie SMS via API Orange Sénégal (à adapter selon l'API réelle)"""
    try:
        # Exemple d'implémentation - à adapter selon l'API Orange
        url = "https://api.orange.sn/sms/v1/send"  # URL exemple
        headers = {
            'Authorization': f'Bearer {self.config["orange_api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': phone_number,
            'message': message,
            'from': 'RESPiRE'  # Nom expéditeur
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "SMS envoyé via Orange"
        else:
            return False, f"Erreur Orange API: {response.status_code}"
            
    except Exception as e:
        return False, f"Erreur Orange: {str(e)}"

def send_sms_free(self, phone_number, message):
    """Envoie SMS via service gratuit (pour tests uniquement)"""
    try:
        # Service SMS gratuit pour tests - attention aux limitations
        url = "https://textbelt.com/text"
        data = {
            'phone': phone_number,
            'message': message,
            'key': 'textbelt'  # Clé gratuite limitée
        }
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result.get('success'):
            return True, "SMS envoyé (service test)"
        else:
            return False, f"Erreur service SMS: {result.get('error', 'Inconnu')}"
            
    except Exception as e:
        return False, f"Erreur SMS gratuit: {str(e)}"



#=========================== Premier code de creation de carte =================================




m = folium.Map(location=[14.5, -14.5], zoom_start=6)

# Creation du popup

for _, loc in locations.iterrows():
    data = data_by_location[loc["location_id"]]
    
    if "error" in data:
        popup_text = f"<b>{loc['name']}</b><br>❌ Erreur données : {data['error']}"
    else:
        popup_text = f"""
                        <b>{loc['name']}</b><br>
                        🕐 {data['last_update']}<br>
                        🌫️ PM2.5 : {data['pm25']} µg/m³<br>
                        💨 CO₂ : {data['co2']} ppm<br>
                        🌡️ Temp : {data['temp']} °C<br>
                        💧 Humidité : {data['humidity']} %<br>
                        🧪 PM10 : {data['pm10']} µg/m³<br>
                        🌫️ PM1 : {data['pm1']} µg/m³<br>
                        🔬 PM0.3 Count : {data['pm03']}<br>
                        🧴 TVOC : {data['tvoc']}<br>
                        🧪 NOx : {data['nox']}
                    """
        
        # popup.options = {"autoPan": False}
        
        popup_html = f"""
                        <div style="max-height: 200px; overflow-y: auto;">
                            {popup_text}
                        </div>
                        """

        popup = folium.Popup(popup_text, max_width=300, min_width=250)
        popup.options = {
                        "autoPan": True,
                        "autoPanPaddingTopLeft": [0, 100],  # Décale légèrement vers le bas
                        "autoPanPaddingBottomRight": [0, 0],
                    }


    folium.Marker(
        location=[loc["lat"], loc["lon"]],
        popup=popup,
        tooltip=loc["name"],
        icon=folium.Icon(color = {
                                        "excellente": "green",
                                        "bonne": "lightgreen",
                                        "moyenne": "orange",
                                        "mauvaise": "red",
                                        "très mauvaise": "darkred"
                                    }.get(loc["status"].lower(), "gray")
                            )
    ).add_to(m)




# Affichage dans Streamlit
st_folium(m, width="100%", height=400, returned_objects=[], use_container_width=True)




def display_map_with_school_selector(locations, data_by_location):
    """Affiche la carte avec un sélecteur d'école Streamlit"""
    
    # Créer la liste des écoles pour le selectbox
    school_names = ["-- Choisir une école --"] + locations['name'].tolist()
    
    # Sélecteur d'école
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_school = st.selectbox(
            " Sélectionnez une école :",
            school_names,
            key="school_selector"
        )
    
    # Créer la carte
    m = create_optimized_map(locations, data_by_location)
    
    # Si une école est sélectionnée, centrer la carte dessus
    if selected_school != "-- Choisir une école --":
        school_data = locations[locations['name'] == selected_school].iloc[0]
        m = folium.Map(
            location=[school_data['lat'], school_data['lon']], 
            zoom_start=12,
            tiles=None
        )
        
        # Réajouter les couches et marqueurs avec focus sur l'école sélectionnée
        folium.TileLayer('CartoDB Positron', name='Clair', control=True).add_to(m)
        folium.TileLayer('CartoDB Dark_Matter', name='Sombre', control=True).add_to(m)
        folium.TileLayer('OpenStreetMap', name='Standard', control=True).add_to(m)
        
        # Groupe de marqueurs
        marker_cluster = plugins.MarkerCluster(
            name="Capteurs",
            options={'maxClusterRadius': 50, 'disableClusteringAtZoom': 10}
        ).add_to(m)
        
        # Ajouter tous les marqueurs mais mettre en évidence l'école sélectionnée
        for _, loc in locations.iterrows():
            data = data_by_location[loc["location_id"]]
            popup_html = create_styled_popup(loc, data)
            
            # Marqueur spécial pour l'école sélectionnée
            if loc['name'] == selected_school:
                # Marqueur plus grand et pulsant pour l'école sélectionnée
                selected_icon_svg = f"""
                <svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="25" cy="25" r="23" fill="{get_air_quality_color(loc['status'])}" 
                            stroke="white" stroke-width="4" opacity="0.9">
                        <animate attributeName="r" values="20;25;20" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="25" cy="25" r="18" fill="{get_air_quality_color(loc['status'])}" opacity="0.8"/>
                    <text x="25" y="30" text-anchor="middle" font-size="14" fill="white">
                        {get_air_quality_icon(loc['status'])}
                    </text>
                </svg>
                """
                icon = folium.DivIcon(
                    html=f'<div style="transform: translate(-25px, -25px);">{selected_icon_svg}</div>',
                    icon_size=(50, 50),
                    icon_anchor=(25, 25)
                )
            else:
                icon = create_custom_marker_icon(loc["status"])
            
            marker = folium.Marker(
                location=[loc["lat"], loc["lon"]],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=folium.Tooltip(f"<b>{loc['name']}</b><br>Qualité: {loc['status']}", sticky=True),
                icon=icon
            )
            marker.add_to(marker_cluster)
        
        # Ajouter la légende
        legend_html = """
        <div style="
            position: fixed;
            bottom: 50px;
            left: 50px;
            width: 200px;
            height: auto;
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            font-size: 12px;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            z-index: 9999;
        ">
            <h4 style="margin: 0 0 10px 0; color: #333;">Qualité de l'air</h4>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #00e400; border-radius: 50%; margin-right: 8px;"></div>
                <span> Excellente</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #ffff00; border-radius: 50%; margin-right: 8px;"></div>
                <span> Bonne</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #ff7e00; border-radius: 50%; margin-right: 8px;"></div>
                <span> Moyenne</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #ff0000; border-radius: 50%; margin-right: 8px;"></div>
                <span> Mauvaise</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #8f3f97; border-radius: 50%; margin-right: 8px;"></div>
                <span> Très mauvaise</span>
            </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
                
        # Ajouter le contrôle des couches
        folium.LayerControl().add_to(m)
        
        # Plugin pour la recherche
        plugins.Search(layer=marker_cluster,search_label='name',placeholder='Rechercher un capteur...').add_to(m)    
        
          

    # Afficher la carte
    return st_folium(m, width="100%", height=600, returned_objects=[], use_container_width=True)
    
    
    
    
    
#=============================================================================================================

def show_header(nom_ecole, logo_path: str = None):
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
    
    .school-name {
        font-size: 1.1rem;
        color: #4caf50;
        background: rgba(255,255,255,0.7);
        padding: 0px 0px;
        padding-left: 0px;
        border-radius: 25px;
        display: inline-block;
        margin-top: 0px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        animation: fadeInUp 1.4s ease-out;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    
    .logo-image {
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 3px solid white;
        animation: bounce 2s infinite;
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
                '<div class="subtitle">Découvrez comment va l\'air de l\'école dans les ecoles de votre ville aujourd\'hui et prenez des décisions !</div>',
                unsafe_allow_html=True
            )
            
        
        with col2:
            if logo_path:
                
                 # Nom de l'école avec style modernisé
                if nom_ecole:
                    st.markdown(
                        f'<div class="school-name"> {nom_ecole}</div>',
                        unsafe_allow_html=True
                    )
                    
                    
                st.markdown('<div class="logo-container">', unsafe_allow_html=True)
                try:
                    st.image(logo_path, width=100, use_container_width=False)
                except:
                    # Fallback si l'image ne se charge pas
                    st.markdown(
                        '<div style="font-size: 60px; text-align: center;">🏫</div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)
                
                    
            else:
                # Logo par défaut si aucun logo fourni
                st.markdown(
                    '<div class="logo-container"><div style="font-size: 60px; text-align: center;">🏫</div></div>',
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ligne décorative animée
        st.markdown('<div class="decorative-line"></div>', unsafe_allow_html=True)

