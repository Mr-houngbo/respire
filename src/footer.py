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
            background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 50%, #f5f9fc 100%);
            padding: 2rem 2rem 1.5rem 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 -3px 15px rgba(52, 152, 219, 0.1);
            margin-top: 2rem;
            margin-bottom: 0;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
            margin-right: calc(-50vw + 50%);
        }
        
        .footer-header {
            text-align: center;
            margin-bottom: 2rem;
            color: #2c3e50;
        }
        
        .footer-logo {
            font-size: 2.5rem;
            font-weight: 700;
            color: #3498db;
            margin-bottom: 0.5rem;
            letter-spacing: 2px;
        }
        
        .footer-tagline {
            font-size: 1.1rem;
            opacity: 0.8;
            font-weight: 300;
            color: #5a6c7d;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 0rem;
        }
        
        .footer-card {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(52, 152, 219, 0.1);
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .footer-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.85);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.15);
        }
        
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 1rem;
            letter-spacing: 0.5px;
        }
        
        .card-content {
            color: #5a6c7d;
            line-height: 1.6;
            font-size: 0.9rem;
            font-weight: 400;
        }
        
        .card-content strong {
            color: #2c3e50;
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
            background: rgba(52, 152, 219, 0.1);
            color: #2c3e50;
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .tech-badge:hover {
            background: rgba(52, 152, 219, 0.2);
            transform: translateY(-1px);
        }
        
        .footer-link {
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .footer-link:hover {
            color: #2980b9;
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
                    <div class="card-title">Équipe</div>
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
                            <span class="tech-badge">AirGradient API</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer-card">
                    <div class="card-title">Code</div>
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
    components.html(footer_html, height=398)

