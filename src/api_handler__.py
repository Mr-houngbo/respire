# ANCIENNE VERSION DU API_HANDLER

import requests
import os
import pandas as pd
import datetime
from urllib.parse import urlencode

#   🧱 Architecture du module api_handler.py
#  ✅ 1. Fonction : fetch_historical_data(location_id, start_date, end_date)
#  – Récupère toutes les données collectées par le capteur sur la période définie.
#  – Utilise l’endpoint :
#  GET /public/api/v1/locations/{location_id}/measures/past?from={start}&to={end}

#  ✅ 2. Fonction : fetch_latest_data(location_id)
#  – Récupère la dernière donnée disponible pour une location.
#  – Utilise :
#  GET /public/api/v1/locations/{location_id}/measures/current
#  → Elle sera utilisée à intervalle régulier (via un cron local ou Streamlit autorefresh).

#  ✅ 3. Fonction : append_new_data(location_id)
#  – Compare la dernière ligne enregistrée localement avec les nouvelles données de l’API.
#  – Si nouvelle, ajoute au fichier CSV de la location dans /data.

#  ✅ 4. Fonction : save_data_to_csv(data, location_id)
#  – Enregistre ou met à jour un fichier CSV contenant toutes les données de cette location.

#  ✅ 5. Optionnel (plus tard) : process_data(location_id)
#  – Prépare les données pour le dashboard (agrégations, nettoyages, etc.)

#=============================================================================================================


BASE_URL = "https://api.airgradient.com/public/api/v1"
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

#=============================================================================================================


def ping_server():
    """Teste la connexion à l’API AirGradient."""
    url = f"{BASE_URL}/ping"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la connexion à l'API : {e}")
        return False

#=============================================================================================================



def fetch_historical_data(location_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Récupère les données historiques d'un capteur AirGradient pour une période donnée.
    
    start_date et end_date doivent être au format 'YYYY-MM-DD'
    """
#    url = f"{BASE_URL}/locations/{location_id}/measures/past"
    url = f"{BASE_URL}/locations/{location_id}/measures/raw"

    params = {
        "from": f"{start_date}T00:00:00Z",
        "to": f"{end_date}T23:59:59Z",
        "token": "2122a271-e910-4ad8-acb8-5a24e764499b"
    }

    full_url = f"{url}?{urlencode(params)}"
    
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()
        
        print(response.json())
        
        # Convertir la liste en DataFrame
        df = pd.DataFrame(data)

    #   df = pd.DataFrame(data.get("measurements", []))
        return df
    
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données pour {location_id} : {e}")
        return pd.DataFrame()





#=============================================================================================================

def save_data_to_csv(df: pd.DataFrame, location_id: str):
    """
    Sauvegarde un DataFrame dans un fichier CSV nommé selon la location.
    Écrase le fichier s’il existe déjà.
    """
    file_path = os.path.join(DATA_DIR, f"{location_id}.csv")
    df.to_csv(file_path, index=False)

#=============================================================================================================


def fetch_latest_data(location_id: str) -> dict:
    """
    Récupère la dernière mesure disponible pour une location spécifique via l'API AirGradient.
    """
    url = f"{BASE_URL}/locations/{location_id}/measures/current"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        
        measurements = data.get("measurements", [])
        return measurements[0] if measurements else {}

#       return data.get("measurements", [{}])[0]  # retourne un dictionnaire  ----- Ceci est une alternative au deux lignes precedentes  . Si elles ne fonctionne pas , veuilllez decommenter ceci !

    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la dernière mesure pour {location_id} : {e}")
        return {}

#=============================================================================================================



def append_new_data(location_id: str, new_data: dict):
    """
    Ajoute les nouvelles données (dict) au fichier CSV existant pour la location,
    uniquement si elles ne sont pas déjà présentes (basé sur le timestamp).
    """
    import pandas as pd
    import os

    file_path = os.path.join(DATA_DIR, f"{location_id}.csv")

    # Charger l'ancien CSV s'il existe
    if os.path.exists(file_path):
        df_old = pd.read_csv(file_path)
    else:
        df_old = pd.DataFrame()

    # Convertir la nouvelle donnée en DataFrame
    df_new = pd.DataFrame([new_data])

    # Vérifier si le timestamp est déjà présent
    if not df_old.empty and 'timestamp' in df_old.columns and new_data.get("timestamp") in df_old["timestamp"].values:
        print("ℹ️ Donnée déjà présente, pas d'ajout.")
        return

    # Ajouter et sauvegarder
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    df_combined.to_csv(file_path, index=False)


#=============================================================================================================
