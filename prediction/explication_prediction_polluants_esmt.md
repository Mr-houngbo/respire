# 📘 README – Modèle de Prédiction de la Qualité de l’Air (J+1)

Ce projet permet de **prédire la qualité de l’air du lendemain (J+1)** à partir des données des jours précédents.
Le modèle utilisé est basé sur **XGBoost**, capable de gérer plusieurs variables cibles (polluants, température, humidité, etc.) simultanément.

---

## 🔧 Étapes principales du code

### 1. Imports

Le code utilise :

* **Pandas / NumPy** : manipulation de données.
* **Scikit-learn** : normalisation, métriques, GridSearchCV.
* **XGBoost** : algorithme principal de régression.
* **Joblib** : sauvegarde/chargement des modèles et paramètres.

---

### 2. Transformation en problème supervisé

La fonction `create_supervised(df, n_lags)` transforme la série temporelle en problème de prédiction supervisée.

👉 Exemple : si `n_lags = 3`, on utilise les 3 derniers jours pour prédire le jour courant.

* Les colonnes deviennent `variable(t-3)`, `variable(t-2)`, `variable(t-1)` pour les features.
* Les colonnes du jour courant `variable(t)` servent de **cibles**.

---

### 3. Préparation des données

* Suppression des colonnes inutiles (`Location ID`, `Sensor ID`, etc.).
* Conversion des dates en format datetime et tri par ordre chronologique.
* Indexation du DataFrame par la date.
* Application de `create_supervised` pour générer les données exploitables par le modèle.

---

### 4. Découpage Train/Test

* On sépare 80% des données pour l’entraînement, 20% pour le test.
* `X_train` = features (jours passés).
* `y_train` = cibles (valeurs des polluants du jour courant).
* Même découpage pour le test.

---

### 5. Normalisation

On applique un **StandardScaler** (moyenne = 0, écart-type = 1) :

* `scaler_X` pour les variables explicatives.
* `scaler_y` pour les variables cibles.

⚠️ Important : les scalers sont sauvegardés pour réutilisation en production.

---

### 6. Définition du modèle

* Base : `XGBRegressor` (XGBoost en régression).
* Enveloppe : `MultiOutputRegressor` → permet de prédire **plusieurs variables à la fois**.
* Une grille d’hyperparamètres (`n_estimators`, `learning_rate`, `max_depth`, etc.) est définie pour optimiser le modèle.

---

### 7. Optimisation par Grid Search

* On utilise `GridSearchCV` avec validation croisée (`cv=5`) pour tester toutes les combinaisons d’hyperparamètres.
* La métrique utilisée est le **R²** (ou `neg_mean_squared_error` si besoin).
* Le meilleur ensemble d’hyperparamètres est sélectionné.

---

### 8. Entraînement final et évaluation

* Le modèle est réentraîné sur tout le jeu d’entraînement avec les meilleurs paramètres.
* On évalue sur le jeu de test avec :

  * **RMSE** (Root Mean Squared Error) : erreur quadratique moyenne.
  * **MAE** (Mean Absolute Error) : erreur absolue moyenne.
  * **R²** (coefficient de détermination).

👉 Ces métriques permettent de comparer le modèle avec une baseline (par ex. persistance = « demain = aujourd’hui »).

---

### 9. Sauvegarde des artefacts

Les objets suivants sont sauvegardés avec `joblib` :

* `xgboost_multioutput.pkl` → le modèle entraîné.
* `scaler_X.pkl` et `scaler_y.pkl` → les normalisations utilisées.
* `target_columns.pkl` → les colonnes cibles (polluants, météo, etc.).
* `n_lags.pkl` → nombre de jours utilisés pour prédire J+1.

👉 Ces fichiers permettent de recharger le modèle directement en production.

---

### 10. Fonction de prédiction J+1

La fonction `predict_j_plus_1(last_days_df)` :

1. Charge le modèle et les paramètres sauvegardés.
2. Vérifie que `last_days_df` contient **exactement `n_lags` jours** et toutes les colonnes nécessaires.
3. Construit les features (`t-1`, `t-2`, …).
4. Applique les scalers et prédit.
5. Retourne un DataFrame avec les valeurs prédites pour **le lendemain**.

👉 Exemple de sortie :

```
            PM2.5 (µg/m³) corrected   CO2 (ppm) corrected   Humidity (%) corrected
2025-08-21                 12.5                    405.2                    71.8
```

---

### 11. Exemple d’utilisation

```python
dernier_jours = df.tail(n_lags)   # Les derniers jours connus
print("🔮 Prédiction J+1 :")
print(predict_j_plus_1(dernier_jours))
```

---

## 🚀 En résumé

1. On prépare les données (suppression colonnes, indexation date).
2. On crée un problème supervisé avec `n_lags` jours en entrée.
3. On normalise les données.
4. On entraîne un modèle XGBoost multi-sorties optimisé par GridSearch.
5. On évalue la performance.
6. On sauvegarde le modèle et ses paramètres.
7. On fournit une fonction clé en main pour prédire J+1.

---

## 💡 Améliorations possibles

* Tester différents `n_lags` (ex. 3, 5, 7).
* Ajouter des features météo (température max/min, humidité, vent) - on pense a openweather .
* Entraîner un modèle par polluant plutôt qu’un multi-sortie.
* Comparer avec d’autres algorithmes (Ridge, Lasso, RandomForest).
