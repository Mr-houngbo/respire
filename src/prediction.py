# dashboard_prediction.py
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import joblib
import numpy as np
from config.settings import token,BASE_URL,VALEURS_LIMITE,DATA_DIR,location_ids


DATA_DIR = "data"
location_id = 164928

API_TO_MODEL_COLS = {
    'pm02_corrected': 'PM2.5 (μg/m³) corrected',
    'pm10_corrected': 'PM10 (μg/m³)',
    'rco2_corrected': 'CO2 (ppm) corrected',
    'pm003Count' : '0.3μm particle count',
    'atmp_corrected': 'Temperature (°C) corrected',
    'rhum_corrected': 'Humidity (%) corrected',
    'tvoc': 'TVOC (ppb)',
    'noxIndex': 'NOX index',
    'pm01_corrected': 'PM1 (μg/m³)',
    'tvocIndex': 'TVOC index',
    
}

# ==== 1. Chargement du modèle et scalers ====
model = joblib.load("models/xgboost_multioutput.pkl")
scaler_X = joblib.load("models/scaler_X.pkl")
scaler_y = joblib.load("models/scaler_y.pkl")
target_columns = joblib.load("models/target_columns.pkl")
n_lags = joblib.load("models/n_lags.pkl")


def predict_j_plus_1(last_days_df):
    
    if last_days_df.empty:
        raise ValueError("Les données d'entrée pour la prédiction sont vides. Vérifiez la récupération des données.")
   
    if len(last_days_df) != n_lags:
        raise ValueError(f"Il faut exactement {n_lags} jours d'historique.")

    # On s'assure que toutes les colonnes cibles sont présentes
    for col in target_columns:
        if col not in last_days_df.columns:
            last_days_df[col] = np.nan  # ou 0 si tu préfères

    # On garde l'ordre des colonnes comme dans target_columns
    last_days_df = last_days_df[target_columns]

    # Construction des features et noms de features
    features = []
    for i in range(n_lags, 0, -1):
        features.extend(last_days_df.iloc[-i].values)

    feature_names = []
    for i in range(n_lags, 0, -1):
        feature_names.extend([f"{col}(t-{i})" for col in target_columns])

    features_df = pd.DataFrame([features], columns=feature_names)
    features_scaled = scaler_X.transform(features_df)
    pred_scaled = model.predict(features_scaled)
    pred = scaler_y.inverse_transform(pred_scaled)

    return pd.DataFrame(
        pred,
        columns=target_columns,
        index=[last_days_df.index[-1] + pd.Timedelta(days=1)]
    )


def get_last_n_lags(location_id: int, token: str) -> pd.DataFrame:
    """
    Récupère les n_lags dernières lignes formatées pour la prédiction J+1.
    """
    
    # Dates pour la requête API
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=n_lags + 2)  # marge pour s'assurer d'avoir n_lags jours complets

    # API request
    base_url = "https://api.airgradient.com/public/api/v1/locations"
    url = f"{base_url}/{location_id}/measures/past"
    params = {
        "token": token,
        "from": from_date.strftime('%Y%m%dT%H%M%SZ'),
        "to": to_date.strftime('%Y%m%dT%H%M%SZ'),
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Erreur API : {response.status_code}")

    # Conversion en DataFrame
    data = response.json()
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    
    
    cols_a_supprimer = [
    "locationId",
    "locationName",
    "serialno",
    "model",
    "pm01",
    "pm02",
    "pm10",
    "atmp",
    "rhum",
    "rco2",
    "wifi",
    "datapoints",
    "firmwareVersion",
    "longitude",
    "latitude"]
    
    df.drop(columns=cols_a_supprimer, inplace=True, errors='ignore')
    
    
    # Groupby par jour (moyenne des valeurs de chaque jour)
    df_daily = df.groupby('date').mean(numeric_only=True)
    # On garde la date comme index
    df_daily.index = pd.to_datetime(df_daily.index)
    
    # Renommage des colonnes API vers celles attendues par le modèle
    df_daily = df_daily.rename(columns=API_TO_MODEL_COLS)
    
    available_cols = [col for col in target_columns if col in df_daily.columns]
    df_daily = df_daily[available_cols]
    
    # On ne garde que les colonnes cibles
    
    # On ne garde que les n_lags derniers jours
    df_last = df_daily.tail(n_lags)

    # Index = datetime
    df_last.index.name = 'timestamp'
    
    

    # Sauvegarde optionnelle
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, f"last-{n_lags}-jours-{location_id}.csv")
    df_last.to_csv(file_path)

    return df_last


def predict():
    st.title("Prédiction de la qualité de l'air J+1")
    st.markdown("Ce dashboard permet de prédire la qualité de l'air pour le jour suivant (J+1) en utilisant les données des derniers jours.")

    # Récupération des dernières données
    
    last_days_df = get_last_n_lags(location_id, token)
    prediction_df = predict_j_plus_1(last_days_df)

    with st.expander(" Données utilisées", expanded=False):        
        st.dataframe(last_days_df)

    st.subheader(" Prédictions J+1")
    st.dataframe(prediction_df.style.format("{:.2f}"))




# Fonction pour recuperer les donnees et creer les dataframes pour le calcul des IQA

DATA_DIR = "data/air_quality"
#=============================================================================================================
@st.cache_data(ttl=300)
def get_measures_range(location_id: int, token: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    """
    Récupère les données pour un `location_id` donné entre from_date et to_date (max 10 jours API).
    """
    base_url = "https://api.airgradient.com/public/api/v1/locations"
    url = f"{base_url}/{location_id}/measures/past"

    params = {
        "token": token,
        "from": from_date.strftime('%Y%m%dT%H%M%SZ'),
        "to": to_date.strftime('%Y%m%dT%H%M%SZ'),
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    else:
        st.error(f"Erreur API : {response.status_code} pour location {location_id}")
        return pd.DataFrame()

#=============================================================================================================
def get_full_history(location_id: int, token: str, days: int = 100) -> pd.DataFrame:
    """
    Récupère toutes les données d'une location_id sur 'days' jours,
    en faisant des requêtes API par tranches de 10 jours.
    """
    all_data = []
    to_date = datetime.utcnow()

    while days > 0:
        chunk_days = min(days, 10)
        from_date = to_date - timedelta(days=chunk_days)

        df_chunk = get_measures_range(location_id, token, from_date, to_date)
        if df_chunk.empty:
            break

        all_data.append(df_chunk)
        days -= chunk_days
        to_date = from_date  # on recule la fenêtre

    if all_data:
        df_full = pd.concat(all_data, ignore_index=True).drop_duplicates()
        file_path = os.path.join(DATA_DIR, f"full-data-{days}-jours-{location_id}.csv")
        df_full.to_csv(file_path, index=False)
        return df_full
    else:
        return pd.DataFrame()

#=============================================================================================================
def calculer_iqa_journalier(df: pd.DataFrame, location_id: int) -> pd.DataFrame:
    """
    Calcule l’IQA journalier pour un DataFrame complet.
    """
    if df.empty:
        return pd.DataFrame()

    iqa_jours = []
    df['date'] = df['timestamp'].dt.date

    for jour, group in df.groupby('date'):
        valeurs = {}
        for pollutant, limite in VALEURS_LIMITE.items():
            if pollutant in group.columns:
                concentration = group[pollutant].mean()
                valeurs[pollutant] = (concentration / limite) * 100

        if valeurs:
            polluant_principal = max(valeurs, key=valeurs.get)
            iqa_principal = round(valeurs[polluant_principal], 2)
            iqa_jours.append({"date": jour, "iqa": iqa_principal})

    iqa_tab = pd.DataFrame(iqa_jours)
    file_path = os.path.join(DATA_DIR, f"iqa-{location_id}.csv")
    iqa_tab.to_csv(file_path, index=False)
    return iqa_tab

#=============================================================================================================
def pipeline_iqa(location_ids: list, token: str, days: int = 100) -> dict:
    """
    Exécute la récupération et le calcul IQA pour plusieurs location_ids.
    Retourne un dictionnaire {location_id: DataFrame IQA}.
    """
    resultats = {}
    for loc_id in location_ids:
        st.info(f" Récupération des données pour Location {loc_id}")
        df_full = get_full_history(loc_id, token, days)
        df_iqa = calculer_iqa_journalier(df_full, loc_id)
        resultats[loc_id] = df_iqa
    return resultats



# pipeline_iqa(location_ids, token, days=100)

