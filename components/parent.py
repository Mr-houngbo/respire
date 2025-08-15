import streamlit as st
from components.parent_ import *

def show():
    """Fonction principale pour afficher la page parents"""
    show_header(nom_ecole="ESMT - Dakar",logo_path="assets/images/logo_esmt.jpeg")
    
    show_air_status_summary()
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
    
    show_health_parameters()

    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
    
    # render_bloc_tendances()
    graphique_iqa(location_id,token)
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
    
    # render_bloc_conseils()
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
    
    
    
    show_sms_sytem()
    
    st.markdown("""
            <div>
                <br><br><br><br><br>
            </div>""",unsafe_allow_html=True)
    
    show_whatsapp_system()
    
# Test de la fonction
if __name__ == "__main__":
    show()



































#=========================== SECTION TOUT EN BAS RESERVEE AU FOOTER =================================

# show_footer()