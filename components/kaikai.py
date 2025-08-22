# Page Kaikai optimisée et professionnelle pour le projet RESPiRE

import streamlit as st

def render_kaikai_page():
    # CSS personnalisé pour un style professionnel
    st.markdown("""
    <style>
    .professional-container {
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #1a365d 0%, #2d5a87 50%, #4a90a4 100%);
        padding: 4rem 2rem;
        margin: -1rem -1rem 3rem -1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="rgba(255,255,255,0.05)"><polygon points="0,0 1000,100 1000,0"/></svg>');
        background-size: cover;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
    }
    
    .hero-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 300;
        margin-bottom: 1rem;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.3rem;
        font-weight: 300;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    .section-title {
        color: #1a365d;
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
        position: relative;
        padding-bottom: 1rem;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #4a90a4, #2d5a87);
    }
    
    .mission-card {
        background: white;
        padding: 3rem 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(26, 54, 93, 0.08);
        border: 1px solid rgba(26, 54, 93, 0.05);
        margin-bottom: 3rem;
        position: relative;
    }
    
    .mission-text {
        color: #2d3748;
        font-size: 1.1rem;
        line-height: 1.8;
        margin-bottom: 2rem;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-item {
        display: flex;
        align-items: flex-start;
        padding: 1.5rem;
        background: #f8fafc;
        border-radius: 12px;
        border-left: 4px solid #4a90a4;
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 144, 164, 0.15);
    }
    
    .feature-icon {
        color: #4a90a4;
        font-size: 1.5rem;
        margin-right: 1rem;
        margin-top: 0.2rem;
    }
    
    .feature-content {
        flex: 1;
    }
    
    .feature-title {
        color: #1a365d;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #4a5568;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .hackathon-section {
        background: linear-gradient(135deg, #2d5a87 0%, #4a90a4 100%);
        padding: 4rem 2rem;
        margin: 4rem -1rem 3rem -1rem;
        text-align: center;
        position: relative;
    }
    
    .hackathon-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .hackathon-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 3rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.1);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.15);
    }
    
    .stat-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .stat-title {
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .stat-desc {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .quote-section {
        background: #f8fafc;
        padding: 3rem 2rem;
        border-radius: 16px;
        margin: 3rem 0;
        position: relative;
        border-left: 6px solid #4a90a4;
    }
    
    .quote-text {
        font-size: 1.25rem;
        color: #2d3748;
        font-style: italic;
        line-height: 1.7;
        margin: 0;
        text-align: center;
    }
    
    .cta-section {
        background: linear-gradient(135deg, #1a365d 0%, #2d5a87 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 4rem 0 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .cta-title {
        color: white;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .cta-text {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #38b2ac 0%, #4fd1c7 100%);
        color: white;
        padding: 16px 40px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        display: inline-block;
        box-shadow: 0 10px 30px rgba(56, 178, 172, 0.4);
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(56, 178, 172, 0.5);
        text-decoration: none;
        color: white;
    }
    
    .logo-placeholder {
        width: 200px;
        height: 120px;
        background: linear-gradient(135deg, #4a90a4, #2d5a87);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 2rem auto;
        color: white;
        font-weight: bold;
        font-size: 1.8rem;
        letter-spacing: 2px;
        box-shadow: 0 10px 30px rgba(74, 144, 164, 0.3);
    }
    
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        .hackathon-title {
            font-size: 2rem;
        }
        .section-title {
            font-size: 1.8rem;
        }
        .hero-section, .hackathon-section {
            padding: 3rem 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # En-tête Hero professionnel
    st.markdown("""
    <div class="professional-container">
        <div class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">KAIKAI</h1>
                <p class="hero-subtitle">Innovation • Environnement • Impact Social</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Section principale avec logo et mission
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="mission-card">
            <h2 class="section-title">Notre Mission</h2>
            <p class="mission-text">
                <strong>Kaikai</strong> est une entreprise sociale sénégalaise de premier plan qui place l'innovation 
                au cœur des défis environnementaux, sanitaires et de développement durable. 
                Nous accompagnons la transformation digitale et sociale du continent africain.
            </p>
            
            <div class="features-grid">
                <div class="feature-item">
                    <div class="feature-icon">🚀</div>
                    <div class="feature-content">
                        <div class="feature-title">Innovation Collaborative</div>
                        <div class="feature-desc">Programmes d'accompagnement et d'accélération pour les startups à impact</div>
                    </div>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">🤝</div>
                    <div class="feature-content">
                        <div class="feature-title">Partenariats Stratégiques</div>
                        <div class="feature-desc">Collaboration avec des acteurs locaux et internationaux</div>
                    </div>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-content">
                        <div class="feature-title">Événements Structurants</div>
                        <div class="feature-desc">Organisation de hackathons et competitions d'innovation</div>
                    </div>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">🌍</div>
                    <div class="feature-content">
                        <div class="feature-title">Écosystème Durable</div>
                        <div class="feature-desc">Solutions adaptées aux contextes africains</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Logo Kaikai élégant
        try:
            st.image("assets/images/kaikai_logo.png", width=200)
        except:
            st.markdown("""
            <div class="logo-placeholder">
                KAIKAI
            </div>
            """, unsafe_allow_html=True)

    # Section Hackathon premium
    st.markdown("""
    <div class="hackathon-section">
        <h2 class="hackathon-title">Hackathon Qualité de l'Air</h2>
        <p class="hackathon-subtitle">Innovation technologique pour un environnement scolaire sain</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-title">Objectif</div>
                <div class="stat-desc">Développer des solutions concrètes pour améliorer la qualité de l'air dans les établissements scolaires</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">💡</div>
                <div class="stat-title">Innovation</div>
                <div class="stat-desc">Technologies de pointe basées sur l'IoT, l'analyse de données et l'intelligence artificielle</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🌍</div>
                <div class="stat-title">Impact</div>
                <div class="stat-desc">Protection de la santé de milliers d'enfants dans les écoles sénégalaises</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Citation inspirante
    st.markdown("""
    <div class="quote-section">
        <p class="quote-text">
            "Ce hackathon rassemble l'écosystème d'innovation sénégalais autour d'un enjeu majeur de santé publique. 
            Notre projet RESPiRE illustre parfaitement cette synergie entre technologie, engagement social et impact environnemental."
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Call-to-action professionnel
    st.markdown("""
    <div class="cta-section">
        <h3 class="cta-title">Partenaire d'Excellence</h3>
        <p class="cta-text">
            Nous remercions sincèrement Kaikai pour son accompagnement exceptionnel et son engagement 
            indéfectible en faveur de l'innovation durable et de l'entrepreneuriat social au Sénégal.
        </p>
        <a href="https://www.kaikai.dev" target="_blank" class="cta-button">
            Découvrir l'Écosystème Kaikai
        </a>
    </div>
    """, unsafe_allow_html=True)
