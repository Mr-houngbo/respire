import streamlit as st
from components.ecole_ import *
from src.footer import show_footer
from config.settings import token,BASE_URL,VALEURS_LIMITE,location_ids,DATA_DIR,liens

location_id = location_ids[6]

  
def show():
    # Bloc I - Titre
    show_header(nom_ecole="ESMT - Dakar", logo_path="assets/images/logo_esmt.jpeg")
    
    # Bloc II - Qualité de l'air  -- Test effectuee avec ESMT comme location_id
    show_air_quality(location_id,token)
    # Aspect beaute de show_air_quality a revoir 
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
    
    # Bloc III
    show_animation("https://github.com/Mr-houngbo/respire/releases/download/v0.1-video/presentation.mp4")
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
     
    #BLOC IV
    show_daily_tips(location_id,token)
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

#=========================== SECTION TOUT EN BAS RESERVEE AU FOOTER =================================


# show_footer()
