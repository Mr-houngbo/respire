# Page Kaikai avec les vraies couleurs et design élégant

import streamlit as st

def render_kaikai_page():
    # CSS avec les vraies couleurs Kaikai et design moderne
    st.markdown("""
    <style>
    .kaikai-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.6;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 4rem 0;
        margin: -2rem -2rem 4rem -2rem;
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
        background: radial-gradient(circle at 30% 50%, rgba(249, 115, 22, 0.1) 0%, transparent 50%);
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        max-width: 800px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .hero-logo {
        width: 120px;
        height: 120px;
        background: white;
        border-radius: 20px;
        margin: 0 auto 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .hero-logo::after {
        content: 'k';
        font-size: 4rem;
        font-weight: bold;
        color: #1e40af;
        position: relative;
    }
    
    .hero-logo::before {
        content: '';
        position: absolute;
        top: 20px;
        right: 20px;
        width: 12px;
        height: 12px;
        background: #f97316;
        border-radius: 50%;
    }
    
    .hero-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: -2px;
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.4rem;
        font-weight: 300;
        margin: 0;
    }
    
    .content-section {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .section-header {
        text-align: center;
        margin-bottom: 4rem;
    }
    
    .section-title {
        color: #1e40af;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .section-description {
        color: #64748b;
        font-size: 1.2rem;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .mission-grid {
        display: grid;
        grid-template-columns: 1fr 300px;
        gap: 4rem;
        align-items: start;
        margin-bottom: 5rem;
    }
    
    .mission-content {
        background: white;
        padding: 3rem;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.08);
        border: 1px solid #e2e8f0;
    }
    
    .mission-text {
        color: #334155;
        font-size: 1.15rem;
        line-height: 1.8;
        margin-bottom: 2rem;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background: white;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.08);
        border: 1px solid #e2e8f0;
        height: fit-content;
        position: sticky;
        top: 2rem;
    }
    
    .kaikai-logo-display {
        width: 200px;
        height: 140px;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        color: white;
        font-size: 3rem;
        font-weight: bold;
    }
    
    .kaikai-logo-display::after {
        content: '';
        position: absolute;
        top: 15px;
        right: 15px;
        width: 16px;
        height: 16px;
        background: #f97316;
        border-radius: 50%;
    }
    
    .features-section {
        margin: 5rem 0;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1e40af, #f97316);
        transform: translateX(-100%);
        transition: transform 0.4s ease;
    }
    
    .feature-card:hover::before {
        transform: translateX(0);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(30, 64, 175, 0.15);
        border-color: #3b82f6;
    }
    
    .feature-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        position: relative;
    }
    
    .feature-icon::after {
        content: '';
        position: absolute;
        top: -2px;
        right: -2px;
        width: 8px;
        height: 8px;
        background: #f97316;
        border-radius: 50%;
    }
    
    .feature-title {
        color: #1e40af;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #64748b;
        line-height: 1.6;
    }
    
    .hackathon-section {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        margin: 5rem -2rem;
        padding: 5rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hackathon-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 70% 30%, rgba(30, 64, 175, 0.1) 0%, transparent 50%);
    }
    
    .hackathon-content {
        position: relative;
        z-index: 2;
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .hackathon-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    .hackathon-subtitle {
        color: rgba(255,255,255,0.95);
        font-size: 1.3rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    .objectives-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .objective-card {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .objective-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.2);
    }
    
    .objective-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .objective-title {
        color: white;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .objective-text {
        color: rgba(255,255,255,0.9);
        line-height: 1.6;
    }
    
    .testimonial-section {
        margin: 5rem 0;
        text-align: center;
    }
    
    .testimonial-card {
        background: #f8fafc;
        padding: 3rem;
        border-radius: 24px;
        max-width: 800px;
        margin: 0 auto;
        border-left: 6px solid #1e40af;
        position: relative;
    }
    
    .testimonial-card::before {
        content: '"';
        position: absolute;
        top: 1rem;
        left: 2rem;
        font-size: 4rem;
        color: #f97316;
        opacity: 0.3;
    }
    
    .testimonial-text {
        color: #334155;
        font-size: 1.3rem;
        line-height: 1.7;
        font-style: italic;
        margin: 0;
    }
    
    .cta-section {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 4rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin: 4rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .cta-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(249, 115, 22, 0.1) 0%, transparent 50%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .cta-content {
        position: relative;
        z-index: 2;
    }
    
    .cta-title {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    .cta-text {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-bottom: 2.5rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        padding: 16px 40px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        display: inline-block;
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.4);
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(249, 115, 22, 0.5);
        text-decoration: none;
        color: white;
    }
    
    @media (max-width: 968px) {
        .mission-grid {
            grid-template-columns: 1fr;
            gap: 2rem;
        }
        
        .logo-container {
            order: -1;
            position: static;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hackathon-title {
            font-size: 2.2rem;
        }
        
        .section-title {
            font-size: 2rem;
        }
    }
    
    @media (max-width: 640px) {
        .hackathon-section, .hero-section, .cta-section {
            margin-left: -1rem;
            margin-right: -1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .content-section {
            padding: 0 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Structure HTML complète
    st.markdown("""
    <div class="kaikai-container">
        <!-- Hero Section -->
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-logo"></div>
                <h1 class="hero-title">kaikai</h1>
                <p class="hero-subtitle">Lead and digital development</p>
            </div>
        </div>
        <!-- Section Mission -->
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">À propos de Kaikai</h2>
                <p class="section-description">
                    L'entreprise sociale qui transforme l'écosystème d'innovation africain
                </p>
            </div>
            <div class="mission-grid">
                <div class="mission-content">
                    <p class="mission-text">
                        <strong>Kaikai</strong> est une entreprise sociale sénégalaise de premier plan qui place l'innovation 
                        au cœur des défis environnementaux, sanitaires et de développement durable. 
                        Ils accompagnent la transformation digitale et sociale du continent africain à travers des initiatives concrètes.
                    </p>
                    <p class="mission-text">
                        Leur approche collaborative et leur engagement pour l'impact social font de Kaikai 
                        un acteur incontournable de l'écosystème d'innovation sénégalais.
                    </p>
                </div>
                <div class="logo-container">
                    <div class="kaikai-logo-display">k</div>
                </div>
            </div>
            <!-- Section Features -->
            <div class="features-section">
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🚀</div>
                        <h3 class="feature-title">Innovation Collaborative</h3>
                        <p class="feature-description">
                            Programmes d'accompagnement et d'accélération pour les startups à impact social et environnemental.
                        </p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🤝</div>
                        <h3 class="feature-title">Partenariats Stratégiques</h3>
                        <p class="feature-description">
                            Collaboration avec des acteurs locaux et internationaux pour maximiser l'impact des projets.
                        </p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🌍</div>
                        <h3 class="feature-title">Solutions Africaines</h3>
                        <p class="feature-description">
                            Développement d'un écosystème de solutions durables adaptées aux contextes africains.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        <!-- Section Hackathon -->
        <div class="hackathon-section">
            <div class="hackathon-content">
                <h2 class="hackathon-title">Hackathon Organisé par Kaikai</h2>
                <p class="hackathon-subtitle">
                    Un défi d'innovation pour améliorer la qualité de l'air dans les écoles sénégalaises
                </p>
                <div class="objectives-grid">
                    <div class="objective-card">
                        <span class="objective-icon">🎯</span>
                        <h3 class="objective-title">Objectif</h3>
                        <p class="objective-text">
                            Développer des solutions concrètes pour améliorer la qualité de l'air 
                            dans les établissements scolaires du Sénégal.
                        </p>
                    </div>
                    <div class="objective-card">
                        <span class="objective-icon">💡</span>
                        <h3 class="objective-title">Innovation</h3>
                        <p class="objective-text">
                            Technologies de pointe basées sur l'IoT, l'analyse de données 
                            et l'intelligence artificielle adaptées au contexte local.
                        </p>
                    </div>
                    <div class="objective-card">
                        <span class="objective-icon">🌍</span>
                        <h3 class="objective-title">Impact</h3>
                        <p class="objective-text">
                            Protection de la santé de milliers d'enfants et création 
                            d'environnements d'apprentissage plus sains.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        <!-- Témoignage -->
        <div class="content-section">
            <div class="testimonial-section">
                <div class="testimonial-card">
                    <p class="testimonial-text">
                        Kaikai a organisé ce hackathon pour rassembler l'écosystème d'innovation sénégalais 
                        autour d'un enjeu majeur de santé publique. Nous sommes fiers de participer avec notre 
                        projet RESPiRE qui illustre cette synergie entre technologie, engagement social et impact environnemental.
                    </p>
                </div>
            </div>
        </div>
        <!-- Call to Action -->
        <div class="content-section">
            <div class="cta-section">
                <div class="cta-content">
                    <h3 class="cta-title">Merci Kaikai !</h3>
                    <p class="cta-text">
                        Nous remercions sincèrement Kaikai pour avoir organisé ce hackathon 
                        et pour leur accompagnement exceptionnel. Leur engagement en faveur de 
                        l'innovation durable nous inspire et nous motive à donner le meilleur de nous-mêmes.
                    </p>
                    <a href="https://www.kaikai.dev" target="_blank" class="cta-button">
                        Découvrir Kaikai
                    </a>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


