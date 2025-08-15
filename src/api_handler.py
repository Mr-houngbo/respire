import requests
import os
import pandas as pd
from datetime import datetime
from urllib.parse import urlencode


#=============================================================================================================


#   🧱 Architecture du module api_handler.py

#  ✅ 2. Fonction : fetch_latest_data(location_id)
#  – Récupère la dernière donnée disponible pour une location , il s'agit de la donnee de la journee (Une aggregation de toutes les donnees collectees la journee , donc en fait c'est juste une seule ligne ).
#  – Utilise :
#  GET /public/api/v1/locations/{location_id}/measures/current
#  → Elle sera utilisée chaque jour a 23h59 pour recuperer les donnees de la journee .

#  ✅ 3. Fonction : append_new_data(location_id)
#  – Compare la dernière ligne enregistrée localement avec les nouvelles données de l’API.
#  – Si nouvelle, ajoute au fichier CSV de la location dans /data.

#  ✅ 4. Fonction : save_data_to_csv(data, location_id)
#  – Enregistre ou met à jour un fichier CSV contenant toutes les données de cette location.

#=============================================================================================================


BASE_URL = "https://api.airgradient.com/public/api/v1"
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data/now')

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

def save_data_to_csv(df: pd.DataFrame, location_id: str):
    """
    Sauvegarde un DataFrame dans un fichier CSV nommé selon la location.
    Écrase le fichier s’il existe déjà.
    """
    
    file_path = os.path.join(DATA_DIR, f"{location_id}.csv")
    df.to_csv(file_path, index=False)

#=============================================================================================================

def fetch_latest_data(location_id: str, token: str) -> pd.DataFrame:
    """
    Récupère la donnée journalière agrégée (bucketSize=1day) pour aujourd'hui à partir de l'endpoint /measures/past.
    """

    endpoint = f"/locations/{location_id}/measures/past"

    today = datetime.utcnow().strftime("%Y-%m-%d")
    from_param = f"{today}T00:00:00Z"
    to_param = f"{today}T23:59:59Z"

    params = {
        "token": token,
        "from": from_param,
        "to": to_param
    }

    full_url = f"{BASE_URL}{endpoint}?{urlencode(params)}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()

        return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la donnée journalière pour {location_id} : {e}")
        return pd.DataFrame()


#=============================================================================================================

def append_new_data(location_id: str, new_data: dict):
    """
    Ajoute les nouvelles données (dict) au fichier CSV existant pour la location,
    uniquement si elles ne sont pas déjà présentes (basé sur le timestamp).
    """
    
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

def generate_daily_summary(location_id, file_path):
    try:
        # Vérifie si le fichier existe et n'est pas vide
        if os.path.getsize(file_path) == 0:
            print(f"[⚠️] Fichier vide ignoré : {file_path}")
            return

        df = pd.read_csv(file_path)

        if df.empty:
            print(f"[⚠️] Aucune donnée dans le fichier : {file_path}")
            return

        # Filtrer les données par locationId
        df = df[df['locationId'] == location_id]

        if df.empty:
            print(f"[⚠️] Aucune donnée pour locationId={location_id} dans {file_path}")
            return

        # Colonnes fixes à conserver
        categorical_cols = df.select_dtypes(include='object').columns
        numerical_cols = df.select_dtypes(include='number').columns.difference(categorical_cols)

        # Moyenne des colonnes numériques
        mean_values = df[numerical_cols].mean()
        constant_values = df[categorical_cols].iloc[0]

        # Fusion et export
        result = pd.concat([constant_values, mean_values]).to_frame().T
        output_filename = f"{location_id}.csv"
        result.to_csv(output_filename, index=False)

        print(f"[✅] Moyenne journalière exportée dans : {output_filename}")

    except pd.errors.EmptyDataError:
        print(f"[⚠️] Fichier vide (aucune colonne) : {file_path}")
    except FileNotFoundError:
        print(f"[❌] Fichier introuvable : {file_path}")
    except Exception as e:
        print(f"[❌] Erreur inattendue pour {file_path} : {e}")
