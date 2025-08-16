import json
import os
import time
import threading
from datetime import datetime, timedelta
import logging
import schedule
from typing import Dict, List, Tuple, Optional
from twilio.rest import Client
import pandas as pd
from src.functions import fetch_current_data,calculer_iqa,afficher_iqa_plot,calculer_iqa_journalier,get_past_measures,calculate_air_quality_status
from config.settings import token,BASE_URL,VALEURS_LIMITE,location_ids,DATA_DIR,liens
import streamlit as st

location_id = location_ids[6]


# Remplacer la lecture des variables d'environnement par :
def get_config_value(key, default=""):
    """Récupère une valeur depuis les secrets Streamlit ou env"""
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, default)


# Configuration du logging propre
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sms_alerts.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SMSAlertSystem:
    """
    Système d'alertes SMS pour les parents - Version Backend Pure
    Gère l'envoi automatique de notifications selon la qualité de l'air à l'école
    """
    def repair_corrupted_files(self) -> None:
        """Répare les fichiers JSON corrompus"""
        files_to_check = [
            (self.sent_alerts_file, 'sent_alerts'),
            (self.rate_limit_file, 'rate_limits'),
            (self.config_file, 'config')
        ]
        
        for file_path, file_type in files_to_check:
            if os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size == 0:
                        logger.warning(f"Fichier {file_path} vide - suppression")
                        os.remove(file_path)
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            json.loads(content)  # Test de parsing
                            logger.info(f"Fichier {file_path} valide")
                        else:
                            logger.warning(f"Fichier {file_path} vide - suppression")
                            os.remove(file_path)
                            
                except json.JSONDecodeError:
                    logger.error(f"Fichier {file_path} corrompu - suppression")
                    backup_name = f"{file_path}.corrupt.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    os.rename(file_path, backup_name)
                    logger.info(f"Sauvegarde créée: {backup_name}")
                    
                except Exception as e:
                    logger.error(f"Erreur vérification {file_path}: {e}")             
                    
    def __init__(self, contacts_file: str = "parents_contacts_sms.txt", config_file: str = "sms_config.json"):
        self.contacts_file = contacts_file
        self.config_file = config_file
        self.sent_alerts_file = "sent_alerts.json"
        self.rate_limit_file = "rate_limits.json"
        
        # Configuration par défaut sécurisée
        self.default_config = {
            "sms_provider": "twilio",            
            "twilio_account_sid": get_config_value("TWILIO_ACCOUNT_SID", ""),
            "twilio_auth_token": get_config_value("TWILIO_AUTH_TOKEN", ""), 
            "twilio_phone_number": get_config_value("TWILIO_PHONE_NUMBER", ""),
            "max_sms_per_day": 5,
            "max_sms_per_hour": 2,
            "quiet_hours_start": "21:00",
            "quiet_hours_end": "07:00",
            "pm25_alert_threshold": 150,
            "pm25_danger_threshold": 150,
            "co2_alert_threshold": 1000,
            "enabled": True,
            "auto_check_interval_minutes": 30,
            "retry_attempts": 3,
            "retry_delay_seconds": 60,
        }
        
        self.repair_corrupted_files()        
        self.load_config()
        self.load_sent_alerts()
        self.load_rate_limits()
        self._running = False
        self._scheduler_thread = None

        logger.info("✅ Système SMS initialisé")

    def load_config(self) -> None:
        """Charge la configuration SMS avec gestion d'erreurs"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge avec la config par défaut pour éviter les clés manquantes
                    self.config = {**self.default_config, **loaded_config}
            else:
                self.config = self.default_config.copy()
                self.save_config()
            
            # Validation de la configuration
            self._validate_config()
            logger.info("Configuration SMS chargée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur chargement config SMS : {e}")
            self.config = self.default_config.copy()

    def _validate_config(self) -> None:
        """Valide la configuration SMS"""
        if self.config['sms_provider'] == 'twilio':
            required_fields = ['twilio_account_sid', 'twilio_auth_token', 'twilio_phone_number']
            missing_fields = [field for field in required_fields if not self.config.get(field)]
            if missing_fields:
                logger.warning(f"Configuration Twilio incomplète: {missing_fields}")

    def save_config(self) -> None:
        """Sauvegarde la configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Configuration sauvegardée")
        except Exception as e:
            logger.error(f"Erreur sauvegarde config : {e}")

    def load_sent_alerts(self) -> None:
        """Charge l'historique des alertes envoyées"""
        try:
            if os.path.exists(self.sent_alerts_file):
                # Vérifier si le fichier n'est pas vide
                file_size = os.path.getsize(self.sent_alerts_file)
                if file_size == 0:
                    logger.warning(f"Fichier {self.sent_alerts_file} vide - initialisation")
                    self.sent_alerts = {}
                    self.save_sent_alerts()
                    return
                
                with open(self.sent_alerts_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning("Contenu du fichier historique vide")
                        self.sent_alerts = {}
                        self.save_sent_alerts()
                        return
                    
                    self.sent_alerts = json.loads(content)
            else:
                self.sent_alerts = {}
                # Créer le fichier immédiatement
                self.save_sent_alerts()
                
            # Nettoyer les anciens historiques (> 30 jours)
            self._cleanup_old_alerts()
            logger.info(f"Historique chargé: {len(self.sent_alerts)} entrées")
            
        except json.JSONDecodeError as e:
            logger.error(f"Fichier JSON corrompu ({self.sent_alerts_file}): {e}")
            # Sauvegarder l'ancien fichier corrompu
            if os.path.exists(self.sent_alerts_file):
                backup_name = f"{self.sent_alerts_file}.corrupt.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.sent_alerts_file, backup_name)
                logger.info(f"Fichier corrompu sauvegardé: {backup_name}")
            
            # Réinitialiser
            self.sent_alerts = {}
            self.save_sent_alerts()
            
        except Exception as e:
            logger.error(f"Erreur chargement historique : {e}")
            self.sent_alerts = {}
            self.save_sent_alerts()
            
            
    def _cleanup_old_alerts(self) -> None:
        """Nettoie les alertes anciennes pour optimiser les performances"""
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        keys_to_remove = []
        
        for key in self.sent_alerts.keys():
            try:
                # Format clé: phone_alerttype_date
                date_part = key.split('_')[-1]
                if date_part < cutoff_date:
                    keys_to_remove.append(key)
            except:
                continue
        
        for key in keys_to_remove:
            del self.sent_alerts[key]
            
        if keys_to_remove:
            self.save_sent_alerts()
            logger.info(f"Nettoyé {len(keys_to_remove)} anciens historiques")

    def save_sent_alerts(self) -> None:
        """Sauvegarde l'historique des alertes"""
        try:
            with open(self.sent_alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.sent_alerts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde alertes : {e}")

    def load_rate_limits(self) -> None:
        """Charge les limites de débit"""
        try:
            if os.path.exists(self.rate_limit_file):
                with open(self.rate_limit_file, 'r', encoding='utf-8') as f:
                    self.rate_limits = json.load(f)
            else:
                self.rate_limits = {}
        except:
            self.rate_limits = {}

    def save_rate_limits(self) -> None:
        """Sauvegarde les limites de débit"""
        try:
            with open(self.rate_limit_file, 'w', encoding='utf-8') as f:
                json.dump(self.rate_limits, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde rate limits : {e}")

    def load_parent_contacts(self) -> List[Dict]:
        """Charge la liste des contacts parents avec validation"""
        contacts = []
        try:
            if not os.path.exists(self.contacts_file):
                logger.warning(f"Fichier {self.contacts_file} non trouvé")
                return contacts
                
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 4:
                            # Validation du numéro de téléphone
                            phone = self._normalize_phone_number(parts[1])
                            if phone:
                                contacts.append({
                                    'nom': parts[0],
                                    'telephone': phone,
                                    'enfant': parts[2],
                                    'classe': parts[3],
                                    'line_num': line_num
                                })
                            else:
                                logger.warning(f"Numéro invalide ligne {line_num}: {parts[1]}")
                        else:
                            logger.warning(f"Ligne {line_num} mal formatée : {line}")
                            
            logger.info(f"Chargé {len(contacts)} contacts parents")
            
        except Exception as e:
            logger.error(f"Erreur lecture contacts : {e}")
        
        return contacts

    def _normalize_phone_number(self, phone: str) -> Optional[str]:
        """Normalise et valide un numéro de téléphone sénégalais"""
        if not phone:
            return None
            
        # Nettoyer le numéro
        phone = ''.join(filter(str.isdigit, phone))
        
        # Formats acceptés pour le Sénégal
        if phone.startswith('221'):
            phone = phone[3:]
        elif phone.startswith('+221'):
            phone = phone[4:]
        elif phone.startswith('00221'):
            phone = phone[5:]
            
        # Vérifier la longueur (numéros sénégalais: 9 chiffres)
        if len(phone) == 9 and phone.startswith(('7', '3')):
            return f"+221{phone}"
        
        return None

    def is_quiet_hours(self) -> bool:
        """Vérifie si on est dans les heures de silence"""
        now = datetime.now().time()
        start_time = datetime.strptime(self.config['quiet_hours_start'], '%H:%M').time()
        end_time = datetime.strptime(self.config['quiet_hours_end'], '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # Cas où les heures passent minuit
            return now >= start_time or now <= end_time

    def can_send_alert(self, alert_type: str, phone_number: str) -> Tuple[bool, str]:
        """Vérifie si on peut envoyer une alerte avec système anti-spam avancé"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_hour = now.strftime('%Y-%m-%d-%H')
        
        # Vérifier si déjà envoyé aujourd'hui pour ce type
        daily_key = f"{phone_number}_{alert_type}_{today}"
        if daily_key in self.sent_alerts:
            return False, "Déjà envoyé aujourd'hui"
        
        # Vérifier limite quotidienne globale
        daily_count = sum(1 for k in self.sent_alerts.keys() 
                         if k.startswith(f"{phone_number}_") and k.endswith(f"_{today}"))
        
        if daily_count >= self.config['max_sms_per_day']:
            return False, f"Limite quotidienne atteinte ({daily_count})"
        
        # Vérifier limite horaire
        hourly_count = sum(1 for k, v in self.sent_alerts.items() 
                          if k.startswith(f"{phone_number}_") and 
                          v.get('timestamp', '').startswith(current_hour))
        
        if hourly_count >= self.config['max_sms_per_hour']:
            return False, "Limite horaire atteinte"
        
        return True, "OK"

    def generate_alert_message(self, alert_type: str, air_data: Dict, school_name: str, child_name: str) -> str:
        """Génère le message d'alerte personnalisé et optimisé"""
        pm25 = air_data.get('pm25', 0)
        co2 = air_data.get('co2', 400)
        status = air_data.get('status', 'Inconnue')
        timestamp = datetime.now().strftime('%H:%M')
        
        messages = {
            'pollution_high': f"🚨 ALERTE {school_name}\n"
                             f"Air très pollué pour {child_name}\n"
                             f"PM2.5: {pm25:.1f}µg/m³\n"
                             f"Surveillez: toux, fatigue\n"
                             f"Hydratation recommandée\n"
                             f"⏰ {timestamp}",
                            
            'pollution_moderate': f"⚠️ {school_name}\n"
                                 f"Air dégradé - {child_name}\n"
                                 f"PM2.5: {pm25:.1f}µg/m³\n"
                                 f"Surveillez son état au retour\n"
                                 f"⏰ {timestamp}",
                                
            'co2_high': f"💨 {school_name}\n"
                       f"CO2 élevé classe de {child_name}\n"
                       f"{co2:.0f} ppm\n"
                       f"Possible fatigue/concentration\n"
                       f"École informée\n"
                       f"⏰ {timestamp}",
                       
            'back_to_normal': f"✅ {school_name}\n"
                             f"Air redevenu bon pour {child_name}\n"
                             f"Activités normales OK\n"
                             f"⏰ {timestamp}",
                             
            'daily_report': f"📊 Rapport {school_name}\n"
                           f"{child_name}: Air {status}\n"
                           f"PM2.5 moyen: {pm25:.1f}µg/m³\n"
                           f"Qualité: {'Bonne' if pm25 <= 15 else 'Moyenne' if pm25 <= 35 else 'Mauvaise'}\n"
                           f"⏰ {timestamp}"
        }
        
        return messages.get(alert_type, f"Alerte {school_name}: {status} - {timestamp}")

    def send_sms_twilio(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Envoie SMS via Twilio avec retry et gestion d'erreurs"""
        max_retries = self.config.get('retry_attempts', 3)
        retry_delay = self.config.get('retry_delay_seconds', 60)
        
        for attempt in range(max_retries):
            try:
                client = Client(
                    self.config['twilio_account_sid'],
                    self.config['twilio_auth_token']
                )
                
                sms = client.messages.create(
                    body=message,
                    from_=self.config['twilio_phone_number'],
                    to=phone_number
                )
                
                logger.info(f"SMS envoyé avec succès à {phone_number} (SID: {sms.sid})")
                return True, f"Envoyé (SID: {sms.sid})"
                
            except Exception as e:
                logger.error(f"Tentative {attempt + 1}/{max_retries} échouée pour {phone_number}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return False, f"Échec après {max_retries} tentatives: {str(e)}"

    def send_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Point d'entrée principal pour l'envoi SMS"""
        if not self.config['enabled']:
            return False, "Système SMS désactivé"
        
        if self.is_quiet_hours():
            return False, "Heures de silence"
        
        provider = self.config['sms_provider']
        
        if provider == 'twilio':
            return self.send_sms_twilio(phone_number, message)
        else:
            return False, f"Provider SMS inconnu: {provider}"

    def send_alert_to_parents(self, alert_type: str, air_data: Dict, school_name: str, 
                            selected_classes: Optional[List[str]] = None) -> Tuple[List[Dict], int]:
        """Envoie une alerte à tous les parents concernés"""
        contacts = self.load_parent_contacts()
        results = []
        sent_count = 0
        
        for contact in contacts:
            # Filtrer par classe si spécifié
            if selected_classes and contact['classe'] not in selected_classes:
                continue
            
            phone = contact['telephone']
            child_name = contact['enfant']
            parent_name = contact['nom']
            
            # Vérifier si on peut envoyer
            can_send, reason = self.can_send_alert(alert_type, phone)
            if not can_send:
                results.append({
                    'parent': parent_name,
                    'phone': phone,
                    'child': child_name,
                    'status': 'Ignoré',
                    'reason': reason
                })
                continue
            
            # Générer et envoyer le message
            message = self.generate_alert_message(alert_type, air_data, school_name, child_name)
            success, send_reason = self.send_sms(phone, message)
            
            if success:
                # Marquer comme envoyé
                today = datetime.now().strftime('%Y-%m-%d')
                key = f"{phone}_{alert_type}_{today}"
                self.sent_alerts[key] = {
                    'timestamp': datetime.now().isoformat(),
                    'parent': parent_name,
                    'child': child_name,
                    'message': message[:100] + '...' if len(message) > 100 else message
                }
                sent_count += 1
                logger.info(f"Alerte {alert_type} envoyée à {parent_name} ({phone})")
            
            results.append({
                'parent': parent_name,
                'phone': phone,
                'child': child_name,
                'status': 'Envoyé' if success else 'Échec',
                'reason': send_reason
            })
        
        # Sauvegarder l'historique
        if sent_count > 0:
            self.save_sent_alerts()
            logger.info(f"Total {sent_count} SMS envoyés pour alerte {alert_type}")
        
        return results, sent_count

    def check_and_send_automatic_alerts(self, school_name: str) -> Tuple[List[Dict], int]:
        """
        Vérifie les conditions et envoie automatiquement des alertes
        """
        try:
            
            # Récupérer les données actuelles de l'école
            air_data = fetch_current_data(location_id, token)
            print("air_data:", air_data)
            air_data['pm25'] = 6000
            air_data['co2'] = 90000
            if not air_data:
                logger.warning("Aucune donnée de qualité d'air disponible")
                return [], 0
            
            pm25 = air_data.get('pm25', 0)
            co2 = air_data.get('co2', 400)
            
            alerts_sent = []
            total_sent = 0
            
            # Logique d'alerte basée sur les seuils
            if pm25 > self.config['pm25_danger_threshold']:
                results, count = self.send_alert_to_parents('pollution_high', air_data, school_name)
                alerts_sent.extend(results)
                total_sent += count
                
            elif pm25 > self.config['pm25_alert_threshold']:
                results, count = self.send_alert_to_parents('pollution_moderate', air_data, school_name)
                alerts_sent.extend(results)
                total_sent += count
            
            # Alerte CO2 indépendante
            if co2 > self.config['co2_alert_threshold']:
                results, count = self.send_alert_to_parents('co2_high', air_data, school_name)
                alerts_sent.extend(results)
                total_sent += count
            
            return alerts_sent, total_sent
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification automatique: {e}")
            return [], 0

    def start_automatic_monitoring(self, school_name: str) -> None:
        """Démarre la surveillance automatique en arrière-plan"""
        if self._running:
            logger.warning("Surveillance déjà en cours")
            return
            
        def monitoring_job():
            """Tâche de surveillance"""
            try:
                results, sent_count = self.check_and_send_automatic_alerts(school_name)
                if sent_count > 0:
                    logger.info(f"Surveillance auto: {sent_count} alertes envoyées")
            except Exception as e:
                logger.error(f"Erreur surveillance automatique: {e}")
        
        # Programmer la tâche
        interval = self.config.get('auto_check_interval_minutes', 30)
        schedule.every(interval).minutes.do(monitoring_job)
        
        def run_scheduler():
            """Boucle du scheduler"""
            while self._running:
                schedule.run_pending()
                time.sleep(60)  # Vérifier chaque minute
        
        self._running = True
        self._scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        logger.info(f"Surveillance automatique démarrée (intervalle: {interval}min)")

    def stop_automatic_monitoring(self) -> None:
        """Arrête la surveillance automatique"""
        self._running = False
        schedule.clear()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("Surveillance automatique arrêtée")

    def get_statistics(self) -> Dict:
        """Retourne des statistiques sur les envois SMS"""
        today = datetime.now().strftime('%Y-%m-%d')
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        today_count = len([k for k in self.sent_alerts.keys() if k.endswith(today)])
        week_count = len([k for k in self.sent_alerts.keys() 
                         if k.split('_')[-1] >= week_ago])
        total_count = len(self.sent_alerts)
        
        unique_parents = len(set(data.get('parent', '') for data in self.sent_alerts.values()))
        
        return {
            'sms_today': today_count,
            'sms_this_week': week_count,
            'sms_total': total_count,
            'unique_parents_contacted': unique_parents,
            'system_enabled': self.config['enabled'],
            'last_check': datetime.now().isoformat()
        }

    def check_air_quality_and_alert(self, school_name: str) -> Tuple[List[Dict], int]:
        """Vérifie la qualité d'air et envoie les alertes nécessaires"""
        try:
            air_data = fetch_current_data(location_id, token)
        
            if not air_data:
                logger.warning("Aucune donnée d'air disponible")
                return [], 0
            
            pm25 = air_data.get('pm25', 0)
            co2 = air_data.get('co2', 400)
            
            alerts_sent = []
            total_sent = 0
            
            # Logique d'alertes
            if pm25 > self.config['pm25_danger_threshold']:
                results, count = self.send_alert_to_parents('pollution_high', air_data, school_name)
                alerts_sent.extend(results)
                total_sent += count
                
            elif pm25 > self.config['pm25_alert_threshold']:
                results, count = self.send_alert_to_parents('pollution_moderate', air_data, school_name)
                alerts_sent.extend(results)
                total_sent += count
            
            if co2 > self.config['co2_alert_threshold']:
                results, count = self.send_alert_to_parents('co2_high', air_data, school_name)
                alerts_sent.extend(results)
                total_sent += count
            
            return alerts_sent, total_sent
            
        except Exception as e:
            logger.error(f"Erreur vérification automatique: {e}")
            return [], 0

# === FONCTIONS UTILITAIRES ===


def main():
    """Fonction principale de test"""
    logger.info("🚀 === DÉMARRAGE SYSTÈME SMS RESPIRE ===")
    
    # Créer les fichiers d'exemple si ils n'existent pas
    if not os.path.exists('sms_config.json'):
        create_sample_config()
        logger.warning("📝 Modifiez sms_config.json avec vos credentials !")
        return
    
    if not os.path.exists('parents_contacts_sms.txt'):
        create_sample_contacts()
        logger.warning("📝 Ajoutez vos contacts dans parents_contacts.txt !")
        return
    
    # Initialiser le système
    sms_system = SMSAlertSystem()
    
    logger.info("✅ Système opérationnel")
    
    # Test d'alerte (en mode mock par défaut)
    #  results, sent_count = sms_system.check_air_quality_and_alert(school_name="École Test")
    results, sent_count = sms_system.check_and_send_automatic_alerts("École Primaire Mamadou Calixte Dia")
    
    logger.info(f"📤 Envoi terminé: {sent_count} alertes envoyées")
        
    

if __name__ == "__main__":
    main()
    
    
    
"""


# === EXEMPLE D'UTILISATION ===

if __name__ == "__main__": 
    
    # Test d'initialisation
    sms_system = SMSAlertSystem()
    print("✅ Système initialisé")

    # Test de chargement des contacts
    contacts = sms_system.load_parent_contacts()
    print(f"📞 {len(contacts)} contacts chargés")

    # Afficher la configuration
    print(f"🔧 Provider: {sms_system.config['sms_provider']}")
    print(f"🔧 Système activé: {sms_system.config['enabled']}")
    
    # Test sur UN SEUL numéro d'abord !
    test_phone = "+221771616286"  # Remplacez par VOTRE numéro
    test_message = "🧪 Test RESPiRE Dashboard - Système SMS fonctionnel"

    success, reason = sms_system.send_sms(test_phone, test_message)
    print(f"📱 SMS Test: {'✅ Envoyé' if success else '❌ Échec'} - {reason}")
    

    # Test d'alerte automatique
    sms_system = SMSAlertSystem()
    results, sent_count = sms_system.check_and_send_automatic_alerts( 
        "École Primaire Mamadou Calixte Dia"
    )
    print(f"🔔 {sent_count} alertes envoyées")
    
    # Démarrer la surveillance automatique
    # sms_system.start_automatic_monitoring(example_fetch_air_data, "École Primaire Mamadou Dia")
    
    
"""