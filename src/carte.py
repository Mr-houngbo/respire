import folium
from folium import plugins
import streamlit as st
from streamlit_folium import st_folium
import streamlit.components.v1 as components




def get_air_quality_color(status):
    """Retourne une couleur de fond plus sombre et lisible pour du texte blanc"""
    color_map = {
        "excellente": "#1b5e20",       # Vert forêt très foncé
        "bonne": "#f9a825",            # Jaune foncé moutarde
        "moyenne": "#ef6c00",          # Orange brûlé
        "mauvaise": "#c62828",         # Rouge brique foncé
        "très mauvaise": "#6a1b9a"     # Violet prune foncé
    }
    return color_map.get(status.lower(), "#37474f")  # Gris bleuté profond par défaut

def get_air_quality_icon(status):
    """Retourne l'icône selon la qualité de l'air"""
    icon_map = {
        "excellente": "😊",
        "bonne": "🙂",
        "moyenne": "😐",
        "mauvaise": "😷",
        "très mauvaise": "🚨"
    }
    return icon_map.get(status.lower(), "❓")

@st.cache_data(ttl=300) # expire au bout de 5 min
def create_styled_popup(loc, data):
    """Crée un popup stylisé avec CSS moderne"""
    
    if "error" in data:
        popup_html = f"""
        <div style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            width: 320px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            border-radius: 15px;
            padding: 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            overflow: hidden;
            color: white;
        ">
            <div style="padding: 20px; text-align: center;">
                <h3 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 600;">
                    ❌ {loc['name']}
                </h3>
                <p style="margin: 0; font-size: 14px; opacity: 0.9;">
                    Erreur de données : {data['error']}
                </p>
            </div>
        </div>
        """
    else:
        # Déterminer la couleur de fond selon la qualité
        bg_color = get_air_quality_color(loc["status"])
        icon = get_air_quality_icon(loc["status"])
        
        # Créer les métriques avec icônes stylisées
        metrics = [
            ("", "Dernière MAJ", data['last_update']),
            ("", "PM2.5", f"{data['pm25']} µg/m³"),
            ("", "CO₂", f"{data['co2']} ppm"),
            ("", "Température", f"{data['temp']} °C"),
            ("", "Humidité", f"{data['humidity']} %"),
            ("", "PM10", f"{data['pm10']} µg/m³"),
            ("", "PM1", f"{data['pm1']} µg/m³"),
            ("", "PM0.3", f"{data['pm03']}"),
            ("", "TVOC", f"{data['tvoc']}"),
            ("", "NOx", f"{data['nox']}")
        ]
        
        metrics_html = ""
        for icon_metric, label, value in metrics:
            metrics_html += f"""
            <div style="
                display: flex;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            ">
                <span style="font-size: 16px; margin-right: 10px; width: 25px;">
                    {icon_metric}
                </span>
                <span style="flex: 1; font-size: 13px; opacity: 0.9;">
                    {label}
                </span>
                <span style="font-weight: 600; font-size: 13px;">
                    {value}
                </span>
            </div>
            """
        
        popup_html = f"""
        <div style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            width: 340px;
            background: linear-gradient(135deg, {bg_color}dd, {bg_color}aa);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 0;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            overflow: hidden;
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        ">
            <!-- En-tête -->
            <div style="
                background: rgba(255,255,255,0.1);
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            ">
                <div style="font-size: 30px; margin-bottom: 5px;">{icon}</div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 600;">
                    {loc['name']}
                </h3>
                <p style="
                    margin: 5px 0 0 0; 
                    font-size: 12px; 
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                ">
                    Qualité: {loc["status"]}
                </p>
            </div>
            
            <!-- Métriques -->
            <div style="
                padding: 15px 20px;
                max-height: 250px;
                overflow-y: auto;
            ">
                {metrics_html}
            </div>
            
            <!-- Pied de page -->
            <div style="
                background: rgba(0,0,0,0.2);
                padding: 10px 20px;
                text-align: center;
                font-size: 11px;
                opacity: 0.8;
            ">
                📡 Donnees recueillies en temps réel .
            </div>
        </div>
        """
    
    return popup_html

@st.cache_data(ttl=300) # expire au bout de 5 min
def create_custom_marker_icon(status):
    """Crée une icône personnalisée pour les marqueurs"""
    color = get_air_quality_color(status)
    icon = get_air_quality_icon(status)
    
    # Icône SVG personnalisée
    icon_svg = f"""
    <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
        <circle cx="20" cy="20" r="18" fill="{color}" stroke="white" stroke-width="3" opacity="0.9"/>
        <circle cx="20" cy="20" r="15" fill="{color}" opacity="0.7"/>
        <text x="20" y="25" text-anchor="middle" font-size="12" fill="white">
            {icon}
        </text>
    </svg>
    """
    
    return folium.DivIcon(
        html=f'<div style="transform: translate(-20px, -20px);">{icon_svg}</div>',
        icon_size=(40, 40),
        icon_anchor=(20, 20)
    )

# Créer la carte avec un style moderne
@st.cache_data(ttl=300) # expire au bout de 5 min
def create_optimized_map(locations, data_by_location):
    """Crée une carte optimisée avec des popups stylisés"""
    
    # Carte avec tiles personnalisés
    m = folium.Map(
        location=[7.0, 21.0],
        zoom_start=4,
        tiles=None  # On va ajouter nos propres tiles
    )
    
    # Ajouter plusieurs couches de fond
    folium.TileLayer(
        'CartoDB Positron',
        name='Clair',
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB Dark_Matter',
        name='Sombre',
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'OpenStreetMap',
        name='Standard',
        control=True
    ).add_to(m)
    
    # Groupe de marqueurs avec clustering
    marker_cluster = plugins.MarkerCluster(
        name="Capteurs",
        options={
            'maxClusterRadius': 50,
            'disableClusteringAtZoom': 10
        }
    ).add_to(m)
    
    # Ajouter les marqueurs
    for _, loc in locations.iterrows():
        data = data_by_location[loc["location_id"]]
        
        # Créer le popup stylisé
        popup_html = create_styled_popup(loc, data)
        
        # Créer le marqueur avec icône personnalisée
        marker = folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=folium.Tooltip(
                f"<b>{loc['name']}</b><br>Qualité: {loc['status']}", 
                sticky=True
            ),
            icon=create_custom_marker_icon(loc["status"])
        )
        
        marker.add_to(marker_cluster)
    
    # Ajouter une légende
    legend_html = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 200px;
        height: auto;
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        font-size: 12px;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        z-index: 9999;
    ">
        <h4 style="margin: 0 0 10px 0; color: #333;">Qualité de l'air</h4>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: #00e400; border-radius: 50%; margin-right: 8px;"></div>
            <span> Excellente</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: #ffff00; border-radius: 50%; margin-right: 8px;"></div>
            <span> Bonne</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: #ff7e00; border-radius: 50%; margin-right: 8px;"></div>
            <span> Moyenne</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: #ff0000; border-radius: 50%; margin-right: 8px;"></div>
            <span> Mauvaise</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: #8f3f97; border-radius: 50%; margin-right: 8px;"></div>
            <span> Très mauvaise</span>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Ajouter le contrôle des couches
    folium.LayerControl().add_to(m)
    
    # Ajouter la géolocalisation
    plugins.LocateControl().add_to(m)
    
    return m


def _embed_folium_map_via_components(m, height=600):
    """
    Renders a folium.Map `m` using components.html and injects JS that forces
    Leaflet to recalc its size several times and on common events.
    """
    # Render full HTML of the folium map
    full_html = m.get_root().render()

    # JS snippet to force invalidateSize(), set div height and observe DOM changes
    fix_js = f"""
    <script>
    (function() {{
       function tryFix() {{
           try {{
               // Find the map DIV created by folium (id starts with 'map_')
               var mapDiv = document.querySelector("div[id^='map_'], div.folium-map");
               if (mapDiv) {{
                   // Force inline height to ensure container size
                   mapDiv.style.height = "{height}px";
               }}
               // Try to find a Map instance:
               var mapObj = null;
               if (mapDiv && mapDiv.id && window.hasOwnProperty(mapDiv.id)) {{
                   mapObj = window[mapDiv.id];
               }}
               if (!mapObj && typeof L !== 'undefined') {{
                   for (var k in window) {{
                       if (window[k] && window[k] instanceof L.Map) {{
                           mapObj = window[k];
                           break;
                       }}
                   }}
               }}
               if (mapObj && typeof mapObj.invalidateSize === 'function') {{
                   mapObj.invalidateSize();
                   window.dispatchEvent(new Event('resize'));
               }}
           }} catch (e) {{
               console && console.warn && console.warn('tryFix folium map:', e);
           }}
       }}

       // Multiple scheduled attempts (covers async loading)
       [50, 200, 500, 1000, 2000].forEach(function(t) {{ setTimeout(tryFix, t); }});

       // React to window resize / visibility
       window.addEventListener('resize', tryFix);
       document.addEventListener('visibilitychange', function() {{
           if (!document.hidden) tryFix();
       }});

       // Short-lived MutationObserver to catch late DOM insertions
       var obs = new MutationObserver(function() {{ tryFix(); }});
       obs.observe(document.body, {{ childList: true, subtree: true }});
       setTimeout(function() {{ obs.disconnect(); }}, 5000);
    }})();
    </script>
    """

    # Inject the JS before </body>
    html_with_fix = full_html.replace("</body>", fix_js + "</body>")

    # Render inside Streamlit with fixed height
    components.html(html_with_fix, height=height, scrolling=False)


def display_map_with_school_selector(locations, data_by_location, height=600):
    """Affiche la carte avec sélecteur d'école — rendu robuste via components.html"""
    # Création du sélecteur d'école (dans colonne de gauche)

    school_names = ["-- Choisir une école --"] + locations['name'].tolist()
    selected_school = st.selectbox("Sélectionnez une école :", school_names, key="school_selector")

    # Construire la carte (par défaut / vue globale)
    if selected_school != "-- Choisir une école --":
        # Centrer sur l'école sélectionnée (tu avais déjà cette logique)
        school_data = locations[locations['name'] == selected_school].iloc[0]
        m = folium.Map(location=[school_data['lat'], school_data['lon']],
                       zoom_start=12, tiles=None)
        folium.TileLayer('CartoDB Positron', name='Clair', control=True).add_to(m)
        folium.TileLayer('CartoDB Dark_Matter', name='Sombre', control=True).add_to(m)
        folium.TileLayer('OpenStreetMap', name='Standard', control=True).add_to(m)

        marker_cluster = plugins.MarkerCluster(
            name="Capteurs",
            options={'maxClusterRadius': 50, 'disableClusteringAtZoom': 10}
        ).add_to(m)

        for _, loc in locations.iterrows():
            data = data_by_location[loc["location_id"]]
            popup_html = create_styled_popup(loc, data)

            if loc['name'] == selected_school:
                # Garde ton DivIcon personnalisé
                selected_icon_svg = f"""
                <svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="25" cy="25" r="23" fill="{get_air_quality_color(loc['status'])}" 
                            stroke="white" stroke-width="4" opacity="0.9">
                        <animate attributeName="r" values="20;25;20" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="25" cy="25" r="18" fill="{get_air_quality_color(loc['status'])}" opacity="0.8"/>
                    <text x="25" y="30" text-anchor="middle" font-size="14" fill="white">
                        {get_air_quality_icon(loc['status'])}
                    </text>
                </svg>
                """
                icon = folium.DivIcon(
                    html=f'<div style="transform: translate(-25px, -25px);">{selected_icon_svg}</div>',
                    icon_size=(50, 50),
                    icon_anchor=(25, 25)
                )
            else:
                icon = create_custom_marker_icon(loc["status"])

            folium.Marker(
                location=[loc["lat"], loc["lon"]],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=folium.Tooltip(f"<b>{loc['name']}</b><br>Qualité: {loc['status']}", sticky=True),
                icon=icon
            ).add_to(marker_cluster)

        folium.LayerControl().add_to(m)
        plugins.Search(layer=marker_cluster, search_label='name', placeholder='Rechercher un capteur...').add_to(m)

        # Légende (même HTML que toi)
        legend_html = """..."""  # (tu peux coller ta légende complète ici)
        m.get_root().html.add_child(folium.Element(legend_html))

    else:
        # Vue globale : utilise ta fonction d'origine create_optimized_map si tu l'as
        m = create_optimized_map(locations, data_by_location)

    # Affiche la carte 
    _embed_folium_map_via_components(m, height=height)

    # retourne la sélection éventuellement utile en dehors
    return selected_school


# Utilisation dans Streamlit
# m = create_optimized_map(locations, data_by_location)
# st_folium(m, width="100%", height=600, returned_objects=[], use_container_width=True)




