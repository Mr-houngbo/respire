import streamlit as st
import pandas as pd
import os
from urllib.parse import urlencode
import requests
from datetime import datetime

# Valeurs limites (à ajuster selon normes locales)
VALEURS_LIMITE = {
    "rco2_corrected": 1000,    # ppm - Qualité d'air intérieur acceptable
    "tvoc": 500,               # µg/m³ - Limite indicative pour COV
    "pm01_corrected": 15,      # µg/m³ - PM1 (proche de PM2.5 mais plus stricte)
    "pm02_corrected": 25,      # µg/m³ - PM2.5 (norme OMS)
    "pm10_corrected": 50,      # µg/m³ - PM10 (norme OMS)
    "noxIndex": 100       # µg/m³ - Limite pour NOx
}

#=============================================================================================================

BASE_URL = "https://api.airgradient.com/public/api/v1"
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data/now')
token = "77a25676-a9ec-4a99-9137-f33e6776b590"

#=============================================================================================================

def fetch_current_data(location_id: str, token: str) -> pd.DataFrame:
    """
    Récupère la mesure  actuelle à partir de l'endpoint /measures/current.
    """

    endpoint = f"/locations/{location_id}/measures/current"
    
    params = {
        "token": token
    }

    full_url = f"{BASE_URL}{endpoint}?{urlencode(params)}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()

        # Vérification du format de réponse
        if isinstance(data, dict):
            # Si les mesures sont directement dans "measures"
            if "measures" in data:
                return pd.DataFrame([data["measures"]])  # ✅ Encapsulation dans une liste
            else:
                return pd.DataFrame([data])  # ✅ On transforme le dict en DataFrame ligne unique
        elif isinstance(data, list):
            return pd.DataFrame(data)  # Si API renvoie déjà une liste d'objets

        print(f"⚠️ Format inattendu de la réponse API pour {location_id} : {data}")
        return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau pour {location_id} : {e}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"❌ Erreur lors du parsing JSON pour {location_id} : {e}")
        return pd.DataFrame()
#=============================================================================================================

def calculer_iqa(df: pd.DataFrame):
    """
    Calcule l'IQA global de l'école à partir du df des données actuelles obtenues plus haut.
    :param df : Le DataFrame des données courantes de l'école
    :return: dict avec 'iqa_principal', 'polluant_principal', 'iqa_moyen'
    """

    # Calculer l'IQA pour chaque polluant
    iqa_values = {}
    for pollutant, limite in VALEURS_LIMITE.items():
        if pollutant in df.columns:
            concentration = df[pollutant].mean()  # moyenne du polluant
            iqa_values[pollutant] = (concentration / limite) * 100

    if not iqa_values:
        st.error("❌ Aucun polluant valide trouvé dans le fichier.")
        return None

    # Polluant le plus critique
    pollutant_principal = max(iqa_values, key=iqa_values.get)
    iqa_principal = iqa_values[pollutant_principal]

    # Moyenne des IQA
    iqa_moyen = sum(iqa_values.values()) / len(iqa_values)

    return {
        "iqa_principal": round(iqa_principal, 2),
        "polluant_principal": pollutant_principal,
        "iqa_moyen": round(iqa_moyen, 2)
    }


#=============================================================================================================
location_id = "164928"
token = "77a25676-a9ec-4a99-9137-f33e6776b590"


print(f" IQA = {calculer_iqa(fetch_current_data(location_id,token))}")







































"""
def calculer_iqa(df: pd.DataFrame):
    Calcule l'IQA global de l'école à partir de son fichier CSV.
    :param location_id: ID de l'école (sert à récupérer le CSV)
    :return: (iqa, polluant_principal)
    file_path = f"{DATA_DIR}/{location_id}.csv"

    if not os.path.exists(file_path):
        st.error(f"❌ Données introuvables pour l'école {location_id}")
        return None, None

    df = pd.read_csv(file_path)

    # Calculer l'IQA pour chaque polluant
    iqa_values = {}
    for pollutant, limite in VALEURS_LIMITE.items():
        if pollutant in df.columns:
            concentration = df[pollutant].mean()  # moyenne du polluant
            iqa_values[pollutant] = (concentration / limite) * 100

    if not iqa_values:
        st.error("❌ Aucun polluant valide trouvé dans le fichier.")
        return None, None

    # Prendre le polluant le plus critique (plus grand IQA)
    pollutant_principal = max(iqa_values, key=iqa_values.get)
    iqa = iqa_values[pollutant_principal]

    return round(iqa), pollutant_principal
"""