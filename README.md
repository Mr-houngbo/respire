# RESPiRE - Dashboard de Surveillance et d'Alerte Qualité de l'Air - HACKATHON KAIKAI 

**RESPiRE** est une plateforme complète de suivi, d’analyse et d’alerte sur la qualité de l’air dans les écoles, pensée pour protéger la santé des enfants et informer les parents et responsables scolaires en temps réel.

---

## 🚀 Fonctionnalités principales

- **Tableau de bord interactif** : Visualisation des données de qualité de l’air (PM2.5, CO2, température, humidité, etc.) en temps réel et sur l’historique.
- **Calcul automatique de l’IQA** (Indice de Qualité de l’Air) journalier.
- **Prédiction J+1** de la qualité de l’air grâce à un modèle de machine learning.
- **Alertes automatiques** par SMS et WhatsApp aux parents en cas de dépassement de seuils critiques.
- **Gestion des contacts parents** (import, édition, visualisation).
- **Programmation et historique des alertes**.
- **Configuration avancée** (seuils, horaires de silence, providers SMS/WhatsApp).

---

## 📦 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Mr-houngbo/respire.git
   cd respire
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv env
   source env/bin/activate  # ou `env\Scripts\activate` sous Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les secrets**
   - Renseigner vos identifiants Twilio/Meta dans `sms_config.json` et `whatsapp_config.json`.
   - Ajouter vos contacts dans `parents_contacts_sms.txt` et `parents_contacts.txt`.

---

## 🖥️ Lancer l’application

```bash
streamlit run app.py
```

L’interface web s’ouvre automatiquement dans votre navigateur.

---

## ⚙️ Configuration

- **Seuils d’alerte** : Modifiables dans l’interface ou dans les fichiers de config.
- **Horaires de silence** : Pour éviter les notifications la nuit.
- **Providers** : Twilio (SMS/WhatsApp Sandbox), Meta Business API (WhatsApp officiel).

---

## 📲 Envoi d’alertes

- **Automatique** : Dès qu’un seuil est dépassé, les parents reçoivent une alerte personnalisée.
- **Manuel** : Possibilité d’envoyer un message à la demande depuis le dashboard.
- **Historique** : Visualisation de tous les messages envoyés, par date, type, parent, etc.

---

## 🔗 Intégration & Automatisation

- **Scheduler GitHub Actions** : Déclenchez des alertes automatiquement à des horaires définis.

---

## 🛡️ Sécurité

- Les accès API et webhooks sont protégés par des secrets.
- Les données personnelles sont stockées localement et non partagées.

---

## 📁 Structure du projet

```
respire/
│
├── app.py                  # Point d’entrée Streamlit
├── src/                    # Fonctions principales (prédiction, IQA, etc.)
├── components/             # Modules UI (parent, alertes, etc.)
├── models/                 # Modèles ML et scalers
├── data/                   # Données locales et historiques
├── parents_contacts_sms.txt
├── parents_contacts.txt
├── sms_config.json
├── whatsapp_config.json
├── requirements.txt
└── README.md
```

---

## 👥 Équipe & Contact

- Projet développé par l'équipe Breath4life lors du Hackathon KAIKAI 2025.
- Contact : [Breath4life] - [houngbo.calixte.r@gmail.com]

---

## 📝 Licence

Ce projet est open-source sous licence MIT.

---


**Protégeons la santé des enfants, respirons**
