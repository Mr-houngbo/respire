import streamlit as st
from src.footer import show_footer
from components.autorite_ import *
from config.settings import token,sender
from src.prediction import *


def show(location_id,logo_path,nom_ecole): 


    # Recuperation des donnees actuelles 

    df = fetch_current_data(location_id, token)
    df = pd.DataFrame([df])
    iqa = calculer_iqa(df)

        
    st.markdown("""
            <div>
                <br>
            </div>""",unsafe_allow_html=True)
    # Bloc I AQI
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # Gauge AQI principal
        st.markdown(f"### Indice de la qualité de l'air (IQA)")
        st.plotly_chart(create_gauge_chart(iqa), use_container_width=True)
        
    with col2:
        #Description de l'aqi
        descript(iqa)
    
    show_line()
    
    # Bloc II Indicateurs cles actuels 
    
    show_air_status_summary(df,iqa)
    
    show_line()


    predict()


























#=========================== SECTION TOUT EN BAS RESERVEE AU FOOTER =================================

# show_footer()