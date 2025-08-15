import streamlit as st
from components.calculer_iqa import calculer_iqa
import pandas as pd
import os
from urllib.parse import urlencode
import requests
from datetime import datetime
import random


# Version alternative encore plus ludique (optionnelle)
def show_header_playful():
    """
    Version encore plus ludique avec effet de bulles et couleurs vives
    """
    st.markdown("""
    <style>
    .playful-header {
        background: linear-gradient(45deg, #81c784, #aed581, #c5e1a5, #dcedc8);
        border-radius: 25px;
        padding: 30px;
        margin-top:20px;
        margin-bottom: 0px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(129, 199, 132, 0.3);
    }
    
    .playful-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 20px 20px;
        animation: bubble-move 20s linear infinite;
    }
    
    @keyframes bubble-move {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(-20px, -20px) rotate(360deg); }
    }
    
    .title-playful {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(45deg, #1b5e20, #2e7d32, #388e3c, #4caf50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        position: relative;
        z-index: 1;
    }
    
    .breathing-text {
        animation: breathe 2s ease-in-out infinite;
    }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="playful-header">', unsafe_allow_html=True)
        
        st.markdown(
            """
            <div class="title-playful breathing-text">
                🌈 RESPIRE - Ton Super Dashboard ! 🌈
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
#=============================================================================================================