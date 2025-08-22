import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import time

# 🔧 PARAMÈTRES - DASHBOARD RESPiRE
# components/parametres.py


# Configuration des constantes
VERSION_DASHBOARD = "1.0.0"
LANGUES_DISPONIBLES = {
    "fr": "🇫🇷 Français",
    "wo": "🇸🇳 Wolof", 
    "en": "🇬🇧 English (bientôt)"
}

# Seuils de référence (basés sur OMS et normes locales)
SEUILS_REFERENCE = {
    "PM2.5": {
        "unite": "µg/m³",
        "excellent": 0,
        "bon": 12,
        "moyen": 35,
        "mauvais": 55,
        "tres_mauvais": 150,
        "source": "OMS 2021"
    },
    "PM10": {
        "unite": "µg/m³", 
        "excellent": 0,
        "bon": 25,
        "moyen": 50,
        "mauvais": 90,
        "tres_mauvais": 180,
        "source": "OMS 2021"
    },
    "CO₂": {
        "unite": "ppm",
        "excellent": 400,
        "bon": 600,
        "moyen": 1000,
        "mauvais": 1500,
        "tres_mauvais": 5000,
        "source": "ASHRAE"
    },
    "TVOC": {
        "unite": "ppb",
        "excellent": 0,
        "bon": 220,
        "moyen": 660,
        "mauvais": 2200,
        "tres_mauvais": 5500,
        "source": "UBA Allemagne"
    },
    "NOx": {
        "unite": "µg/m³",
        "excellent": 0,
        "bon": 40,
        "moyen": 100,
        "mauvais": 200,
        "tres_mauvais": 400,
        "source": "UE 2008"
    },
    "Température": {
        "unite": "°C",
        "excellent": 20,
        "bon": 23,
        "moyen": 27,
        "mauvais": 30,
        "tres_mauvais": 35,
        "source": "Confort ISO 7730"
    },
    "Humidité": {
        "unite": "%",
        "excellent": 40,
        "bon": 50,
        "moyen": 70,
        "mauvais": 80,
        "tres_mauvais": 90,
        "source": "ASHRAE"
    }
}


def show_header():
    """Affiche un en-tête professionnel pour la page Paramètres"""
    
    st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #f8fdf8 0%, #f1f8f1 100%);
        border: 1px solid #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.1);
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
        color: #155724;
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
    
    .professional-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 3px solid #28a745;
    }
    
    .section-title {
        color: #155724;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e9ecef;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8fdf8 0%, #ffffff 100%);
        border: 1px solid #d4edda;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #155724;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #6c757d;
        margin: 0.25rem 0 0 0;
    }
    
    .tab-content {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .settings-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1rem 0;
    }
    
    .settings-item {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 1rem;
    }
    
    .settings-item h4 {
        color: #495057;
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.75rem 0;
    }
    
    .action-buttons {
        background: #f8fdf8;
        border: 1px solid #d4edda;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('''
    <div class="header-container">
        <div class="header-content">
            <div class="title-main">
                Paramètres & Configuration
            </div>
            <div class="subtitle">
                Configurez votre expérience de surveillance de la qualité de l'air
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def initialiser_session_state():
    """Initialise les variables de session si elles n'existent pas"""
    defaults = {
        'langue_selectionnee': 'fr',
        'mode_sombre': False,
        'animations_activees': True,
        'notifications_activees': True,
        'auto_refresh': True,
        'intervalle_refresh': 300,  # 5 minutes
        'derniere_maj_manuelle': None,
        'ecole_preferee': None,
        'seuils_personnalises': SEUILS_REFERENCE.copy()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_system_stats():
    """Récupère les statistiques système simulées"""
    # Dans un vrai projet, ces données viendraient de votre base de données
    return {
        'capteurs_actifs': 1,
        'capteurs_total': 5,
        'ecoles_suivies': 0,
        'derniere_synchronisation': datetime.now() - timedelta(minutes=2),
        'uptime': timedelta(days=15, hours=3, minutes=42)
    }


def sauvegarder_parametres():
    """Sauvegarde les paramètres (simulation)"""
    # Dans un vrai projet, vous sauvegarderiez dans une base de données
    parametres = {
        'langue': st.session_state.langue_selectionnee,
        'mode_sombre': st.session_state.mode_sombre,
        'animations': st.session_state.animations_activees,
        'notifications': st.session_state.notifications_activees,
        'auto_refresh': st.session_state.auto_refresh,
        'intervalle_refresh': st.session_state.intervalle_refresh,
        'ecole_preferee': st.session_state.ecole_preferee,
        'timestamp': datetime.now().isoformat()
    }
    
    # Simulation de sauvegarde
    st.success("✅ Paramètres sauvegardés avec succès!")
    return True


def forcer_mise_a_jour():
    """Force la mise à jour des données"""
    with st.spinner("Synchronisation des données en cours..."):
        # Simulation de la mise à jour
        time.sleep(2)
        st.session_state.derniere_maj_manuelle = datetime.now()
        
        # Vider le cache Streamlit
        st.cache_data.clear()
        
    st.success("✅ Données synchronisées avec succès!")
    st.balloons()


def afficher_page_parametres():
    """Fonction principale pour afficher la page paramètres"""
    
    # Header professionnel
    show_header()
    
    # Initialisation
    initialiser_session_state()
    
    # Statistiques système en en-tête
    stats = get_system_stats()
    
    st.markdown('<div class="settings-grid">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{stats['ecoles_suivies']}</div>
            <div class="metric-label">Écoles surveillées</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{stats['capteurs_actifs']}/{stats['capteurs_total']}</div>
            <div class="metric-label">Capteurs déployés</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{(datetime.now() - stats['derniere_synchronisation']).seconds//60} min</div>
            <div class="metric-label">Dernière sync</div>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets pour organiser les paramètres
    tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Seuils", 
        "🔄 Synchronisation", 
        "🎨 Interface", 
        "⚙️ Système"
    ])
    
    # =====================================
    # ONGLET 2: SEUILS DE RÉFÉRENCE
    # =====================================
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Seuils de référence pour l\'évaluation</h3>', unsafe_allow_html=True)
        
        # Tableau des seuils
        seuils_df = []
        for parametre, valeurs in SEUILS_REFERENCE.items():
            seuils_df.append({
                'Paramètre': parametre,
                'Unité': valeurs['unite'],
                'Excellent': f"0 - {valeurs['excellent']}",
                'Bon': f"{valeurs['excellent']} - {valeurs['bon']}",
                'Moyen': f"{valeurs['bon']} - {valeurs['moyen']}",
                'Mauvais': f"{valeurs['moyen']} - {valeurs['mauvais']}",
                'Très Mauvais': f"> {valeurs['mauvais']}",
                'Source': valeurs['source']
            })
        
        df_seuils = pd.DataFrame(seuils_df)
        
        # Affichage du tableau
        st.dataframe(
            df_seuils,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Paramètre": st.column_config.TextColumn("🧪 Paramètre", width="medium"),
                "Unité": st.column_config.TextColumn("📏 Unité", width="small"),
                "Source": st.column_config.TextColumn("📚 Source", width="medium")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =====================================
    # ONGLET 3: SYNCHRONISATION
    # =====================================
    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="settings-item">', unsafe_allow_html=True)
            st.markdown('<h4>🔄 Mise à jour automatique</h4>', unsafe_allow_html=True)
            
            auto_refresh = st.toggle(
                "Actualisation automatique", 
                value=st.session_state.auto_refresh,
                key="auto_refresh_toggle"
            )
            st.session_state.auto_refresh = auto_refresh
            
            if auto_refresh:
                intervalle = st.select_slider(
                    "Intervalle de mise à jour",
                    options=[30, 60, 180, 300, 600, 1800],
                    value=st.session_state.intervalle_refresh,
                    format_func=lambda x: f"{x//60}:{x%60:02d}" if x >= 60 else f"{x}s",
                    key="intervalle_slider"
                )
                st.session_state.intervalle_refresh = intervalle
                
                st.info(f"ℹ️ Prochaine mise à jour dans ~ {intervalle//60} minutes")
            else:
                st.warning("⚠️ Mise à jour automatique désactivée")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="settings-item">', unsafe_allow_html=True)
            st.markdown('<h4>🔧 Mise à jour manuelle</h4>', unsafe_allow_html=True)
            
            derniere_maj = st.session_state.derniere_maj_manuelle
            if derniere_maj:
                st.info(f"Dernière mise à jour manuelle : {derniere_maj.strftime('%H:%M:%S')}")
            else:
                st.info("Aucune mise à jour manuelle effectuée")
            
            if st.button("🔄 Forcer la synchronisation", type="primary", use_container_width=True):
                forcer_mise_a_jour()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =====================================
    # ONGLET 4: INTERFACE
    # =====================================
    with tab4:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="settings-item">', unsafe_allow_html=True)
            st.markdown('<h4>🎨 Apparence</h4>', unsafe_allow_html=True)
            
            mode_sombre = st.toggle(
                "Mode sombre", 
                value=st.session_state.mode_sombre,
                key="mode_sombre_toggle"
            )
            st.session_state.mode_sombre = mode_sombre
            
            if mode_sombre:
                st.info("🌙 Mode sombre activé (redémarrage requis)")
            
            st.markdown('<h4>🌐 Langue d\'affichage</h4>', unsafe_allow_html=True)
            langue_actuelle = st.session_state.langue_selectionnee
            
            nouvelle_langue = st.selectbox(
                "Sélectionner la langue",
                options=list(LANGUES_DISPONIBLES.keys()),
                format_func=lambda x: LANGUES_DISPONIBLES[x],
                index=list(LANGUES_DISPONIBLES.keys()).index(langue_actuelle),
                key="langue_selector"
            )
            
            if nouvelle_langue != langue_actuelle:
                st.session_state.langue_selectionnee = nouvelle_langue
                st.info(f"Langue changée vers : {LANGUES_DISPONIBLES[nouvelle_langue]}")
                
            if nouvelle_langue == "en":
                st.warning("Anglais disponible prochainement")
                
            if nouvelle_langue == "wo":
                st.warning("Wolof disponible prochainement")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="settings-item">', unsafe_allow_html=True)
            st.markdown('<h4>🔔 Notifications</h4>', unsafe_allow_html=True)
            
            notifications = st.toggle(
                "Alertes de qualité d'air",
                value=st.session_state.notifications_activees,
                key="notifications_toggle"
            )
            st.session_state.notifications_activees = notifications
            
            if notifications:
                seuil_alerte = st.selectbox(
                    "Déclencher l'alerte à partir de :",
                    ["Moyen", "Mauvais", "Très Mauvais"],
                    index=1
                )
                st.info(f"🔔 Alertes activées pour niveau '{seuil_alerte}' et plus")
        
            # Aperçu des changements
            if st.button("👁️ Aperçu des modifications", use_container_width=True):
                st.balloons()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =====================================
    # ONGLET 5: INFORMATIONS SYSTÈME
    # =====================================
    with tab5:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.markdown('<h3 class="section-title">Informations du système</h3>', unsafe_allow_html=True)
        
        info_df = pd.DataFrame({
            'Propriété': [
                'Version RESPiRE',
                'Dernière mise à jour',
                'Développeur',
                'Licence',
                'Architecture'
            ],
            'Valeur': [
                VERSION_DASHBOARD,
                datetime.now().strftime("%d/%m/%Y"),
                'Équipe RESPiRE',
                'Open Source',
                'Streamlit + Python'
            ]
        })
        
        st.dataframe(info_df, hide_index=True, use_container_width=True)
        
        # Actions système
        st.markdown('<h3 class="section-title">Actions système</h3>', unsafe_allow_html=True)
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("🗑️ Vider le cache", use_container_width=True):
                st.cache_data.clear()
                st.success("Cache vidé!")
        
        with col_action2:
            if st.button("📤 Exporter config", use_container_width=True):
                config = {key: str(value) for key, value in st.session_state.items() if not key.startswith('_')}
                config_json = json.dumps(config, indent=2, ensure_ascii=False)
                st.download_button("💾 Télécharger", config_json, "config_respire.json", "application/json")
        
        with col_action3:
            if st.button("🔄 Redémarrer", use_container_width=True, type="secondary"):
                st.info("🔄 Redémarrage ...")
                time.sleep(1)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =====================================
    # BOUTONS D'ACTION PRINCIPAUX
    # =====================================
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 Sauvegarder tous les paramètres", type="primary", use_container_width=True):
            sauvegarder_parametres()
    
    with col2:
        if st.button("🔄 Restaurer par défaut", use_container_width=True):
            # Reset des paramètres
            for key in ['langue_selectionnee', 'mode_sombre', 'animations_activees', 'notifications_activees']:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Paramètres restaurés!")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================
# POINT D'ENTRÉE
# =====================================

def parametre():
    # Affichage de la page
    afficher_page_parametres()
