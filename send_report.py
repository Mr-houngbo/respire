import os
import json
import base64
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
from google.oauth2 import service_account
from report_generator import *

# Scopes Gmail
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_authority_contacts(csv_path="data/autorite.csv"):
    """
    Récupère la liste des autorités avec nom et email depuis le CSV.
    Retourne une liste de dictionnaires : [{"nom": ..., "email": ...}, ...]
    """
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["email"])  # Supprimer les lignes sans email
    return df[["nom", "email"]].to_dict(orient="records")

def load_credentials_from_env():
    """
    Charge les credentials Google depuis GOOGLE_CREDENTIALS_JSON (GitHub Secret).
    Retourne un objet Credentials pour Gmail API.
    """
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not credentials_json:
        raise ValueError("❌ GOOGLE_CREDENTIALS_JSON n'est pas défini dans les variables d'environnement")

    try:
        credentials_dict = json.loads(credentials_json)
    except json.JSONDecodeError:
        raise ValueError("❌ GOOGLE_CREDENTIALS_JSON contient un JSON invalide")

    creds = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=SCOPES
    )

    return creds

def gmail_authenticate():
    """Authentifie et retourne le service Gmail API via compte de service."""
    creds = load_credentials_from_env()
    service = build("gmail", "v1", credentials=creds)
    return service

def send_email_with_attachment(service, sender, to, subject, body_text, file_path=None):
    """Envoie un e-mail via Gmail API avec pièce jointe."""
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    # Corps du message
    message.attach(MIMEText(body_text, "plain"))

    # Pièce jointe
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_path)}"'
        message.attach(part)

    try:
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        print(f"📩 Message envoyé à {to} : {send_message['id']}")
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi à {to}: {e}")
        return False

def envoyer_rapport_aux_autorites(location_id, service, sender):
    """Génère et envoie un rapport personnalisé à chaque autorité."""
    try:
        contacts_autorites = get_authority_contacts()
        if not contacts_autorites:
            print("❌ Aucun contact trouvé dans autorite.csv")
            return False

        success_count = 0
        total_count = len(contacts_autorites)

        for contact in contacts_autorites:
            nom = contact["nom"]
            email = contact["email"]

            # Génération du rapport PDF
            pdf_path = test_professional_report()

            subject = "Rapport Qualité de l'air - École"
            body = (
                f"Bonjour {nom},\n\n"
                "Voici votre rapport personnalisé sur la qualité de l'air dans votre zone.\n"
                "Il contient :\n"
                " - Les mesures actuelles\n"
                " - Les prévisions pour demain et la semaine prochaine\n"
                " - Les recommandations adaptées à votre niveau de priorité\n\n"
                "Nous comptons sur votre engagement pour sensibiliser et agir.\n\n"
                "Cordialement,\n"
                "L'équipe Respire"
            )

            if send_email_with_attachment(service, sender, email, subject, body, pdf_path):
                success_count += 1

        print(f"✅ Rapports envoyés avec succès : {success_count}/{total_count}")
        return success_count == total_count

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi des rapports: {e}")
        return False

# ========================================
# MAIN
# ========================================
def main():
    """Fonction principale pour lancer l'envoi de rapports."""
    try:
        # Authentification Gmail API via compte de service
        service = gmail_authenticate()

        # Email expéditeur
        sender = os.getenv("SENDER_EMAIL", "houngbo.calixte.r@gmail.com")

        # Location ID (par défaut 164928)
        location_id = os.getenv("LOCATION_ID", "164928")

        # Envoi des rapports
        success = envoyer_rapport_aux_autorites(
            location_id=location_id,
            service=service,
            sender=sender
        )

        if success:
            print("🎉 Tous les rapports ont été envoyés avec succès!")
        else:
            print("⚠️ Certains rapports n'ont pas pu être envoyés.")

    except Exception as e:
        print(f"❌ Erreur dans le processus principal: {e}")

if __name__ == "__main__":
    main()
