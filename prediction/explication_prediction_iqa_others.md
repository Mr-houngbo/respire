# 🌍 Explication du Processus de Prédiction IQA avec Régression Linéaire

## 1. Contexte
L’**Indice de Qualité de l’Air (IQA)** est une mesure qui permet d’évaluer la pollution atmosphérique sur une zone donnée.  
Dans notre projet, nous cherchons à **prédire l’IQA des prochains jours** pour plusieurs écoles équipées de capteurs IoT.  

Le modèle choisi est une **régression linéaire adaptée aux séries temporelles**, qui utilise uniquement les IQA passés (des 7 derniers jours) pour prévoir les valeurs futures.

---

## 2. Préparation des données
1. **Collecte des données** : récupération des IQA journaliers depuis les capteurs.
2. **Nettoyage et interpolation** : les données manquantes sont complétées (`interpolate()`) pour éviter des trous dans la série.
3. **Fréquence temporelle fixe** : on force les dates à être continues avec `asfreq('D')`.

Exemple :
```text
date        iqa
2025-05-04  134.09
2025-05-05  129.40
2025-05-06  125.43
...
```
---

## 3. Création des variables explicatives (lags)

Pour prédire la valeur d’aujourd’hui, on crée des **retards (lags)** :

* `lag_1` = IQA d’hier
* `lag_2` = IQA d’avant-hier
* ...
* `lag_7` = IQA d’il y a 7 jours

Ainsi, chaque observation contient la valeur cible (`iqa`) et ses antécédents.

---

## 4. Entraînement du modèle

* On découpe les données en **train (80%)** et **test (20%)**.
* On utilise une **régression linéaire standardisée** (`StandardScaler + LinearRegression`).
* On valide le modèle avec une **validation croisée temporelle (TimeSeriesSplit)** pour éviter les fuites d’information.

📊 **Métriques utilisées :**

* RMSE (Root Mean Squared Error)
* MAE (Mean Absolute Error)
* R² (coefficient de détermination)

---

## 5. Prédiction

### a) Prédiction J+1

On prend les **7 derniers jours d’IQA réels**, on les passe au modèle → on obtient la prévision pour **demain**.

### b) Prédictions J+1 → J+5

Pour prévoir plusieurs jours :

1. On prédit J+1.
2. On insère cette prédiction comme nouveau `lag_1`.
3. On décale les autres lags (`lag_2`, `lag_3`, …).
4. On répète le processus jusqu’à J+5.

C’est ce qu’on appelle **l’auto-régression récursive**.

---

## 6. Sauvegarde et utilisation en production

Chaque modèle est entraîné pour une école (`location_id`) et sauvegardé dans un fichier `.pkl`.
Exemples :

```
linreg_iqa_best_151726.pkl
linreg_iqa_best_89441.pkl
```

En production, on :

1. Charge le modèle correspondant à la `location_id`.
2. Récupère les IQA des 7 ou 10 derniers jours.
3. Génère la prédiction J+1 (et éventuellement J+5).
4. Affiche le résultat dans **Streamlit**.

---

## 7. Schéma récapitulatif

```
Données IQA (capteurs) → Prétraitement → Lags (7 jours) → 
Régression Linéaire → Prédiction J+1 (et multi-jours) → Streamlit
```

---

✅ En résumé :
Nous utilisons un modèle de **régression linéaire simple mais efficace**, basé uniquement sur l’historique des 7 derniers jours d’IQA, pour fournir des prédictions à court terme fiables et faciles à expliquer.

