import pandas as pd 
import os

token = "77a25676-a9ec-4a99-9137-f33e6776b590"


BASE_URL = "https://api.airgradient.com/public/api/v1"

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data/now')



sender="houngbo.calixte.r@gmail.com"



# Valeurs limites (à ajuster selon normes locales)
VALEURS_LIMITE = {
"pm03_count": 100000, # particules de 0.3μm - pas de norme OMS, seuil indicatif élevé
"pm01_corrected": 15, # µg/m³ - Particules fines PM1 (plus sévère que PM2.5)
"pm02_corrected": 75, # µg/m³ - PM2.5 - norme OMS 2021
"pm10_corrected": 150, # µg/m³ - PM10 - norme OMS 2021
"rco2_corrected": 1000, # ppm - qualité de l'air intérieur acceptable (OMS + ASHRAE)
"atmp_corrected": 27, # °C - Température intérieure maximale conseillée
"rhum_corrected": 60, # % - Humidité relative recommandée : 40-60%
"tvoc": 500, # µg/m³ - Limite indicative (sensibilité à 150-300 selon source)
"noxIndex": 100 # µg/m³ - Limite OMS pour NO₂ sur 1h
}

# Liens pour les differentes videos youtubes explicatives et illustratives 
liens = {
            
            "1":
                {
                    "lien":"https://youtu.be/3YyaYqYO7Ks?si=fXdVMjUsqSSBHE45",
                    "nom":"Montpellier Méditerranée Métropole"
                },
            "2":
                {
                    "lien":"https://youtu.be/GFkaDF_c6zA?si=_axvJFh5ksmEAJGr",
                    "nom":"Agence de la transition ecologique ADEME"
                },
            "3":
                {
                    "lien":"https://youtu.be/AUrSjPIPxgY?si=IF_vhIcFGe6dPepl",
                    "nom":"CCube Academy"
                },
            "4":
                {
                    "lien":"https://youtu.be/IPXIvaXI0xg?si=XXFErUfpcrXsEgUb",
                    "nom":"European Environment Agency"
                }
                
        }

#======================================================

locations = pd.read_csv("locations_info.csv")

location_ids = locations["location_id"]
school_names = locations["name"]
logo_paths = locations["logo_path"]












