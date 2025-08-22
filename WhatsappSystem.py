# WhatsappSystem.py
# Système d’alertes WhatsApp basé sur WaChap, compatible avec votre pipeline existant.
# Dépendances: requests, schedule, streamlit (pour secrets), twilio (facultatif si vous gardez l'ancien SMS), pandas (optionnel)
# pip install requests schedule streamlit

import os
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import requests
import schedule
import streamlit as st  # utilisé uniquement pour st.secrets si présent

# Vos dépendances existantes (conservent votre logique métier)
from src.functions import (
    fetch_current_data,
    calculer_iqa,
    afficher_iqa_plot,
    calculer_iqa_journalier,
    get_past_measures,
    calculate_air_quality_status,
)
from config.settings import token, BASE_URL, VALEURS_LIMITE, location_ids, DATA_DIR, liens


# ==============================
# OUTILS & LOGGING
# ==============================

def get_config_value(key: str, default: str = "") -> str:
    """Récupère une valeur depuis Streamlit secrets ou variables d'environnement."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("whatsapp_alerts.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ==============================
# CLASSE PRINCIPALE
# ==============================

class WhatsAppAlertSystem:
    """
    Système d'alertes WhatsApp via WaChap.
    - Anti-spam: limites horaires/quotidiennes, mémorisation par type d’alerte.
    - Heures de silence: pas d’envoi entre quiet_hours_start et quiet_hours_end.
    - Envoi texte et média (PDF/Images) via WaChap.
    - Monitoring automatique avec schedule (thread).
    """

    def __init__(
        self,
        contacts_file: str = "parents_contacts_wa.txt",
        config_file: str = "whatsapp_config.json",
        sent_alerts_file: str = "whatsapp_sent_alerts.json",
        rate_limit_file: str = "whatsapp_rate_limits.json",
    ):
        self.contacts_file = contacts_file
        self.config_file = config_file
        self.sent_alerts_file = sent_alerts_file
        self.rate_limit_file = rate_limit_file

        self.default_config: Dict = {
            # Provider
            "sms_provider": "wachap",  # "wachap" (recommandé) | "twilio" (optionnel legacy)
            # WaChap
            "wachap_base_url": "https://wachap.app/api",
            "wachap_access_token": get_config_value("WACHAP_ACCESS_TOKEN", ""),
            "wachap_instance_id": get_config_value("WACHAP_INSTANCE_ID", ""),
            # Throttling
            "max_whatsapp_per_day": 5,
            "max_whatsapp_per_hour": 2,
            # Quiet hours (HH:MM 24h)
            "quiet_hours_start": "21:00",
            "quiet_hours_end": "07:00",
            # Seuils AQI/Capteurs
            "pm25_alert_threshold": 35,     # ajustez selon vos besoins
            "pm25_danger_threshold": 150,   # OMS ~ dangereux >150 µg/m3
            "co2_alert_threshold": 1000,    # ppm
            # Système
            "enabled": True,
            "auto_check_interval_minutes": 30,
            "retry_attempts": 3,
            "retry_delay_seconds": 60,
        }

        # Réparation fichiers, puis chargements
        self.repair_corrupted_files()
        self.load_config()
        self.load_sent_alerts()
        self.load_rate_limits()

        # Thread scheduler
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None

        logger.info("✅ WhatsAppAlertSystem initialisé")

    # ------------------------------
    # Gestion fichiers & configuration
    # ------------------------------

    def repair_corrupted_files(self) -> None:
        """Répare les fichiers JSON corrompus (sent_alerts, rate_limits, config)."""
        files_to_check = [
            (self.sent_alerts_file, "sent_alerts"),
            (self.rate_limit_file, "rate_limits"),
            (self.config_file, "config"),
        ]
        for file_path, _ in files_to_check:
            if not os.path.exists(file_path):
                continue
            try:
                if os.path.getsize(file_path) == 0:
                    logger.warning(f"Fichier vide supprimé: {file_path}")
                    os.remove(file_path)
                    continue
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    logger.warning(f"Contenu vide supprimé: {file_path}")
                    os.remove(file_path)
                    continue
                json.loads(content)  # test parse
            except json.JSONDecodeError:
                backup = f"{file_path}.corrupt.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(file_path, backup)
                logger.error(f"Fichier corrompu sauvegardé: {backup}")
            except Exception as e:
                logger.error(f"Erreur vérification {file_path}: {e}")

    def load_config(self) -> None:
        """Charge et valide la configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.config = {**self.default_config, **loaded}
            else:
                self.config = self.default_config.copy()
                self.save_config()
            self._validate_config()
            logger.info("Configuration chargée.")
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
            self.config = self.default_config.copy()

    def _validate_config(self) -> None:
        if self.config.get("sms_provider") == "wachap":
            req = ["wachap_access_token", "wachap_instance_id", "wachap_base_url"]
            missing = [k for k in req if not self.config.get(k)]
            if missing:
                logger.warning(f"Configuration WaChap incomplète: {missing}")

    def save_config(self) -> None:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Configuration sauvegardée.")
        except Exception as e:
            logger.error(f"Erreur sauvegarde config: {e}")

    def load_sent_alerts(self) -> None:
        """Charge l'historique d'envois (clé: phone_alerttype_YYYY-MM-DD)."""
        try:
            if os.path.exists(self.sent_alerts_file):
                with open(self.sent_alerts_file, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                self.sent_alerts = json.loads(raw) if raw else {}
            else:
                self.sent_alerts = {}
                self.save_sent_alerts()

            self._cleanup_old_alerts()
        except Exception as e:
            logger.error(f"Erreur load_sent_alerts: {e}")
            self.sent_alerts = {}
            self.save_sent_alerts()

    def save_sent_alerts(self) -> None:
        try:
            with open(self.sent_alerts_file, "w", encoding="utf-8") as f:
                json.dump(self.sent_alerts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur save_sent_alerts: {e}")

    def _cleanup_old_alerts(self) -> None:
        """Nettoie les entrées > 30 jours."""
        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        keys_to_remove = []
        for k in list(self.sent_alerts.keys()):
            try:
                d = k.split("_")[-1]
                if d < cutoff:
                    keys_to_remove.append(k)
            except Exception:
                continue
        for k in keys_to_remove:
            self.sent_alerts.pop(k, None)
        if keys_to_remove:
            self.save_sent_alerts()
            logger.info(f"Historique nettoyé: {len(keys_to_remove)} clés retirées")

    def load_rate_limits(self) -> None:
        try:
            if os.path.exists(self.rate_limit_file):
                with open(self.rate_limit_file, "r", encoding="utf-8") as f:
                    self.rate_limits = json.load(f)
            else:
                self.rate_limits = {}
        except Exception:
            self.rate_limits = {}

    def save_rate_limits(self) -> None:
        try:
            with open(self.rate_limit_file, "w", encoding="utf-8") as f:
                json.dump(self.rate_limits, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur save_rate_limits: {e}")

    # ------------------------------
    # Contacts & numéros
    # ------------------------------

    def load_parent_contacts(self) -> List[Dict]:
        """
        Fichier texte, 1 contact par ligne (sans en-tête):
        Nom Parent, +221771234567, Nom Enfant, Classe
        Lignes commençant par # ignorées.
        """
        contacts: List[Dict] = []
        try:
            if not os.path.exists(self.contacts_file):
                logger.warning(f"Fichier contacts absent: {self.contacts_file}")
                return contacts

            with open(self.contacts_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) < 4:
                        logger.warning(f"Ligne mal formée ({i}): {line}")
                        continue
                    phone_norm = self._normalize_phone_number(parts[1])
                    if not phone_norm:
                        logger.warning(f"Numéro invalide ({i}): {parts[1]}")
                        continue
                    contacts.append(
                        {
                            "nom": parts[0],
                            "telephone": phone_norm,
                            "enfant": parts[2],
                            "classe": parts[3],
                            "line_num": i,
                        }
                    )
            logger.info(f"{len(contacts)} contacts chargés.")
        except Exception as e:
            logger.error(f"Erreur lecture contacts: {e}")
        return contacts

    def _normalize_phone_number(self, phone: str) -> Optional[str]:
        """Normalise un numéro sénégalais en format international +221XXXXXXXXX (9 chiffres après indicatif)."""
        if not phone:
            return None
        digits = "".join(ch for ch in phone if ch.isdigit())
        # Retirer préfixes possibles
        if digits.startswith("00221"):
            digits = digits[5:]
        elif digits.startswith("221"):
            digits = digits[3:]
        # À ce stade 'digits' peut être 9 chiffres locaux
        if len(digits) == 9 and digits[0] in ("7", "3"):
            return f"+221{digits}"
        return None

    def _to_wachap_number(self, phone_plus: str) -> str:
        """
        WaChap attend un 'number' numérique sans '+'.
        - Si +221xxxxxxxxx => 221xxxxxxxxx
        - Si 9 chiffres => préfixer 221
        - Si déjà 221xxxxxxxxx => renvoyer tel quel
        """
        d = "".join(ch for ch in phone_plus if ch.isdigit())
        if len(d) == 9:  # local
            return "221" + d
        if d.startswith("221") and len(d) == 12:
            return d
        # fallback
        return d

    # ------------------------------
    # Fenêtre de silence & anti-spam
    # ------------------------------

    def is_quiet_hours(self) -> bool:
        now = datetime.now().time()
        start = datetime.strptime(self.config["quiet_hours_start"], "%H:%M").time()
        end = datetime.strptime(self.config["quiet_hours_end"], "%H:%M").time()
        if start <= end:
            return start <= now <= end
        # chevauche minuit
        return now >= start or now <= end

    def can_send_alert(self, alert_type: str, phone_number: str) -> Tuple[bool, str]:
        """
        Anti-spam:
        - 1 msg/alert_type/jour/parent
        - max_whatsapp_per_hour
        - max_whatsapp_per_day
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        cur_hour_prefix = now.strftime("%Y-%m-%d-%H")

        # 1) Déjà envoyé ce type aujourd'hui ?
        daily_key = f"{phone_number}_{alert_type}_{today}"
        if daily_key in self.sent_alerts:
            return False, "Déjà envoyé aujourd'hui"

        # 2) Limite quotidienne
        per_day = sum(
            1 for k in self.sent_alerts.keys() if k.startswith(f"{phone_number}_") and k.endswith(f"_{today}")
        )
        if per_day >= self.config["max_whatsapp_per_day"]:
            return False, "Limite quotidienne atteinte"

        # 3) Limite horaire
        per_hour = sum(
            1 for k, v in self.sent_alerts.items()
            if k.startswith(f"{phone_number}_") and v.get("timestamp", "").startswith(cur_hour_prefix)
        )
        if per_hour >= self.config["max_whatsapp_per_hour"]:
            return False, "Limite horaire atteinte"

        return True, "OK"

    # ------------------------------
    # Contenu des messages
    # ------------------------------

    def generate_alert_message(self, alert_type: str, air_data: Dict, school_name: str, child_name: str) -> str:
        pm25 = float(air_data.get("pm25", 0) or 0)
        co2 = float(air_data.get("co2", 400) or 400)
        status = air_data.get("status", "Inconnue")
        ts = datetime.now().strftime("%H:%M")

        messages = {
            "pollution_high": (
                f"🚨 {school_name}\n"
                f"Air très pollué pour {child_name}\n"
                f"PM2.5: {pm25:.1f} µg/m³\n"
                f"Hydratation & repos conseillés\n"
                f"⏰ {ts}"
            ),
            "pollution_moderate": (
                f"⚠️ {school_name}\n"
                f"Air dégradé – {child_name}\n"
                f"PM2.5: {pm25:.1f} µg/m³\n"
                f"Surveillez son état au retour\n"
                f"⏰ {ts}"
            ),
            "co2_high": (
                f"💨 {school_name}\n"
                f"CO₂ élevé en classe de {child_name}\n"
                f"{co2:.0f} ppm – possible fatigue\n"
                f"Équipe informée\n"
                f"⏰ {ts}"
            ),
            "back_to_normal": (
                f"✅ {school_name}\n"
                f"Air redevenu bon pour {child_name}\n"
                f"Activités normales OK\n"
                f"⏰ {ts}"
            ),
            "daily_report": (
                f"📊 Rapport {school_name}\n"
                f"{child_name}: Air {status}\n"
                f"PM2.5 moy.: {pm25:.1f} µg/m³\n"
                f"⏰ {ts}"
            ),
        }
        return messages.get(alert_type, f"{school_name}: {status} ({ts})")

    # ------------------------------
    # ENVOIS WACHAP
    # ------------------------------

    def send_wachap_message(
        self,
        phone_number: str,
        message: str,
        msg_type: str = "text",
        media_url: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Envoi via WaChap /api/send (POST JSON).
        Payload attendu:
        {
            "number": "221771234567",
            "type": "text" | "media",
            "message": "...",
            "instance_id": "...",
            "access_token": "...",
            "media_url": "https://.../file.pdf",   # si type=media
            "filename": "file.pdf"                 # optionnel
        }
        """
        url = f'{self.config["wachap_base_url"].rstrip("/")}/send'
        number = self._to_wachap_number(phone_number)

        payload: Dict[str, str] = {
            "number": number,
            "type": "media" if msg_type == "media" else "text",
            "message": message,
            "instance_id": self.config["wachap_instance_id"],
            "access_token": self.config["wachap_access_token"],
        }
        if payload["type"] == "media":
            if not media_url:
                return False, "media_url requis pour type=media"
            payload["media_url"] = media_url
            if filename:
                payload["filename"] = filename

        try:
            r = requests.post(url, json=payload, timeout=20)
            if r.status_code != 200:
                logger.error(f"WaChap HTTP {r.status_code}: {r.text[:300]}")
                return False, f"HTTP {r.status_code}"

            # Réponses possibles: {"status":"success"} | {"success":true} | { ... }
            try:
                data = r.json()
            except Exception:
                data = {}

            success_flags = {
                str(data.get("status", "")).lower() in {"success", "ok", "true"},
                data.get("success") is True,
            }
            if True in success_flags or not isinstance(data, dict):
                msg_id = data.get("message_id") or data.get("id") or "no-id"
                return True, f"Envoyé (id: {msg_id})"

            logger.error(f"Réponse WaChap inattendue: {data}")
            return False, "Réponse inattendue WaChap"
        except Exception as e:
            logger.exception("Erreur envoi WaChap")
            return False, f"Erreur WaChap: {e}"

    def send_message(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Routeur unique (ici WaChap).
        Applique: enabled + quiet hours.
        """
        if not self.config.get("enabled", True):
            return False, "Système désactivé"
        if self.is_quiet_hours():
            return False, "Heures de silence"

        # Utilise WaChap par défaut
        return self.send_wachap_message(phone_number, message)

    # ------------------------------
    # Envoi par lot aux parents
    # ------------------------------

    def send_alert_to_parents(
        self,
        alert_type: str,
        air_data: Dict,
        school_name: str,
        selected_classes: Optional[List[str]] = None,
    ) -> Tuple[List[Dict], int]:
        """
        Parcourt le fichier de contacts et envoie les alertes aux parents filtrés.
        Retourne (résultats détaillés, total envoyés).
        """
        contacts = self.load_parent_contacts()
        results: List[Dict] = []
        sent_count = 0

        for c in contacts:
            if selected_classes and c["classe"] not in selected_classes:
                continue

            phone = c["telephone"]
            child = c["enfant"]
            parent = c["nom"]

            can, why = self.can_send_alert(alert_type, phone)
            if not can:
                results.append(
                    {
                        "parent": parent,
                        "phone": phone,
                        "child": child,
                        "status": "Ignoré",
                        "reason": why,
                    }
                )
                continue

            msg = self.generate_alert_message(alert_type, air_data, school_name, child)
            ok, info = self.send_message(phone, msg)

            if ok:
                today = datetime.now().strftime("%Y-%m-%d")
                key = f"{phone}_{alert_type}_{today}"
                self.sent_alerts[key] = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
                    "parent": parent,
                    "child": child,
                    "message": msg[:100] + "..." if len(msg) > 100 else msg,
                }
                sent_count += 1

            results.append(
                {
                    "parent": parent,
                    "phone": phone,
                    "child": child,
                    "status": "Envoyé" if ok else "Échec",
                    "reason": info,
                }
            )

        if sent_count > 0:
            self.save_sent_alerts()
            logger.info(f"{sent_count} messages envoyés pour {alert_type}")

        return results, sent_count

    # ------------------------------
    # Vérification & monitoring
    # ------------------------------

    def check_air_quality_and_alert(self, school_name: str, location_id: int) -> Tuple[List[Dict], int]:
        """
        Récupère les données actuelles d'une école, applique la logique d'alertes et envoie si besoin.
        """
        try:
            air_data = fetch_current_data(location_id, token)
            if not air_data:
                logger.warning("Aucune donnée de qualité d'air.")
                return [], 0

            pm25 = float(air_data.get("pm25", 0) or 0)
            co2 = float(air_data.get("co2", 400) or 400)

            alerts_sent: List[Dict] = []
            total_sent = 0

            if pm25 >= self.config["pm25_danger_threshold"]:
                r, n = self.send_alert_to_parents("pollution_high", air_data, school_name)
                alerts_sent += r
                total_sent += n
            elif pm25 >= self.config["pm25_alert_threshold"]:
                r, n = self.send_alert_to_parents("pollution_moderate", air_data, school_name)
                alerts_sent += r
                total_sent += n

            if co2 >= self.config["co2_alert_threshold"]:
                r, n = self.send_alert_to_parents("co2_high", air_data, school_name)
                alerts_sent += r
                total_sent += n

            return alerts_sent, total_sent

        except Exception as e:
            logger.error(f"Erreur AQ check: {e}")
            return [], 0

    def check_and_send_automatic_alerts(self, school_name: str, location_id: int) -> Tuple[List[Dict], int]:
        """Alias lisible."""
        return self.check_air_quality_and_alert(school_name, location_id)

    def start_automatic_monitoring(self, school_name: str, location_id: int) -> None:
        """
        Démarre un thread de surveillance qui exécute la vérification périodiquement.
        """
        if self._running:
            logger.warning("Monitoring déjà en cours.")
            return

        interval = int(self.config.get("auto_check_interval_minutes", 30))

        def monitoring_job():
            try:
                _, sent = self.check_and_send_automatic_alerts(school_name, location_id)
                if sent > 0:
                    logger.info(f"Surveillance: {sent} alertes envoyées.")
            except Exception as e:
                logger.error(f"Erreur monitoring_job: {e}")

        schedule.clear()  # garde-fou
        schedule.every(interval).minutes.do(monitoring_job)

        def run_scheduler():
            while self._running:
                schedule.run_pending()
                time.sleep(60)

        self._running = True
        self._scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self._scheduler_thread.start()
        logger.info(f"Surveillance démarrée (intervalle: {interval} min).")

    def stop_automatic_monitoring(self) -> None:
        self._running = False
        schedule.clear()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("Surveillance arrêtée.")

    # ------------------------------
    # Stats & utilitaires WaChap
    # ------------------------------

    def get_statistics(self) -> Dict:
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today_count = len([k for k in self.sent_alerts if k.endswith(today)])
        week_count = len([k for k in self.sent_alerts if k.split("_")[-1] >= week_ago])
        total_count = len(self.sent_alerts)
        unique_parents = len({d.get("parent", "") for d in self.sent_alerts.values()})
        return {
            "wa_today": today_count,
            "wa_this_week": week_count,
            "wa_total": total_count,
            "unique_parents_contacted": unique_parents,
            "system_enabled": self.config.get("enabled", True),
            "last_check": datetime.now().isoformat(),
        }

    def wachap_set_webhook(self, webhook_url: str, enable: bool = True) -> Tuple[bool, str]:
        """Optionnel: configurer un webhook de réception côté WaChap (si disponible)."""
        try:
            url = f'{self.config["wachap_base_url"].rstrip("/")}/set_webhook'
            params = {
                "webhook_url": webhook_url,
                "enable": "true" if enable else "false",
                "instance_id": self.config["wachap_instance_id"],
                "access_token": self.config["wachap_access_token"],
            }
            r = requests.get(url, params=params, timeout=20)
            return (r.status_code == 200, f"HTTP {r.status_code}")
        except Exception as e:
            return False, f"Erreur set_webhook: {e}"


# ==============================
# EXEMPLE D’UTILISATION (facultatif)
# ==============================

if __name__ == "__main__":
    # 1) Secrets à définir:
    #   WACHAP_ACCESS_TOKEN, WACHAP_INSTANCE_ID (via st.secrets ou variables d'env)
    # 2) Fichier contacts "parents_contacts_wa.txt"
    #    Format: Nom Parent, +221771234567, Nom Enfant, Classe

    school = "École Primaire Mamadou Calixte Dia"
    loc_id = location_ids[6] if len(location_ids) > 6 else location_ids[0]

    wa = WhatsAppAlertSystem()
    logger.info("Test d'envoi unitaire…")

    # Test simple (assurez-vous que le numéro a opt-in côté WhatsApp Business/WaChap)
    test_phone = os.getenv("TEST_PHONE", "+221771616286")
    ok, info = wa.send_message(test_phone, "🧪 Test RESPiRE – WaChap opérationnel ✔")
    logger.info(f"SendMessage: {ok} | {info}")

    # Test logique AQ + alertes
    results, sent = wa.check_and_send_automatic_alerts(school, loc_id)
    logger.info(f"Alerte AQ: {sent} envoyés")

    # Lancer le monitoring automatique (Ctrl+C pour stopper si script standalone)
    # wa.start_automatic_monitoring(school, loc_id)
    # time.sleep(5 * 60)
    # wa.stop_automatic_monitoring()
