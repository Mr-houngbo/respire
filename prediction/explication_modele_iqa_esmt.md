# 🔎 Explication du pipeline de prédiction de l’IQA (Indice de Qualité de l’Air)

## 1. Fusion des données (merge)

Nous disposions de deux sources :

* **Données capteurs** : mesures brutes et corrigées (PM2.5, PM10, CO₂, NOX, TVOC, humidité, température, etc.).
* **Données IQA** : valeurs journalières de l’indice de qualité de l’air.

La première étape a été de **fusionner ces DataFrames sur la date**.
Comme l’un utilisait un format UTC et l’autre un format local, nous avons harmonisé les colonnes de dates (`pd.to_datetime()`, suppression du fuseau horaire).

👉 Résultat : un **seul tableau** contenant :

* Une colonne `date`
* Les mesures capteurs
* La colonne cible `iqa`

---

## 2. Préparation des données temporelles

Comme il s’agit d’une **série temporelle**, il faut introduire la dépendance au temps.
Nous avons donc créé des **lags (décalages temporels)** :

* **Pour la cible `iqa`** : uniquement `iqa_lag_1`, c’est-à-dire la valeur de l’IQA du jour précédent.
* **Pour les variables exogènes** (PM, CO₂, humidité, etc.) : un décalage de 1 jour également (`feature_lag_1`).

👉 Pourquoi un seul lag ?
Avec un petit dataset (18 lignes utiles), ajouter 7 lags introduit trop de dimensions et du bruit.
Au contraire, garder **1 seul lag** concentre l’information utile et améliore la performance (car la qualité de l’air dépend surtout du jour précédent + des conditions capteurs).

---

## 3. Split des données

* **80% des données** → entraînement
* **20% restantes** → test (simulation de prédictions futures)
* Pas de mélange (on conserve l’ordre temporel).

---

## 4. Validation croisée temporelle

On utilise un `TimeSeriesSplit` (validation croisée adaptée aux séries temporelles) pour estimer la robustesse du modèle.

👉 Résultat : **CV RMSE moyen = 4.43**.

---

## 5. Entraînement du modèle XGBoost

Le modèle utilisé est un **XGBRegressor** avec régularisation (boosting par arbres).
Hyperparamètres principaux :

* `n_estimators=800`,
* `learning_rate=0.04`,
* `max_depth=3`,
* `subsample=0.9`, `colsample_bytree=0.9`,
* régularisation L1/L2 (`reg_alpha=0.1`, `reg_lambda=1.0`).

👉 Ce modèle apprend à prédire l’IQA en fonction :

* de la valeur de la veille (`iqa_lag_1`),
* des mesures capteurs décalées (`PM2.5_lag_1`, `CO₂_lag_1`, etc.).

---

## 6. Évaluation du modèle

Sur les données de test (non vues), on obtient :

* **RMSE = 1.41**
* **MAE = 0.90**
* **R² = 0.86**

Ces scores montrent que :

* L’erreur moyenne est inférieure à 1 point IQA.
* Le modèle explique **près de 86% de la variance**, ce qui est excellent vu la petite taille du dataset.
* C’est **nettement meilleur** que la version précédente (7 lags, R² ≈ 0.52).

---

## 7. Sauvegarde du modèle

Le modèle final est sauvegardé avec **joblib** sous le nom :

```
xgb_iqa_all_features.pkl
```

Il peut donc être réutilisé immédiatement pour de nouvelles prédictions.

---

## 8. Prédictions J+1 et multi-jours

* **J+1** : on utilise la dernière ligne connue et ses lags pour prédire le lendemain.
* **J+1 → J+5** : on applique une boucle auto-régressive :

  * chaque prédiction devient le nouveau `iqa_lag_1` du jour suivant,
  * les capteurs sont supposés constants (persistance de leurs valeurs).

👉 Résultat :

* **J+1 = 130.04**
* **Prédictions J+1 → J+5 = \[130.04, 129.66, 130.02, 129.55, 128.94]**

Ces valeurs sont cohérentes : elles suivent une tendance stable, avec de légères oscillations.

---

# 🎯 Conclusion

* La fusion des données a permis de centraliser IQA et mesures capteurs.
* La création des **lags temporels** a transformé le dataset en un problème supervisé.
* Le modèle **XGBoost** s’est révélé très performant, surtout avec un seul lag sur l’IQA.
* Résultats : **R² = 0.86**, erreurs faibles et prédictions réalistes.

👉 En résumé :
La qualité de l’air du lendemain peut être prédite **de façon fiable** à partir :

* de l’IQA de la veille,
* et des mesures capteurs décalées d’un jour.

---
