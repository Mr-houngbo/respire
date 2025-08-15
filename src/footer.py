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
        padding-bottom: 520px !important;
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
            background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 30%, #43A047 70%, #66BB6A 100%);
            padding: 3rem 2rem 2rem 2rem;
            border-radius: 25px 25px 0 0;
            position: relative;
            overflow: hidden;
            box-shadow: 0 -10px 40px rgba(27, 94, 32, 0.4);
            margin-top: 2rem;
            margin-bottom: 0;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
            margin-right: calc(-50vw + 50%);
        }
        
        .footer-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #81C784, #A5D6A7, #C8E6C9, #81C784);
            background-size: 200% 100%;
            animation: wave 3s ease-in-out infinite;
        }
        
        @keyframes wave {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .footer-header {
            text-align: center;
            margin-bottom: 2.5rem;
            color: white;
        }
        
        .footer-logo {
            font-size: 3.2rem;
            font-weight: 900;
            background: linear-gradient(45deg, #E8F5E8, #FFFFFF, #F1F8E9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.8rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
            letter-spacing: 3px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 4px 8px rgba(0,0,0,0.3); }
            to { text-shadow: 0 4px 20px rgba(232, 245, 232, 0.4); }
        }
        
        .footer-tagline {
            font-size: 1.3rem;
            opacity: 0.95;
            font-weight: 300;
            letter-spacing: 1px;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 0rem;
        }
        
        .footer-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 25px;
            padding: 2.5rem 2rem;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .footer-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
            transition: left 0.6s;
        }
        
        .footer-card:hover::before {
            left: 100%;
        }
        
        .footer-card:hover {
            transform: translateY(-10px) scale(1.03);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
            background: rgba(255, 255, 255, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.4);
        }
       
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        .card-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #E8F5E8;
            margin-bottom: 1.5rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        
        .card-content {
            color: rgba(255, 255, 255, 0.95);
            line-height: 1.8;
            font-size: 1rem;
        }
        
        .card-content strong {
            color: #E8F5E8;
            font-weight: 600;
        }
        
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.8rem;
            margin-top: 1.5rem;
        }
        
        .tech-badge {
            background: rgba(255, 255, 255, 0.3);
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.4);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .tech-badge:hover {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(1.1) translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        
        .footer-link {
            color: #E8F5E8;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border-bottom: 2px solid transparent;
        }
        
        .footer-link:hover {
            color: white;
            border-bottom: 2px solid white;
            text-shadow: 0 0 15px rgba(255, 255, 255, 0.6);
            margin-bottom: 0rem !important;
        }
        
        @media (max-width: 768px) {
            .footer-container {
                padding: 2rem 1.5rem 1.5rem 1.5rem;
            }
            .footer-logo {
                font-size: 2.5rem;
            }
            .footer-tagline {
                font-size: 1.1rem;
            }
            .footer-content {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }
            .footer-card {
                padding: 2rem 1.5rem;
            }
            .card-icon {
                font-size: 2.5rem;
            }
        }
        iframe.stFrame { margin-bottom: 0 !important; padding-bottom: 0 !important; height: 140px !important; /* Ajuste selon la hauteur réelle de ton footer */ }
        
        </style>
    </head>
    <body>
        <div>
            <br><br><br><br><br>
        </div>
            
        <div class="footer-container">
            <div class="footer-header">
                <div class="footer-logo">RESPiRE</div>
                <div class="footer-tagline">Dashboard de qualité de l'air dans les écoles</div>
            </div>
            
            <div class="footer-content">
                <div class="footer-card">
                    <div class="card-title">Équipe & Projet</div>
                    <div class="card-content">
                        Créé avec passion par<br>
                        <strong>Breath4Life</strong><br><br>
                        Hackathon <a href="https://www.kaikai.dev" target="_blank" class="footer-link">Kaikai 2025</a><br><br>
                        <em>"Sensibiliser pour mieux respirer"</em>
                    </div>
                </div>
                
                <div class="footer-card">
                    <div class="card-title">Technologies</div>
                    <div class="card-content">
                        Stack technique moderne<br><br>
                        <div class="tech-stack">
                            <span class="tech-badge">Python</span>
                            <span class="tech-badge">Streamlit</span>
                            <span class="tech-badge">Pandas</span>
                            <span class="tech-badge">AirGradient</span>
                            <span class="tech-badge">CSS3</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer-card">
                    <div class="card-title">Code & Données</div>
                    <div class="card-content">
                        <strong>Capteurs temps réel</strong><br>
                        AirGradient API<br><br>
                        <a href="https://github.com/Mr-houngbo/respire/" target="_blank" class="footer-link">Code source GitHub</a><br><br>
                         Version <strong>1.0.0</strong>
                    </div>
                </div>
            </div>
           
        </div>

    </body>
    </html>
    """
    
    # Affichage avec st.components.v1.html
    components.html(footer_html, height=674)
    