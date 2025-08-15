import streamlit as st
import streamlit.components.v1 as components

def show_sensibilisation_page():
    st.markdown("""
    <style>
        body { font-family: 'Segoe UI', sans-serif; }
        h1, h2, h3, h4 { font-weight: 700; }
        .video-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.15); }
        .video-card { transition: all 0.3s ease; }
        .stat-card { text-align: center; padding: 15px; border-radius: 12px; color: white; }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1976d2, #42a5f5);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
    ">
        <h1 style="font-size: 3rem;"> Sensibilisation & Éducation</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">
            Revivez nos moments forts dans les écoles et découvrez comment nous agissons pour un air plus sain
        </p>
    </div>
    """, unsafe_allow_html=True)

    # STATS
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-card" style="background:#4caf50;"><h2>6</h2><p>Vidéos produites</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card" style="background:#2196f3;"><h2>5</h2><p>Écoles partenaires</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card" style="background:#ff9800;"><h2>300+</h2><p>Élèves sensibilisés</p></div>', unsafe_allow_html=True)
    

    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)


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
