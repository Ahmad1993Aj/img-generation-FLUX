import streamlit as st
import replicate
import os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Umgebungsvariablen laden
load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Streamlit-Seitenkonfiguration
st.set_page_config(
    page_title="Image Generation",
    page_icon=":art:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API-Key prüfen
if not REPLICATE_API_TOKEN:
    st.error("Bitte setze den REPLICATE_API_TOKEN in deiner .env Datei.")
    st.stop()

replicate.Client(api_token=REPLICATE_API_TOKEN)

# Session State initialisieren
if "image_url" not in st.session_state:
    st.session_state["image_url"] = None

# UI: Titel und Prompt
st.title("🖼️ Image Generation mit Replicate")
st.header("Prompt und Einstellungen")

prompt_text = st.text_area(
    "Gib einen Prompt für das Bildgenerierungsmodell ein:",
    value="Baby cat playing with a ball ",
    height=100
)

use_random_seed = st.checkbox("Zufälliger Seed verwenden", value=True)
random_seed = None
if use_random_seed:
    random_seed = st.slider("Zufalls-Seed", min_value=0, max_value=100000, value=42, step=1)

output_quality = st.slider('Bildqualität', 50, 100, 80)

# Zwei Spalten für Buttons
col1, col2 = st.columns([1, 1])

# Bild generieren
if col1.button('Bild generieren') and prompt_text:
    with st.spinner('🔄 Bild wird generiert...'):
        try:
            input_data = {
                "prompt": prompt_text,
                "aspect_ratio": "3:2", # Seitenverhältnis
                "quality": output_quality # Bildqualität
            }
            if random_seed is not None:
                input_data["seed"] = random_seed

            output = replicate.run(
                "black-forest-labs/flux-schnell", # name des Modells
                input=input_data
            )

            # Extrahiere die URL korrekt
            image_url = None
            if output:
                # Falls output eine Liste mit String-URLs ist
                if isinstance(output[0], str):
                    image_url = output[0]
                # Falls output eine Liste mit Dicts ist
                elif isinstance(output[0], dict) and "url" in output[0]:
                    image_url = output[0]["url"]
                # Falls output ein FileOutput-Objekt ist
                elif hasattr(output[0], "url"):
                    image_url = output[0].url

            st.session_state["image_url"] = image_url

        except Exception as e:
            st.error(f"Fehler bei der Bildgenerierung: {e}")
            st.session_state["image_url"] = None

# Bild anzeigen & Download-Button
if st.session_state["image_url"]:
    st.image(st.session_state["image_url"], caption='🖼️ Generiertes Bild')

    try:
        response = requests.get(st.session_state["image_url"])
        image = Image.open(BytesIO(response.content))

        img_buffer = BytesIO()
        image.save(img_buffer, format="JPEG")
        img_buffer.seek(0)

        with col2:
            st.download_button(
                label="📥 Bild herunterladen",
                data=img_buffer,
                file_name="generated_image.jpg",
                mime="image/jpeg"
            )
    except Exception as e:
        st.error(f"Fehler beim Herunterladen des Bildes: {e}")