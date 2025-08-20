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
import warnings
warnings.filterwarnings("ignore")


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



def compute_heat_index(temp_c, rh):
    """
    Calcule le Heat Index (°C) à partir de la température (°C) et de l'humidité relative (%).
    """
    # conversion °C -> °F
    T = (temp_c * 9/5) + 32
    R = rh

    HI = (-42.379 + 2.04901523*T + 10.14333127*R
          - 0.22475541*T*R - 0.00683783*T*T - 0.05481717*R*R
          + 0.00122874*T*T*R + 0.00085282*T*R*R - 0.00000199*T*T*R*R)

    # reconversion en °C
    return (HI - 32) * 5/9



def predict_j_plus_1(last_days_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prédit les valeurs du jour suivant à partir des n_lags derniers jours.
    last_days_df : DataFrame avec exactement n_lags jours, colonnes = target_columns
    """
    if last_days_df.empty:
        raise ValueError("Les données d'entrée sont vides.")

    # Construction des features
    features, feature_names = [], []
    for i in range(n_lags, 0, -1):
        features.extend(last_days_df.iloc[-i].values)
        feature_names.extend([f"{col}(t-{i})" for col in target_columns])

    features_df = pd.DataFrame([features], columns=feature_names)

    # Scaling et prédiction
    features_scaled = scaler_X.transform(features_df)
    pred_scaled = model.predict(features_scaled)
    pred = scaler_y.inverse_transform(pred_scaled)

    # Index = dernier jour + 1
    last_date = pd.to_datetime(last_days_df.index[-1])
    next_date = last_date + pd.Timedelta(days=1)

    return pd.DataFrame(pred, columns=target_columns, index=[next_date])

   
def get_last_n_lags(location_id: int, token: str, n_lags: int = None) -> pd.DataFrame:
    
    """
    Récupère les n_lags dernières lignes formatées pour la prédiction J+1.
    """
    
    if n_lags is None:
        n_lags = joblib.load("models/n_lags.pkl")

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
    df_daily = df_daily.dropna()  # supprime les jours incomplets

    # On garde la date comme index
    df_daily.index = pd.to_datetime(df_daily.index)
    
    #file_path = os.path.join(DATA_DIR, f"Donnees brutes par jour for -{location_id}.csv")  it was pour voir les donnees et colonnes recues de l'api
    #df_daily.to_csv(file_path)  
    
     
    # Renommage des colonnes API vers celles attendues par le modèle
    df_daily = df_daily.rename(columns=API_TO_MODEL_COLS)
    
    available_cols = [col for col in target_columns if col in df_daily.columns]
    df_daily = df_daily[available_cols]
    
    # On ne garde que les colonnes cibles
    
    # On ne garde que les n_lags derniers jours
    df_last = df_daily.tail(n_lags)

    # Index = datetime
    df_last.index.name = 'timestamp'
    
        
    if len(df_last) != n_lags:
        raise ValueError(f"Il faut exactement {n_lags} jours d'historique (actuel = {len(last_days_df)}).")

    # S'assurer que toutes les colonnes sont présentes
    for col in target_columns:
        if col not in df_last.columns:
            df_last[col] = 0

    # Réordonner les colonnes
    df_last = df_last[target_columns]

    # === Après ton groupby/join sur df_daily ===
    if "Temperature (°C) corrected" in df_last.columns and "Humidity (%) corrected" in df_last.columns:
        df_last["Heat Index (°C)"] = df_last.apply(
            lambda row: compute_heat_index(row["Temperature (°C) corrected"], row["Humidity (%) corrected"]),
            axis=1
        )
    
    # Remplir les valeurs manquantes éventuelles
    df_last = df_last.interpolate().bfill().ffill()
    
    # Sauvegarde optionnelle
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, f"last-{n_lags}-jours-{location_id}.csv")
    df_last.to_csv(file_path)
    

    return df_last


def predict():
    st.title("Prédiction de la qualité de l'air J+1")
    st.markdown("Ce dashboard permet de prédire la qualité de l'air pour le jour suivant (J+1) en utilisant les données des derniers jours.")

    # Récupération des dernières données
    
    last_days_df = get_last_n_lags(location_id,token,n_lags)
    prediction_df = predict_j_plus_1(last_days_df)

    with st.expander(" Données utilisées", expanded=False):        
        st.dataframe(last_days_df)

    st.subheader(" Prédictions J+1")
    st.dataframe(prediction_df.style.format("{:.2f}"))





# Fonction pour recuperer les donnees et creer les dataframes pour le calcul des IQA
# Il s'agitde s fonctions que j'avais utilise pour creer les dataframes au debut pour demarrer les predictions
# Actuellement utilisees  pour la predictionj+1 de l'iqa de l'ESMT 


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

#=============================================================================================================
#==============================================================================================================

#                                                  SECTION PREDICTION IQA J+1 (SUPPRIMÉE DEFINITIVEMENT )
#=============================================================================================================
#=============================================================================================================


#=============================================================================================================
#=============================================================================================================

#                                                  SECTION COMPREHENSION PREDICTION J+1 DES POLLUANTS 
#=============================================================================================================
#=============================================================================================================

DATA_DIR = "data"

#=============================================================================================================
@st.cache_data(ttl=60)  # expire au bout de 1 minute
def get_last_days_aggregated(location_id: int, token: str, n_lags: int = 5) -> pd.DataFrame:
    """
    Récupère les données brutes (5 min) des 7 derniers jours via l'API,
    les agrège par jour, et retourne exactement n_lags jours sous forme de DataFrame
    (colonnes = target_columns utilisées pour le modèle).
    """
    base_url = "https://api.airgradient.com/public/api/v1/locations"
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=7)

    url = f"{base_url}/{location_id}/measures/past"
    params = {
        "token": token,
        "from": from_date.strftime('%Y%m%dT%H%M%SZ'),
        "to": to_date.strftime('%Y%m%dT%H%M%SZ'),
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error(f"Erreur API : {response.status_code}")
        return pd.DataFrame()

    # === 1. Convertir en DataFrame
    data = response.json()
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Sauvegarde brute
    file_path = os.path.join(DATA_DIR, f"data-7-jours-{location_id}.csv")
    df.to_csv(file_path, index=False)

    # === 2. Agrégation par jour
    df.set_index("timestamp", inplace=True)

    # moyenne journalière
    daily_df = df.resample("D").mean()

    # === 3. Garder uniquement les colonnes utiles
    target_columns = joblib.load("target_columns.pkl")
    daily_df = daily_df[target_columns]

    # === 4. Supprimer les jours incomplets si NaN
    daily_df = daily_df.dropna()

    # === 5. Ne garder que les n_lags derniers jours
    last_days = daily_df.tail(n_lags)

    return last_days
#=============================================================================================================
#=============================================================================================================






#=============================================================================================================
#                                                  SECTION AMELIORATION  PREDICTION J+1 A J+5 IQA 
#=============================================================================================================



# predict_pipeline.py

import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# ================== 1) Charger le modèle entraîné ==================
MODEL_PATH = "models/xgb_iqa_all_features.pkl"
model_ = joblib.load(MODEL_PATH)
FEATURES = joblib.load("models/features.pkl")


# Colonnes utiles à garder (adapter si besoin)
COLS_TO_DROP = [
    "Location ID", "Location Name", "Location Group", "Location Type",
    "Sensor ID", "Place Open", "UTC Date/Time", "# of aggregated records"
]


# ================== 2) Préparation des données ==================
def prepare_data(df_iqa: pd.DataFrame, df_polluants: pd.DataFrame) -> pd.DataFrame:
    """
    Merge IQA + Polluants, nettoyage, fréquence journalière, interpolation.
    """
    # Merge
    df = pd.merge(df_iqa, df_polluants, on="date", how="inner")

    # Supprimer colonnes inutiles
    df = df.drop(columns=[c for c in COLS_TO_DROP if c in df.columns], errors="ignore")

    # Convertir date
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D")

    # Interpolation simple
    for c in df.columns:
        df[c] = df[c].interpolate().bfill().ffill()

    return df.reset_index()


# ================== 3) Création des lags ==================
def make_lags(df_in: pd.DataFrame, target: str, exog: list,
              n_t: int = 7, n_x: int = 1) -> pd.DataFrame:
    df_out = df_in.copy()
    # lags de la cible
    for k in range(1, n_t + 1):
        df_out[f'{target}_lag_{k}'] = df_out[target].shift(k)
    # lags des exogènes
    for col in exog:
        for k in range(1, n_x + 1):
            df_out[f'{col}_lag_{k}'] = df_out[col].shift(k)
    return df_out


# ================== 4) Fonction de prédiction ==================
def predict_iqa(df: pd.DataFrame, target="iqa", n_lags_target=7, n_lags_exog=1, n_days=5):
    """
    Retourne les prédictions J+1 → J+5 de l'IQA.
    Gère l'alignement des features avec celles sauvegardées à l'entraînement.
    """
    # Colonnes exogènes (hors date et target)
    exog_cols = [c for c in df.columns if c not in ["date", target]]
    df_lags = make_lags(df, target, exog_cols, n_lags_target, n_lags_exog).dropna()

    # Vérification : assez de données ?
    if df_lags.empty:
        raise ValueError("❌ Pas assez de données pour créer les lags et prédire l’IQA.")

    # Forcer l’ordre + alignement colonnes
    X = df_lags.reindex(columns=FEATURES, fill_value=0)

    # Prendre la dernière ligne connue
    last_row = X.iloc[[-1]]

    preds = []
    step_feats = last_row.copy()

    iqa_lag_cols = [f"{target}_lag_{k}" for k in range(1, n_lags_target + 1)]
    exog_lag_cols = [f"{col}_lag_{1}" for col in exog_cols if f"{col}_lag_{1}" in FEATURES]

    for _ in range(n_days):
        # ✅ prédiction avec colonnes bien alignées
        y_hat = float(model_.predict(step_feats)[0])
        preds.append(y_hat)

        # MAJ des lags cible
        if all(c in step_feats.columns for c in iqa_lag_cols):
            iqa_vals = step_feats[iqa_lag_cols].to_numpy().ravel()
            iqa_vals = np.roll(iqa_vals, 1)
            iqa_vals[0] = y_hat
            step_feats.loc[:, iqa_lag_cols] = iqa_vals

        # MAJ des lags exogènes (persistance)
        if exog_lag_cols:
            exog_vals = step_feats[exog_lag_cols].to_numpy().ravel()
            exog_vals = np.roll(exog_vals, 1)
            step_feats.loc[:, exog_lag_cols] = exog_vals

    return preds


# ================== 5) Wrapper Streamlit ==================
def run_prediction_pipeline(df_iqa, df_polluants, n_days=5):
    """
    Fonction principale : reçoit deux DataFrames, retourne un DataFrame prédictions + explication.
    """
    df = prepare_data(df_iqa, df_polluants)
    preds = predict_iqa(df, n_days=n_days)

    # Créer DataFrame résultats
    future_dates = pd.date_range(start=df["date"].max() + pd.Timedelta(days=1), periods=n_days, freq="D")
    df_preds = pd.DataFrame({"date": future_dates, "iqa_pred": np.round(preds, 2)})

    # Texte explicatif sur la précision
    explanation = (
        "ℹ️ Modèle XGBoost entraîné sur les données historiques de la station.\n"
        "Précision moyenne sur test : RMSE ≈ 1.96, MAE ≈ 1.76, R² ≈ 0.52.\n"
        "Les prévisions à 5 jours doivent être interprétées comme des tendances."
    )

    return df_preds, explanation

def aggregate_polluants_daily(df):
    """Agrège les polluants par jour (moyenne uniquement des colonnes numériques)."""
    if df.empty:
        return pd.DataFrame()
    
    df = df.copy()
    df["date"] = df["timestamp"].dt.date
    
    # Colonnes numériques uniquement
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    df_daily = (
        df.groupby("date")[num_cols]
        .mean()
        .reset_index()
    )
    return df_daily


def predict_iqa_esmt():

    st.header("📈 Prévisions IQA ESMT  J+1 → J+5")

    
    df_raw = get_full_history(location_id, token, days=7)
    df_iqa = calculer_iqa_journalier(df_raw, location_id)

    df_polluants = get_full_history(location_id, token, days=15)
    
    print(df_polluants.dtypes)
    print(df_polluants.head())

    df_polluants = aggregate_polluants_daily(df_polluants)

    df_preds, explanation = run_prediction_pipeline(df_iqa, df_polluants, n_days=5)
    st.dataframe(df_preds)
    with st.expander("📄 Explication des prévisions"):
        st.markdown(explanation)
    st.subheader("Graphique des prévisions IQA")
    fig = px.line(df_preds, x="date", y="iqa_pred", markers =True,
                  title="Prévisions IQA ESMT J+1 → J+5",
                    labels={"iqa_pred": "IQA prédit", "date": "Date"})
    st.plotly_chart(fig, use_container_width=True)
    
    
    
    
    













