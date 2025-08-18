import os
import pandas as pd
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from report_generator import *

def get_authority_contacts(csv_path="data/autorite.csv"):
    """Charge la liste des autorités depuis un CSV."""
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["email"])
    return df[["nom", "email"]].to_dict(orient="records")

def send_email_smtp(sender, password, to, subject, body_text, file_path=None):
    """Envoie un mail via SMTP Gmail avec option pièce jointe."""
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject

    # Corps du message
    msg.attach(MIMEText(body_text, "plain"))

    # Pièce jointe
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to, msg.as_string())
        print(f"📩 Email envoyé à {to}")
        return True
    except Exception as e:
        print(f"⚠️ Erreur SMTP lors de l'envoi à {to}: {e}")
        return False

def envoyer_rapport_aux_autorites(location_id, sender, password):
    """Génère et envoie un rapport personnalisé à chaque autorité."""
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

        if send_email_smtp(sender, password, email, subject, body, pdf_path):
            success_count += 1

    print(f"✅ Rapports envoyés avec succès : {success_count}/{total_count}")
    return success_count == total_count

def main():
    """Point d'entrée principal."""
    sender = os.getenv("SENDER_EMAIL", "houngbo.calixte.r@gmail.com")
    password = os.getenv("GMAIL_APP_PASSWORD")  # ⚠️ à définir dans GitHub Secrets
    location_id = os.getenv("LOCATION_ID", "164928")

    if not password:
        raise ValueError("❌ Variable d'environnement GMAIL_APP_PASSWORD manquante")

    success = envoyer_rapport_aux_autorites(location_id, sender, password)

    if success:
        print("🎉 Tous les rapports envoyés avec succès!")
    else:
        print("⚠️ Certains rapports n'ont pas pu être envoyés.")

if __name__ == "__main__":
    main()
