# Page Kaikai optimisée pour le projet RESPiRE

import streamlit as st

def render_kaikai_page():
    # En-tête principal avec style
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    ">
        <h1 style="
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        "> À propos de Kaikai</h1>
        <p style="
            color: rgba(255,255,255,0.9);
            text-align: center;
            font-size: 1.2rem;
            margin: 0;
        ">Innovation • Environnement • Impact Social</p>
    </div>
    """, unsafe_allow_html=True)

    # Section principale avec colonnes
    col1, col2 = st.columns([2, 1])
    
    with col1:
                
        st.markdown("""
        **Kaikai** est une entreprise sociale sénégalaise qui met l'innovation au service de l'environnement, 
        de la santé et du développement durable. 
        
         **Mission** : Accompagner des initiatives à impact positif à travers :
        - Des programmes d'innovation collaborative
        - Des partenariats stratégiques avec des acteurs locaux
        - Des événements structurants comme ce hackathon RESPiRE
        - Un écosystème de solutions durables pour l'Afrique
        """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        
        
        # Logo Kaikai (vous pouvez ajuster le chemin)
        try:
            st.image("assets/images/kaikai_logo.png", width=180)
        except:
            st.markdown("""
            <div style="
                width: 180px;
                height: 120px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                color: white;
                font-weight: bold;
                font-size: 1.5rem;
            ">KAIKAI</div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Section Hackathon avec design attractif
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
    ">
        <h2 style="
            color: white;
            text-align: center;
            margin-bottom: 1rem;
            font-size: 2rem;
        "> Le Hackathon sur la qualite de l'air </h2>
    </div>
    """, unsafe_allow_html=True)

    # Contenu hackathon avec cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <h4 style="color: #333; margin-bottom: 0.5rem;">Objectif</h4>
            <p style="color: #666; font-size: 0.9rem;">Solutions concrètes pour améliorer la qualité de l'air scolaire</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💡</div>
            <h4 style="color: #333; margin-bottom: 0.5rem;">Innovation</h4>
            <p style="color: #666; font-size: 0.9rem;">Outils basés sur les données et technologies locales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🌍</div>
            <h4 style="color: #333; margin-bottom: 0.5rem;">Impact</h4>
            <p style="color: #666; font-size: 0.9rem;">Protéger la santé des enfants dans les écoles</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Description détaillée du hackathon
    st.markdown("""
    <div style="
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid #11998e;
        margin: 1.5rem 0;
    ">
        <p style="font-size: 1.1rem; line-height: 1.6; color: #333; margin: 0;">
            Ce hackathon rassemble des équipes de jeunes innovateurs passionnés qui travaillent 
            ensemble pour développer des solutions durables et adaptées au contexte local. <br>
            Notre projet <strong>RESPiRE</strong> s'inscrit dans cette démarche collaborative 
            pour créer un impact positif sur la santé environnementale des écoles sénégalaises.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Message de remerciement stylisé
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    ">
        <h3 style="color: white; margin-bottom: 0.5rem;">Merci Kaikai !</h3>
        <p style="color: rgba(255,255,255,0.9); margin: 0;">
            Un grand merci pour votre accompagnement et votre engagement pour l'innovation durable 🌿
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Lien vers Kaikai avec bouton stylisé
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <a href="https://www.kaikai.dev" target="_blank" style="
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
            box-shadow: 0 5px 15px rgba(17, 153, 142, 0.3);
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='translateY(-2px)'" 
           onmouseout="this.style.transform='translateY(0)'">
            Découvrir Kaikai
        </a>
    </div>
    """, unsafe_allow_html=True)

