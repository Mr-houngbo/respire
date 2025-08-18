import os
import json
import base64
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
from report_generator import *
# Scopes Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

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

def load_credentials_from_env():
    """
    Charge les credentials Google depuis les variables d'environnement.
    Retourne un dictionnaire de credentials ou None.
    """
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not credentials_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON n'est pas défini dans les variables d'environnement")
    
    try:
        return json.loads(credentials_json)
    except json.JSONDecodeError:
        raise ValueError("GOOGLE_CREDENTIALS_JSON contient un JSON invalide")

def load_token_from_env():
    """
    Charge le token depuis les variables d'environnement.
    Retourne un dictionnaire de token ou None.
    """
    token_json = os.getenv('GOOGLE_TOKENS_JSON')
    if not token_json:
        return None
    
    try:
        return json.loads(token_json)
    except json.JSONDecodeError:
        print("Warning: GOOGLE_TOKENS_JSON contient un JSON invalide")
        return None

def save_token_to_env_format(creds):
    """
    Convertit les credentials en format JSON pour sauvegarde.
    En production, vous devriez sauvegarder ceci comme nouveau secret.
    """
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    return json.dumps(token_data)

def gmail_authenticate():
    """Authentifie et retourne le service Gmail API en utilisant les secrets GitHub."""
    
    creds = None
    
    # Essayer de charger le token existant depuis les variables d'environnement
    token_data = load_token_from_env()
    if token_data:
        try:
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"Erreur lors du chargement du token: {e}")
            creds = None
    
    # Vérifier si les credentials sont valides
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # En production, vous devriez mettre à jour le secret GOOGLE_TOKEN_JSON
                new_token = save_token_to_env_format(creds)
                print("Token rafraîchi. Mettez à jour GOOGLE_TOKEN_JSON avec:")
                print(new_token)
            except Exception as e:
                print(f"Erreur lors du rafraîchissement: {e}")
                creds = None
        
        if not creds:
            # Authentification initiale avec les credentials
            credentials_dict = load_credentials_from_env()
            
            # Pour l'environnement de production/CI, utiliser le flow sans serveur local
            if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
                # En CI/CD, vous devez gérer l'authentification différemment
                # Par exemple, utiliser un service account ou un token pré-autorisé
                raise RuntimeError(
                    "Authentification interactive non disponible en CI/CD. "
                    "Assurez-vous que GOOGLE_TOKEN_JSON contient un token valide."
                )
            else:
                # Développement local uniquement
                flow = InstalledAppFlow.from_client_config(credentials_dict, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Afficher le token pour mise à jour manuelle du secret
                new_token = save_token_to_env_format(creds)
                print("Nouveau token généré. Mettez à jour GOOGLE_TOKEN_JSON avec:")
                print(new_token)
    
    return build('gmail', 'v1', credentials=creds)

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
    try:
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Message envoyé à {to} : {send_message['id']}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi à {to}: {e}")
        return False

def envoyer_rapport_aux_autorites(location_id, service, sender):
    """Génère et envoie un rapport personnalisé à chaque autorité."""
    try:
        contacts_autorites = get_authority_contacts()
        if not contacts_autorites:
            print("Erreur: Aucun contact d'autorité trouvé pour envoyer le rapport.")
            return False

        success_count = 0
        total_count = len(contacts_autorites)

        for contact in contacts_autorites:
            nom = contact["nom"]
            email = contact["email"]

            # Générer le rapport (fonction à implémenter)
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
        print(f"Erreur lors de l'envoi des rapports: {e}")
        return False

# ========================================
# EXEMPLE D'UTILISATION
# ========================================

def main():
    """Fonction principale pour tester l'envoi de rapports."""
    try:
        # Authentification
        service = gmail_authenticate()
        
        # Configuration
        sender = "houngbo.calixte.r@gmail.com"  # À remplacer par votre email
        location_id = "164928"
        
        # Envoi des rapports
        success = envoyer_rapport_aux_autorites(
            location_id=location_id,
            service=service,
            sender=sender
        )
        
        if success:
            print("Tous les rapports ont été envoyés avec succès!")
        else:
            print("Certains rapports n'ont pas pu être envoyés.")
            
    except Exception as e:
        print(f"Erreur dans le processus principal: {e}")

if __name__ == "__main__":
    main()

# ========================================
# NOTES IMPORTANTES:
# ========================================
# 1. Définir ces variables d'environnement ou secrets GitHub:
#    - GOOGLE_CREDENTIALS_JSON: contenu de credentials.json
#    - GOOGLE_TOKEN_JSON: contenu de token.json (après première auth)
#
# 2. Pour GitHub Actions, ajoutez dans votre workflow:
#    env:
#      GOOGLE_CREDENTIALS_JSON: ${{ secrets.GOOGLE_CREDENTIALS_JSON }}
#      GOOGLE_TOKEN_JSON: ${{ secrets.GOOGLE_TOKEN_JSON }}
#
# 3. La fonction generate_report() doit être implémentée séparément
#
# 4. En production, gérez les erreurs d'authentification de manière appropriée

