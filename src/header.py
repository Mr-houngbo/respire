import streamlit as st
from components.calculer_iqa import calculer_iqa
import pandas as pd
import os
from urllib.parse import urlencode
import requests
from datetime import datetime
import random


# Version un peu plus pro 

def show_header_playful():
    """
    Header professionnel, épuré et moderne
    """
    st.markdown("""
    <style>
    .professional-header {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 0 0 12px 12px;
        padding: 1rem 2rem;
        margin: 2rem 2rem 2rem -1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .header-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #4ade80;
        margin: 0;
        text-align: center;
        letter-spacing: -0.02em;
    }
    
    .header-subtitle {
        font-size: 1rem;
        color: #6c757d;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('''
        <div class="professional-header">
            <h1 class="header-title">
                RESPIRE Dashboard
            </h1>
        </div>
        ''', unsafe_allow_html=True)
        
        
        

#=============================================================================================================
