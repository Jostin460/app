# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# ----------------------------------------------------------
# Configuración de la aplicación
# ----------------------------------------------------------
st.title("Mental Health Text Analysis Assistant")
st.write("Aplicación para analizar el dataset de características textuales, psicológicas y de sentimiento.")

# ----------------------------------------------------------
# Entradas del usuario
# ----------------------------------------------------------
question = st.text_area(
    "Ingrese su pregunta sobre el dataset:",
    placeholder="Ejemplo: ¿Qué variable presenta mayor correlación con el sentimiento negativo?"
)

api_key = st.text_input("Ingrese su clave de API de OpenAI:", type="password")

# ----------------------------------------------------------
# Carga del dataset
# ----------------------------------------------------------
uploaded_file = st.file_uploader("Suba el archivo CSV con los datos de análisis lingüístico y psicológico", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        st.success("Archivo cargado correctamente.")
        st.write("Vista completa del dataset (puede desplazarse y filtrar):")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        st.stop()
else:
    st.info("Suba el archivo CSV para continuar.")
    st.stop()

# ----------------------------------------------------------
# Procesar la pregunta mediante OpenAI
# ----------------------------------------------------------
if st.button("Analizar pregunta"):
    if not api_key:
        st.error("Debe ingresar una clave de API para continuar.")
        st.stop()

    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=api_key)

    df_preview = df.head(20).to_string()

    system_prompt = (
        "Eres un analista experto en datos psicológicos y lingüísticos. "
        "El dataset contiene características derivadas de textos, como índices de legibilidad, "
        "puntuaciones de sentimiento, indicadores de estrés, aislamiento, historial de salud mental y otros factores emocionales. "
        "Debes responder únicamente preguntas relacionadas con el análisis de estos datos o con temas asociados a salud mental basada en texto. "
        "Si la pregunta no se relaciona con este tipo de datos, indícalo amablemente."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Primeras filas del dataset:\n{df_preview}"},
                {"role": "user", "content": question}
            ],
            temperature=0.5
        )

        answer = response.choices[0].message.content
        st.subheader("Respuesta del modelo:")
        st.write(answer)

    except Exception as e:
        st.error(f"Error al procesar la solicitud: {e}")
