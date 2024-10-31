import os
import streamlit as st
import base64
from openai import OpenAI

# Configuración de página con tipografía y título centrado
st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<style>body { font-family: 'Lexend', sans-serif; }</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-family: Lexend, sans-serif;'>Análisis de Imagen 🤖🏞️</h1>", unsafe_allow_html=True)

# Función para codificar imagen en base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Entrada para clave API
ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Inicializar el cliente OpenAI con la clave
client = OpenAI(api_key=api_key)

# Carga de archivo de imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Mostrar imagen cargada con expandir
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Añadir toggle para detalles adicionales
show_details = st.checkbox("Añadir detalles sobre la imagen", value=False)

if show_details:
    # Campo de texto para detalles adicionales
    additional_details = st.text_area("Añadir contexto de la imagen aquí:")

# Botón para análisis de imagen
analyze_button = st.button("Analizar la imagen")

# Verificación de entrada para análisis
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        base64_image = encode_image(uploaded_file)

        # Prompt optimizado en español
        prompt_text = (
            "Eres un experto en análisis de imágenes científicas. Examina en detalle la siguiente imagen "
            "y proporciona una explicación precisa de lo que representa. Destaca los elementos clave y su importancia, "
            "en un formato claro y bien estructurado en markdown. Incluye terminología científica relevante en español."
        )

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

        # Crear el mensaje para la API
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
                ],
            }
        ]

        # Solicitud a la API de OpenAI
        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview", messages=messages, max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    if not uploaded_file and analyze_button:
        st.warning("Por favor sube una imagen.")
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
