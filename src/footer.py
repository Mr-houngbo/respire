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
        padding-bottom: 380px !important;
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
            background: linear-gradient(135deg, #6c757d 0%, #868e96 50%, #adb5bd 100%);
            padding: 2rem 2rem 1.5rem 2rem;
            border-radius: 15px 15px 0 0;
            position: relative;
            overflow: hidden;
            box-shadow: 0 -5px 20px rgba(108, 117, 125, 0.2);
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
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 0rem;
        }
        
        .footer-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .footer-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }
        
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 1rem;
            letter-spacing: 0.5px;
        }
        
        .card-content {
            color: rgba(255, 255, 255, 0.9);
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
            margin-top: 0.5rem;
        }
        
        .tech-badge {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 12px;
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
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .footer-link:hover {
            color: #f8f9fa;
            text-decoration: none;
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
                    <div class="card-content">
                        Créé par <strong>Breath4Life</strong><br>
                        Dans le cadre du hackathon <a href="https://www.kaikai.dev" target="_blank" class="footer-link">Kaikai 2025</a>
                    </div>
                </div>
                
                <div class="footer-card">
                    <div class="card-title">Technologies</div>
                    <div class="card-content">
                        <div class="tech-stack">
                            <span class="tech-badge">Python</span>
                            <span class="tech-badge">Streamlit</span>
                            <span class="tech-badge">HTML/CSS</span>
                            <span class="tech-badge">Pandas</span>
                            <span class="tech-badge">AirGradient API</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer-card">
                    <div class="card-title">Code & Données</div>
                    <div class="card-content">
                        <a href="https://github.com/Mr-houngbo/respire/" target="_blank" class="footer-link">Repository GitHub</a><br>
                        Version <strong>2.0.0</strong>
                    </div>
                </div>
            </div>
        </div>

    </body>
    </html>
    """
    
    # Affichage avec st.components.v1.html
    components.html(footer_html, height=450)




