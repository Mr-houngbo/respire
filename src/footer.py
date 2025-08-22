import streamlit as st
import streamlit.components.v1 as components


def show_footer():
    
    # CSS pour fixer le footer en bas
    st.markdown("""
    <style>
    iframe[title="st.iframe"] {
    margin-bottom: 0 !important;
    }
    
    /* Padding pour éviter que le footer masque le contenu */
    .main .block-container {
        padding-bottom: 480px !important;
    }
    
    /* Supprimer le footer par défaut de Streamlit */
    .stApp > footer {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    footer_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: transparent;
            margin: 0;
            padding: 0;
        }
        
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
        }
        
        .footer-container {
            background: linear-gradient(135deg, #2E7D32 0%, #43A047 50%, #66BB6A 100%);
            padding: 2rem 2rem 1.5rem 2rem;
            border-radius: 15px 15px 0 0;
            position: relative;
            overflow: hidden;
            box-shadow: 0 -5px 20px rgba(27, 94, 32, 0.3);
            margin-top: 2rem;
            margin-bottom: 0;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
            margin-right: calc(-50vw + 50%);
        }
        
        .footer-header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }
        
        .footer-logo {
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
            letter-spacing: 2px;
        }
        
        .footer-tagline {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 0rem;
        }
        
        .footer-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .footer-card:hover {
            transform: translateY(-3px);
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }
        
        .card-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 1.2rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 0.5rem;
        }
        
        .card-subtitle {
            font-size: 1rem;
            font-weight: 600;
            color: #E8F5E8;
            margin: 1rem 0 0.5rem 0;
            text-transform: capitalize;
        }
        
        .card-content {
            color: rgba(255, 255, 255, 0.85);
            line-height: 1.6;
            font-size: 0.9rem;
            font-weight: 400;
        }
        
        .card-content strong {
            color: #ffffff;
            font-weight: 600;
        }
        
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .tech-badge {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .tech-badge:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }
        
        .footer-link {
            color: #ffffff;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .footer-link:hover {
            color: #E8F5E8;
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .footer-container {
                padding: 1.5rem;
            }
            .footer-logo {
                font-size: 2rem;
            }
            .footer-content {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            .footer-card {
                padding: 1.2rem;
            }
        }
        
        </style>
    </head>
    <body>
        <div>
            <br><br><br>
        </div>
            
        <div class="footer-container">
            <div class="footer-header">
                <div class="footer-logo">RESPIRE</div>
                <div class="footer-tagline">Dashboard de qualité de l'air dans les écoles</div>
            </div>
            <div class="footer-content">
                <div class="footer-card">
                    <div class="card-title">Équipe & Projet</div>
                    <div class="card-subtitle">Développeurs</div>
                    <div class="card-content">
                        Créé par <strong>Breath4Life</strong> Dans le cadre du hackathon de <a href="https://www.kaikai.dev" target="_blank" class="footer-link">Kaikai 2025</a>
                    </div>
                </div>
                
                <div class="footer-card">
                    <div class="card-title">Technologies</div>
                    <div class="card-subtitle">Frontend & Backend</div>
                    <div class="card-content">
                        <div class="tech-stack">
                            <span class="tech-badge">Python | Streamlit</span>
                            <span class="tech-badge">HTML/CSS</span>
                            <span class="tech-badge">JavaScript</span>
                        </div>
                    </div>
                    <div class="card-subtitle">Données & API</div>
                    <div class="card-content">
                        <div class="tech-stack">
                            <span class="tech-badge">Pandas</span>
                            <span class="tech-badge">AirGradient API</span>
                            <span class="tech-badge">JSON</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer-card">
                    <div class="card-title">Code & Données</div>
                    <div class="card-content">
                        <a href="https://github.com/Mr-houngbo/respire/" target="_blank" class="footer-link">Repository GitHub  | Version <strong>2.0.0</strong>  </a>
                    </div>
                </div>
            </div>
        </div>

    </body>
    </html>
    """
    
    # Affichage avec st.components.v1.html
    components.html(footer_html, height=480)

