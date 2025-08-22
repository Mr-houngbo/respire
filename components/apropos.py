# PAGE À PROPOS - RESPIRE (DESIGN PRO MINIMALISTE)
# components/about.py
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

def afficher_page_about():
    """Page À Propos avec design ultra-professionnel et minimaliste"""
    
    # CSS professionnel minimaliste
    st.markdown("""
    <style>
    /* Variables globales */
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1d4ed8;
        --neutral-50: #f8fafc;
        --neutral-100: #f1f5f9;
        --neutral-200: #e2e8f0;
        --neutral-600: #475569;
        --neutral-700: #334155;
        --neutral-800: #1e293b;
        --neutral-900: #0f172a;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
    }
    
    /* Reset et base */
    .main > div {
        padding-top: 2rem !important;
    }
    
    /* Hero section minimaliste */
    .hero-minimal {
        padding: 4rem 0 3rem 0;
        text-align: center;
        border-bottom: 1px solid var(--neutral-200);
        margin-bottom: 4rem;
    }
    
    .hero-title {
        font-size: clamp(2.5rem, 5vw, 3.5rem);
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.125rem;
        color: var(--neutral-600);
        max-width: 600px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 1rem;
        background: var(--neutral-100);
        color: var(--neutral-700);
        border-radius: 50px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Cards minimalistes */
    .card-minimal {
        background: white;
        border: 1px solid var(--neutral-200);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .card-minimal:hover {
        border-color: var(--neutral-300);
        box-shadow: var(--shadow-md);
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--neutral-900);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-text {
        color: var(--neutral-600);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Section avec image */
    .image-section {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--neutral-200);
    }
    
    /* Stats minimalistes */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-item {
        text-align: center;
        padding: 1.5rem 1rem;
        background: var(--neutral-50);
        border: 1px solid var(--neutral-200);
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .stat-item:hover {
        background: white;
        border-color: var(--primary);
        transform: translateY(-1px);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 0.25rem;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--neutral-600);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Team grid */
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .team-card {
        background: white;
        border: 1px solid var(--neutral-200);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: left;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .team-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-md);
    }
    
    .team-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary);
        border-radius: 12px 12px 0 0;
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .team-card:hover::before {
        opacity: 1;
    }
    
    .team-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--neutral-900);
        margin-bottom: 0.75rem;
    }
    
    .team-description {
        color: var(--neutral-600);
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    .skills-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .skill-tag {
        background: var(--neutral-100);
        color: var(--neutral-700);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid var(--neutral-200);
    }
    
    /* Contact section */
    .contact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .contact-item {
        text-align: center;
        padding: 2rem 1rem;
        background: var(--neutral-50);
        border: 1px solid var(--neutral-200);
        border-radius: 12px;
        transition: all 0.2s ease;
    }
    
    .contact-item:hover {
        background: white;
        border-color: var(--primary);
        box-shadow: var(--shadow-sm);
    }
    
    .contact-icon {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: var(--primary);
    }
    
    .contact-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--neutral-900);
        margin-bottom: 0.5rem;
    }
    
    .contact-text {
        font-size: 0.9rem;
        color: var(--neutral-600);
    }
    
    .contact-link {
        color: var(--primary) !important;
        text-decoration: none;
    }
    
    .contact-link:hover {
        text-decoration: underline;
    }
    
    /* Section dividers */
    .section-divider {
        height: 1px;
        background: var(--neutral-200);
        margin: 3rem 0;
    }
    
    /* Typography */
    h2, h3, h4 {
        color: var(--neutral-900) !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
    }
    
    h2 {
        font-size: 1.875rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        margin-bottom: 1.25rem !important;
    }
    
    h4 {
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .hero-minimal {
            padding: 2rem 0;
        }
        
        .card-minimal {
            padding: 1.5rem;
        }
        
        .team-grid, .contact-grid {
            grid-template-columns: 1fr;
        }
        
        .stat-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # =====================================
    # HERO SECTION MINIMALISTE
    # =====================================
    st.markdown("""
    <div class="hero-minimal">
        <div class="hero-badge">
            💨 Monitoring de la qualité de l'air
        </div>
        <h1 class="hero-title">Breath4Life</h1>
        <p class="hero-subtitle">
            Nous transformons les données de qualité de l'air en actions concrètes 
            pour protéger la santé des enfants dans les écoles sénégalaises.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # =====================================
    # LAYOUT PRINCIPAL
    # =====================================
    
    # Section avec image et description
    col_image, col_content = st.columns([1, 2], gap="large")
    
    with col_image:
        st.markdown('<div class="image-section">', unsafe_allow_html=True)
        try:
            image_path = "assets/images/equipe.png"
            image = Image.open(image_path)
            st.image(image, use_container_width=True)
        except:
            st.markdown("""
            <div style="background: var(--neutral-100); padding: 4rem 2rem; text-align: center; color: var(--neutral-500);">
                📸 Image d'équipe
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_content:
        st.markdown("""
        <div class="card-minimal">
            <h3 class="card-title">🎯 Notre Mission</h3>
            <p class="card-text">
                Rendre visible et compréhensible la qualité de l'air dans les écoles sénégalaises 
                grâce à la technologie et à l'engagement communautaire. Nous croyons qu'une 
                information accessible est le premier pas vers un environnement plus sain.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card-minimal">
            <h4 class="card-title">⭐ Nos Valeurs</h4>
            <p class="card-text">
                <strong>Transparence</strong> • <strong>Innovation</strong> • <strong>Impact social</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # =====================================
    # STATISTIQUES D'IMPACT
    # =====================================
    st.markdown("## 📊 Notre Impact")
    
    st.markdown("""
    <div class="stat-grid">
        <div class="stat-item">
            <div class="stat-number">5</div>
            <div class="stat-label">Écoles</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">10</div>
            <div class="stat-label">Capteurs</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">2500+</div>
            <div class="stat-label">Élèves</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # =====================================
    # EXPERTISES DE L'ÉQUIPE
    # =====================================
    st.markdown("## 👥 Nos Expertises")
    
    team_roles = [
        {
            "title": "Data & Développement",
            "description": "Analyse avancée, visualisation interactive et traitement automatique des données AirGradient en temps réel.",
            "skills": ["Python", "Streamlit", "APIs", "Data Science"]
        },
        {
            "title": "Environnement & Éducation", 
            "description": "Création de contenus pédagogiques en langues locales et formation des communautés éducatives.",
            "skills": ["Pédagogie", "Environnement", "Communication", "Wolof"]
        },
        {
            "title": "Design & Interface",
            "description": "Conception d'interfaces intuitives adaptées à tous les publics : élèves, parents et autorités.",
            "skills": ["UX/UI", "Design", "Accessibilité", "Responsive"]
        },
        {
            "title": "Coordination & Partenariats",
            "description": "Pilotage projet, relations institutionnelles et développement de partenariats stratégiques.",
            "skills": ["Management", "Stratégie", "Communication", "Partenariats"]
        }
    ]
    
    st.markdown('<div class="team-grid">', unsafe_allow_html=True)
    for role in team_roles:
        skills_html = ''.join([f'<span class="skill-tag">{skill}</span>' for skill in role['skills']])
        st.markdown(f"""
        <div class="team-card">
            <h4 class="team-title">{role['title']}</h4>
            <p class="team-description">{role['description']}</p>
            <div class="skills-container">
                {skills_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # =====================================
    # CONTACT
    # =====================================
    st.markdown("## 📞 Nous Contacter")
    
    st.markdown("""
    <div class="contact-grid">
        <div class="contact-item">
            <div class="contact-icon">📧</div>
            <h4 class="contact-title">Email</h4>
            <p class="contact-text">
                <a href="mailto:contact@breath4life.sn" class="contact-link">
                    contact@breath4life.sn
                </a>
            </p>
        </div>
        
        <div class="contact-item">
            <div class="contact-icon">📱</div>
            <h4 class="contact-title">Téléphone</h4>
            <p class="contact-text">+221 77 XXX XX XX</p>
        </div>
        
        <div class="contact-item">
            <div class="contact-icon">📍</div>
            <h4 class="contact-title">Localisation</h4>
            <p class="contact-text">Dakar, Sénégal</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer subtle
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid var(--neutral-200); color: var(--neutral-500); font-size: 0.875rem;">
        Breath4Life © 2024 • Pour un air plus sain dans nos écoles
    </div>
    """, unsafe_allow_html=True)
