import streamlit as st
import streamlit.components.v1 as components

def show_sensibilisation_page():
    
    st.markdown("""
    <style>
        body { font-family: 'Segoe UI', sans-serif; }
        h1, h2, h3, h4 { font-weight: 600; }
        .video-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .video-card { transition: all 0.2s ease; }
        .stat-card { 
            text-align: center; 
            padding: 1.5rem; 
            border-radius: 8px; 
            background: linear-gradient(135deg, #f8fdf8 0%, #f1f8f1 100%);
            border: 1px solid #d4edda;
            color: #495057;
            border-left: 4px solid #28a745;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #155724;
            margin: 0;
        }
        .stat-label {
            font-size: 0.9rem;
            color: #6c757d;
            margin: 0.5rem 0 0 0;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        padding: 2.5rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    ">
        <h1 style="font-size: 2.2rem; color: #2c3e50; margin: 0 0 1rem 0;">Sensibilisation & Éducation</h1>
        <p style="font-size: 1.1rem; color: #6c757d; margin: 0; line-height: 1.5;">
            Revivez nos moments forts dans les écoles et découvrez comment nous agissons pour un air plus sain
        </p>
    </div>
    """, unsafe_allow_html=True)

    # STATS
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('''
        <div class="stat-card">
            <div class="stat-number">6</div>
            <div class="stat-label">Vidéos produites</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown('''
        <div class="stat-card">
            <div class="stat-number">5</div>
            <div class="stat-label">Écoles partenaires</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col3:
        st.markdown('''
        <div class="stat-card">
            <div class="stat-number">300+</div>
            <div class="stat-label">Élèves sensibilisés</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    
    
    
    # VIDEOS DATA
    videos_data = [
        {"title": "Installation des capteurs IoT - École de Yoff", "type": "Installation", "duration": "8:24", "views": "1,2K", "thumbnail": "assets/thumbnails/yoff_install.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Atelier Élèves - Comprendre la pollution", "type": "Sensibilisation", "duration": "12:15", "views": "856", "thumbnail": "assets/thumbnails/thies_atelier.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Témoignages Enseignants", "type": "Témoignages", "duration": "6:42", "views": "634", "thumbnail": "assets/thumbnails/liberte_temoignages.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Analyse temps réel avec les élèves", "type": "Activités élèves", "duration": "15:33", "views": "2,1K", "thumbnail": "assets/thumbnails/lycee_donnees.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Remise des Certificats Éco-Ambassadeurs", "type": "Événement", "duration": "20:17", "views": "3,4K", "thumbnail": "assets/thumbnails/ceremonie_certificats.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Formation des Directeurs", "type": "Formation", "duration": "18:45", "views": "1,8K", "thumbnail": "assets/thumbnails/formation_directeurs.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Formation des Directeurs", "type": "Formation", "duration": "18:45", "views": "1,8K", "thumbnail": "assets/thumbnails/formation_directeurs.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Formation des Directeurs", "type": "Formation", "duration": "18:45", "views": "1,8K", "thumbnail": "assets/thumbnails/formation_directeurs.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        {"title": "Formation des Directeurs", "type": "Formation", "duration": "18:45", "views": "1,8K", "thumbnail": "assets/thumbnails/formation_directeurs.jpg", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"}    ]

    # GRID DISPLAY AVEC PLAYER
    st.subheader(" Nos vidéos")
    for i in range(0, len(videos_data), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(videos_data):
                video = videos_data[i + j]
                with col:
                    components.html(f"""
                    <div class="video-card" style="
                        background:white;
                        border-radius:12px;
                        overflow:hidden;
                        margin-bottom:20px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    ">
                        <iframe 
                            width="100%" 
                            height="300" 
                            src="{video['url']}" 
                            title="{video['title']}" 
                            frameborder="0" 
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowfullscreen>
                        </iframe>
                        <div style="padding:10px;">
                            <h4 style="margin:0;font-size:1rem;">{video['title']}</h4>
                            <p style="margin:5px 0; font-size:0.85rem; color:#666;">{video['views']} • {video['type']}</p>
                        </div>
                    </div>
                    """, height=400)
