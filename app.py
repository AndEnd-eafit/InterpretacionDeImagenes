import os
import streamlit as st
import base64
from openai import OpenAI

# Configuración de la página debe ser la primera instrucción de Streamlit
st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")

# CSS to set custom fonts (Lexend for titles and Inter for text)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;700&family=Inter:wght@400;600&display=swap');
    
    /* Apply Lexend font for titles */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lexend', sans-serif;
    }
    
    /* Apply Inter font for general text */
    body, p, div, input, textarea, button {
        font-family: 'Inter', sans-serif;
    }
    
    /* Center align the title */
    .centered-title {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Title and input for API key
st.markdown('<h1 class="centered-title">Análisis de Imagen 🤖🏞️</h1>', unsafe_allow_html=True)
ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# File uploader for image
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Toggle for additional details
show_details = st.checkbox("Añadir detalles sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area("Añade contexto de la imagen aquí:")

# Analyze button
analyze_button = st.button("Analiza la imagen")

# Analysis function
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando..."):
        base64_image = encode_image(uploaded_file)
        prompt_text = "Describe lo que ves en la imagen en español"

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
        
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages, max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    if not uploaded_file and analyze_button:
        st.warning("Por favor, sube una imagen.")
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
