import os
import bcrypt
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader




CONFIG_PATH = os.path.join("data", "config.yaml")

# Charger les utilisateurs depuis le fichier YAML
def charger_utilisateurs():
    if not os.path.exists(CONFIG_PATH):
        return {
            "credentials": {"usernames": {}},
            "cookie": {"name": "respire", "key": "cle_secrete", "expiry_days": 1},
        }

    with open(CONFIG_PATH, "r") as filem:
        config = yaml.load(filem, Loader=SafeLoader)

    if config is None:
        config = {
            "credentials": {"usernames": {}},
            "cookie": {"name": "respire", "key": "cle_secrete", "expiry_days": 1},
        }

    return config

# Enregistrer un nouvel utilisateur dans le fichier YAML
def enregistrer_utilisateur(username, name, password):
    config = charger_utilisateurs()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    config["credentials"]["usernames"][username] = {
        "name": name,
        "password": hashed_pw
    }

    with open(CONFIG_PATH, "w") as filem:
        yaml.dump(config, filem)

# Créer l'objet authenticator
def creer_authenticator():
    config = charger_utilisateurs()
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )
    return authenticator

def connexionn(login_result):
    #login_result = authenticator.login(location="main")
    if login_result:
        name, auth_status, username = login_result
        if auth_status:
            st.success(f"Bienvenue {name} 👋🏾")
            return True
        elif auth_status is False:
            st.error("Nom d’utilisateur ou mot de passe incorrect.")
        else:
            st.warning("Veuillez entrer vos identifiants.")
    return False

def inscriptionn():
    with st.form("inscription_formulaire"):
            name = st.text_input("Nom complet")
            username = st.text_input("Nom d’utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("S’inscrire")

    if submit:
        if name and username and password:
            try:
                utilisateurs = charger_utilisateurs()
                if username in utilisateurs["credentials"]["usernames"]:
                    st.error("Ce nom d’utilisateur existe déjà.")
                else:
                    enregistrer_utilisateur(username, name, password)
                    st.success("✅ Inscription réussie. Vous pouvez maintenant vous connecter.")
            except Exception as e:
                st.error(f"Erreur lors de l’inscription : {e}")
        else:
            st.warning("Merci de remplir tous les champs.")
    return False





# Afficher le formulaire de connexion/inscription
"""def afficher_formulaire():
    authenticator = creer_authenticator()
    action = st.radio("Choisissez une action", ["Connexion", "Créer un compte"])
    if action == "Connexion":
        login_result = authenticator.login(location="main")
        if login_result:
            name, auth_status, username = login_result
            if auth_status:
                st.success(f"Bienvenue {name} 👋🏾")
                return True
            elif auth_status is False:
                st.error("Nom d’utilisateur ou mot de passe incorrect.")
            else:
                st.warning("Veuillez entrer vos identifiants.")
        return False

    
    else:
        with st.form("inscription_formulaire"):
            name = st.text_input("Nom complet")
            username = st.text_input("Nom d’utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("S’inscrire")

        if submit:
            if name and username and password:
                try:
                    utilisateurs = charger_utilisateurs()
                    if username in utilisateurs["credentials"]["usernames"]:
                        st.error("Ce nom d’utilisateur existe déjà.")
                    else:
                        enregistrer_utilisateur(username, name, password)
                        st.success("✅ Inscription réussie. Vous pouvez maintenant vous connecter.")
                except Exception as e:
                    st.error(f"Erreur lors de l’inscription : {e}")
            else:
                st.warning("Merci de remplir tous les champs.")
        return False
"""