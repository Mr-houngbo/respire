import os
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from report_generator import *


def get_authority_contacts(csv_path="data/autorite.csv"):
    """Charge la liste des autorités depuis un CSV."""
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["email"])
    return df[["nom", "email"]].to_dict(orient="records")


def send_email_sendgrid(sender, to, subject, body_text, file_path=None):
    """Envoie un mail via SendGrid avec option pièce jointe."""
    message = Mail(
        from_email=sender,
        to_emails=to,
        subject=subject,
        plain_text_content=body_text,
    )

    # Pièce jointe
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            encoded_file = base64.b64encode(data).decode()
        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName(os.path.basename(file_path)),
            FileType("application/pdf"),
            Disposition("attachment"),
        )
        message.attachment = attachedFile

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"📩 Email envoyé à {to} (status {response.status_code})")
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"⚠️ Erreur SendGrid lors de l'envoi à {to}: {e}")
        return False


def envoyer_rapport_aux_autorites(location_id, sender):
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

        if send_email_sendgrid(sender, email, subject, body, pdf_path):
            success_count += 1

    print(f"✅ Rapports envoyés avec succès : {success_count}/{total_count}")
    return success_count == total_count


def main():
    """Point d'entrée principal."""
    sender = os.getenv("SENDER_EMAIL", "houngbo.calixte.r@gmail.com")  # doit être validé dans SendGrid
    location_id = os.getenv("LOCATION_ID", "164928")

    if not os.getenv("SENDGRID_API_KEY"):
        raise ValueError("❌ Variable d'environnement SENDGRID_API_KEY manquante")

    success = envoyer_rapport_aux_autorites(location_id, sender)

    if success:
        print("🎉 Tous les rapports envoyés avec succès!")
    else:
        print("⚠️ Certains rapports n'ont pas pu être envoyés.")


if __name__ == "__main__":
    main()
