#  PAGE À PROPOS - RESPIRE (DESIGN MODERNE)
# components/about.py
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

def afficher_page_about():
    """Page À Propos avec design moderne et interactif"""
    
    # CSS personnalisé pour une apparence moderne
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .team-member {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .team-member:hover {
        border-color: #667eea;
        transform: scale(1.02);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .impact-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .timeline-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .social-button {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        text-decoration: none;
        border-radius: 25px;
        margin: 0.5rem;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .social-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # SECTION MODIFIÉE - IMAGE À GAUCHE, INFOS À DROITE
    
    # =====================================
    # LAYOUT PRINCIPAL - IMAGE À GAUCHE, TOUT LE RESTE À DROITE
    # =====================================
    
    # Division principale : 1/3 pour l'image, 2/3 pour le contenu
    col_image, col_content = st.columns([1, 2])
    
    # =====================================
    # COLONNE GAUCHE - IMAGE D'ÉQUIPE
    # =====================================
    with col_image:
        
        # Image d'équipe avec cadre stylisé
        image_path = "assets/images/equipe.png"
        image = Image.open(image_path)

        st.image(image, caption="Breath4Life Team", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # =====================================
    # COLONNE DROITE - TOUT LE CONTENU
    # =====================================
    with col_content:
        
        # Qui sommes-nous
        st.markdown("""
        <div class="card">
            <h3> Qui sommes-nous ?</h3>
            <p style="font-size: 1.1rem; line-height: 1.7; color: #555;">
                Nous sommes un collectif de <strong>jeunes passionnés</strong> par l'environnement, 
                la technologie et la santé publique. Unis par une vision commune : 
                <em>transformer les données en actions concrètes</em> pour la santé de nos enfants.
            </p>
            <div style="margin-top: 1rem; padding: 1rem; background: linear-gradient(135deg, #667eea22, #764ba222); border-radius: 10px;">
                <strong style="color: #667eea;"> "Un air plus sain, une génération plus consciente"</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mission & Vision côte à côte
        
        st.markdown("""
        <div class="card">
            <h4> Notre Mission</h4>
            <p style="font-size: 1rem; line-height: 1.6; color: #555;">
                Rendre <strong>visible et compréhensible</strong> la qualité de l'air dans les écoles sénégalaises 
                grâce à la technologie et à l'engagement communautaire.
            </p>
            <ul style="font-size: 0.9rem; color: #666; padding-left: 1rem;">
                <li> Surveillance temps réel</li>
                <li> Sensibilisation des élèves</li>
                <li> Actions environnementales</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)        
        
        
# Statistiques d'impact
    st.markdown("### Notre Impact")
    
    stats_subcol1, stats_subcol2, stats_subcol3 = st.columns(3)
    
    stats = [
        ("", "5", "Écoles"),
        ("", "10", "Capteurs"),
        ("", "2,500+", "Élèves"),
    ]
    
    for i, (emoji, number, label) in enumerate(stats):
        with [stats_subcol1, stats_subcol2, stats_subcol3][i]:
            st.markdown(f"""
            <div class="stats-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">{emoji}</div>
                <div class="impact-number">{number}</div>
                <div style="font-size: 0.8rem; opacity: 0.9;">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
        
    # Profils d'équipe
    st.markdown("###  Nos Expertises")
    
    team_roles = [
        {
            "emoji": "",
            "title": "Data & Développement",
            "description": "Analyse avancée, visualisation interactive, traitement automatique des données AirGradient",
            "skills": ["Python", "Streamlit", "APIs", "Visualisation"]
        },
        {
            "emoji": "", 
            "title": "Environnement & Éducation",
            "description": "Contenus de sensibilisation en Wolof, formation des élèves, expertise environnementale",
            "skills": ["Pédagogie", "Environnement", "Communication"]
        },
        {
            "emoji": "",
            "title": "Design & Interface",
            "description": "Conception d'interfaces adaptées aux élèves, parents et autorités éducatives",
            "skills": ["UX/UI", "Design", "Accessibilité", "Ergonomie"]
        },
        {
            "emoji": "",
            "title": "Coordination & Communication", 
            "description": "Pilotage agile, structuration projet, communication institutionnelle",
            "skills": ["Management", "Communication", "Stratégie", "Partenariats"]
        }
    ]
    
    cols = st.columns(2)
    for i, role in enumerate(team_roles):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="team-member">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{role['emoji']}</div>
                <h4 style="color: #667eea; margin-bottom: 1rem;">{role['title']}</h4>
                <p style="color: #555; margin-bottom: 1rem;">{role['description']}</p>
                <div>
                    {' '.join([f'<span style="background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin: 0.2rem;">{skill}</span>' for skill in role['skills']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # =====================================
    # CONTACT ET RÉSEAUX SOCIAUX
    # =====================================
    st.markdown("##  Nous Contacter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h4> Email</h4>
            <p><a href="mailto:contact@breath4life.sn" style="color: #667eea;">contact@breath4life.sn</a></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h4> Téléphone</h4>
            <p style="color: #667eea;">+221 77 XXX XX XX | +221 77 XXX XX XX | +221 77 XXX XX XX</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h4> Localisation</h4>
            <p style="color: #667eea;">Dakar, Sénégal</p>
        </div>
        """, unsafe_allow_html=True)