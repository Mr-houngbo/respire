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

#                                                  SECTION PREDICTION IQA J+1
#=============================================================================================================
#=============================================================================================================



# ---------------------------
# CONFIG
# ---------------------------
MODEL_PATH = "models/xgb_iqa_all_features.pkl"

# Mapping API -> noms de colonnes du modèle (déjà utilisé dans ton script)
API_TO_MODEL_COLS = {
    'pm02_corrected': 'PM2.5 (μg/m³) corrected',
    'pm10_corrected': 'PM10 (μg/m³)',
    'rco2_corrected': 'CO2 (ppm) corrected',
    'pm003Count': '0.3μm particle count',
    'atmp_corrected': 'Temperature (°C) corrected',
    'rhum_corrected': 'Humidity (%) corrected',
    'tvoc': 'TVOC (ppb)',
    'noxIndex': 'NOX index',
    'pm01_corrected': 'PM1 (μg/m³)',
    'tvocIndex': 'TVOC index',
}

# Liste des features exogènes utilisées à l'entraînement (toutes sauf 'iqa')
EXOG_FEATURES = [
    'PM2.5 (μg/m³) corrected',
    '0.3μm particle count',
    'CO2 (ppm) corrected',
    'Temperature (°C) corrected',
    'Heat Index (°C)',
    'Humidity (%) corrected',
    'TVOC (ppb)',
    'TVOC index',
    'NOX index',
    'PM1 (μg/m³)',
    'PM10 (μg/m³)',
]

# ---------------------------
# HELPERS
# ---------------------------
def _rename_api_columns(df_daily: pd.DataFrame) -> pd.DataFrame:
    """Renomme les colonnes de l'API vers les noms utilisés par le modèle si elles existent."""
    cols = df_daily.columns.tolist()
    for api_col, model_col in API_TO_MODEL_COLS.items():
        if api_col in cols:
            df_daily.rename(columns={api_col: model_col}, inplace=True)
    return df_daily



def _make_multiday_preds(model, last_row: pd.DataFrame, horizon: int = 5) -> list:
    """
    Prédictions auto-régressives sur plusieurs jours.
    - iqa_lag_1 devient la prédiction précédente
    - les exogènes lag_1 restent persistantes (valeur constante)
    """
    step_feats = last_row.copy()
    preds = []
    for _ in range(horizon):
        y_hat = float(model.predict(step_feats)[0])
        preds.append(y_hat)
        # MAJ iqa_lag_1 avec la dernière prédiction
        step_feats['iqa_lag_1'] = y_hat
        # Exogènes: persistance -> ne change pas
    return preds

# ---------------------------
# CORE
# ---------------------------

# === PATCH 1/4 — _daily_aggregate : évite les conflits d’index/colonne "date" et rend l’agrégation robuste
def _daily_aggregate(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Agrège par jour (moyenne) à partir d'une colonne temporelle.
    Retourne un DF indexé par datetime avec index.name="__day__" (évite tout conflit 'date').
    """
    df = df_raw.copy()

    # Normaliser la colonne temporelle
    if 'timestamp' not in df.columns:
        for alt in ['time', 'createdAt']:
            if alt in df.columns:
                df = df.rename(columns={alt: 'timestamp'})
                break
    if 'timestamp' not in df.columns:
        raise ValueError("Aucune colonne temporelle ('timestamp'|'time'|'createdAt') trouvée.")

    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    df = df.dropna(subset=['timestamp'])

    # Grouper à JOUR (floor) puis moyenne
    df['__day__'] = df['timestamp'].dt.floor('D')
    daily = df.groupby('__day__').mean(numeric_only=True)

    daily.index = pd.to_datetime(daily.index)
    daily.index.name = '__day__'
    return daily


# === PATCH 2/4 — fetch_last_days_for_iqa_prediction : fenêtre ≤ 9j (évite 422) + fallback progressif
def fetch_last_days_for_iqa_prediction(location_id: int, token: str, days: int = 9):
    """
    Récupère les mesures brutes sur une fenêtre ≤10 jours (sinon 422),
    agrège par jour, renomme, calcule l'IQA journalier et renvoie:
      - daily_feats (agrégé capteurs, index='__day__')
      - daily_iqa (DataFrame ['date','iqa'])
    Fallback progressif si vide/422: 9 -> 7 -> 5 -> 3 -> 2 -> 1.
    """
    candidate_windows = [min(days, 9), 7, 5, 3, 2, 1]
    df_raw = pd.DataFrame()
    last_error = None

    for win in candidate_windows:
        try:
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=win)
            tmp = get_measures_range(location_id, token, from_date, to_date)
            if not tmp.empty:
                df_raw = tmp
                break
        except Exception as e:
            last_error = e
            continue

    if df_raw.empty:
        raise ValueError(f"Aucune donnée brute récupérée (fenêtres testées: {candidate_windows}). "
                         f"Dernière erreur: {last_error}")

    daily_feats = _daily_aggregate(df_raw)

    # Renommer colonnes API -> noms modèle (si colonnes présentes)
    daily_feats = _rename_api_columns(daily_feats)

    # IQA journalier (utilise df_raw brut)
    daily_iqa = calculer_iqa_journalier(df_raw, location_id)  # doit retourner ['date','iqa']
    if daily_iqa.empty or len(daily_iqa) < 2:
        raise ValueError("IQA journalier insuffisant pour créer iqa_lag_1 (au moins 2 jours requis).")

    return daily_feats, daily_iqa

# === PATCH 3/4 — _build_last_feature_row_for_iqa_j1 : aligne EXACTEMENT sur les features attendues par le modèle
def _get_expected_features_from_model(model) -> list:
    """Retourne la liste des features attendues par le modèle (ordre exact)."""
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    try:
        return list(model.get_booster().feature_names)
    except Exception:
        raise ValueError("Impossible de récupérer les noms de features du modèle (feature_names_in_ / booster).")

def _safe_get_last_value(df_idx_dt: pd.DataFrame, col: str) -> float:
    """Dernière valeur non-NaN; 0.0 si absente."""
    if col not in df_idx_dt.columns:
        return 0.0
    v = df_idx_dt[col].dropna()
    return float(v.iloc[-1]) if len(v) else 0.0

def _safe_get_prev_value_dfidx(df_idx_dt: pd.DataFrame, col: str) -> float:
    """Valeur J-1 (avant-dernier) à partir d'un DF indexé par datetime; 0.0 si indisponible."""
    if col not in df_idx_dt.columns:
        return 0.0
    v = df_idx_dt[col].dropna()
    if len(v) >= 2:
        return float(v.iloc[-2])
    return float(v.iloc[-1]) if len(v) else 0.0

def _safe_get_prev_value_iqa(iqa_df: pd.DataFrame) -> float:
    """Valeur iqa J-1 à partir de daily_iqa ['date','iqa'] trié par date; 0.0 si indisponible."""
    if 'date' not in iqa_df.columns or 'iqa' not in iqa_df.columns:
        return 0.0
    tmp = iqa_df.copy()
    tmp['date'] = pd.to_datetime(tmp['date'])
    tmp = tmp.sort_values('date')
    v = tmp['iqa'].dropna()
    if len(v) >= 2:
        return float(v.iloc[-2])
    return float(v.iloc[-1]) if len(v) else 0.0

def _build_last_feature_row_for_iqa_j1(model, daily_feats: pd.DataFrame, daily_iqa: pd.DataFrame) -> pd.DataFrame:
    """
    Construit UNE ligne de features alignée EXACTEMENT sur ce que le modèle attend :
      - 'iqa_lag_1' := IQA J-1 (daily_iqa)
      - '<feature>_lag_1' := valeur capteur J-1 (daily_feats)
      - '<feature>' (sans suffixe) := valeur capteur J (daily_feats)
    """
    expected = _get_expected_features_from_model(model)

    # daily_feats est indexé par '__day__' (datetime). On s'assure du tri.
    feats = daily_feats.copy().sort_index()

    values = []
    for feat in expected:
        if feat == 'iqa_lag_1':
            values.append(_safe_get_prev_value_iqa(daily_iqa))
        elif feat.endswith('_lag_1'):
            base = feat[:-6]  # retire "_lag_1"
            values.append(_safe_get_prev_value_dfidx(feats, base))
        else:
            values.append(_safe_get_last_value(feats, feat))

    return pd.DataFrame([values], columns=expected)


def load_iqa_model(path: str = MODEL_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Modèle introuvable: {path}")
    return joblib.load(path)

# ---------------------------
# UI STREAMLIT
# ---------------------------

# === PATCH 4/4 — show_iqa_prediction_section : charger le modèle AVANT, puis construire la ligne attendue
def show_iqa_prediction_section(location_id: int, token: str):
    st.subheader("🔮 Prédiction IQA (J+1)")

    try:
        # 1) Charger le modèle pour connaître les features attendues
        model = load_iqa_model(MODEL_PATH)

        # 2) Récupérer les données et séries journalières
        daily_feats, daily_iqa = fetch_last_days_for_iqa_prediction(
            location_id=location_id,
            token=token,
            days=9  # <= 10 jours (évite 422)
        )

        # 3) Construire la dernière ligne de features EXACTEMENT dans l'ordre attendu
        last_row_features = _build_last_feature_row_for_iqa_j1(model, daily_feats, daily_iqa)

        # 4) Prédictions
        pred_j1 = float(model.predict(last_row_features)[0])
        preds_5  = _make_multiday_preds(model, last_row_features, horizon=5)

        # 5) UI
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("IQA prédit (J+1)", f"{pred_j1:.2f}")
            st.caption("Basé sur iqa_lag_1 et capteurs (lag_1/brut) alignés au modèle.")
        with col2:
            st.write("**Features modèle (dernière ligne)**")
            st.dataframe(last_row_features)

        # Série observée (7j) + prévisions (5j)
        hist = daily_iqa.copy()
        hist['date'] = pd.to_datetime(hist['date'])
        hist = hist.sort_values('date').tail(7)

        future_dates = [hist['date'].iloc[-1] + timedelta(days=i) for i in range(1, len(preds_5) + 1)]
        df_future = pd.DataFrame({'date': future_dates, 'iqa': preds_5})
        chart_df = pd.concat([hist[['date','iqa']].assign(type='observé'), df_future.assign(type='prévu')], ignore_index=True)

        fig = px.line(chart_df, x='date', y='iqa', color='type', markers=True,
                      title="IQA : 7 jours observés + 5 jours prévus")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📄 Journal des prédictions J+1 → J+5"):
            st.dataframe(pd.DataFrame({'date': future_dates, 'iqa_prévu': np.round(preds_5, 2)}))

    except Exception as e:
        st.error(f"Erreur pendant la prédiction IQA : {e}")


# ---------------------------
# Exemple d’utilisation dans app.py
# ---------------------------
# from iqa_prediction_dashboard import show_iqa_prediction_section
# def show():
#     ...
#     show_iqa_prediction_section(location_id=164928, token="VOTRE_TOKEN")
#     ...
# --- PATCH: remplacer les 2 fonctions ci-dessous dans iqa_prediction_dashboard.py ---












#=============================================================================================================
#=============================================================================================================

#                                                  SECTION COMPREHENSION PREDICTION J+1
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
    """
    exog_cols = [c for c in df.columns if c not in ["date", target]]
    df_lags = make_lags(df, target, exog_cols, n_lags_target, n_lags_exog).dropna()

    # Vérification avant d'aller plus loin
    if df_lags.empty:
        raise ValueError("❌ Pas assez de données pour créer les lags et prédire l’IQA.")

    
    
    # Features attendues
    features = [c for c in df_lags.columns if c not in ["date", target]]

    if not features:
        raise ValueError("❌ Aucune variable explicative disponible pour la prédiction.")

    # Prendre la dernière ligne connue
    last_row = df_lags[features].iloc[[-1]]

    preds = []
    step_feats = last_row.copy()

    iqa_lag_cols = [f"{target}_lag_{k}" for k in range(1, n_lags_target + 1)]
    exog_lag_cols = [f"{col}_lag_{1}" for col in exog_cols]

    for _ in range(n_days):
        y_hat = float(model_.predict(step_feats)[0])
        preds.append(y_hat)

        # MAJ lags cible
        iqa_vals = step_feats[iqa_lag_cols].to_numpy().ravel()
        iqa_vals = np.roll(iqa_vals, 1)
        iqa_vals[0] = y_hat
        step_feats[iqa_lag_cols] = iqa_vals

        # MAJ lags exogènes (persistance)
        if len(exog_lag_cols) > 0:
            exog_vals = step_feats[exog_lag_cols].to_numpy().ravel()
            exog_vals = np.roll(exog_vals, 1)
            step_feats[exog_lag_cols] = exog_vals

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
    
    
    
    
    








