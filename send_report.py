
import os.path
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def get_authority_contacts(csv_path="data/autorite.csv"):
    """
    Récupère la liste des autorités avec nom et email depuis le CSV.
    Retourne une liste de dictionnaires : [{"nom": ..., "email": ...}, ...]
    """
    df = pd.read_csv(csv_path)

    # Supprimer les lignes où l'email est manquant
    df = df.dropna(subset=["email"])

    # Ne garder que les colonnes nécessaires
    contacts = df[["nom", "email"]].to_dict(orient="records")

    return contacts



def gmail_authenticate():
    """Authentifie et retourne le service Gmail API."""
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# ========================================
# ENVOI DE MAIL AVEC PJ
# ========================================
def send_email_with_attachment(service, sender, to, subject, body_text, file_path=None):
    """Envoie un e-mail via Gmail API avec pièce jointe."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Corps du message
    message.attach(MIMEText(body_text, 'plain'))

    # Pièce jointe
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        message.attach(part)

    # Encodage & envoi
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
    print(f"Message envoyé à {to} : {send_message['id']}")

# ========================================
# PIPELINE PRINCIPALE
# ========================================
def envoyer_rapport_aux_autorites(location_id, service, sender):
    """Génère et envoie un rapport personnalisé à chaque autorité."""
    contacts_autorites = get_authority_contacts()  # ← à implémenter selon ton CSV
    if not contacts_autorites:
        st.error("Aucun contact d'autorité trouvé pour envoyer le rapport.")
        return

    for contact in contacts_autorites:
        nom = contact["nom"]
        email = contact["email"]

        pdf_path = generate_report(location_id)

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

        send_email_with_attachment(service, sender, email, subject, body, pdf_path)

    st.success("✅ Rapports envoyés avec succès à toutes les autorités !")

# ========================================

# Bloc III Envoi de rapports aux autorités
    
#    service = gmail_authenticate()
#    envoyer_rapport_aux_autorites(
#        location_id="164928",
#       service=service,
#       sender=sender
#   )

    
# ========================================