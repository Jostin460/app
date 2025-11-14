import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# ----------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# ----------------------------
st.title("S&P 500 Data Analysis Assistant")
st.write("Realice consultas sobre el dataset del S&P 500. Si la pregunta no pertenece al ámbito del dataset, el sistema lo indicará de manera adecuada.")

# ----------------------------
# ENTRADAS DEL USUARIO
# ----------------------------

# Pregunta del usuario
question = st.text_area(
    "Escriba su pregunta relacionada con el dataset:",
    placeholder="Ejemplo: ¿Qué empresa tiene el mayor MarketCap?"
)

# Clave de API
api_key = st.text_input("Ingrese su clave API de OpenAI:", type="password")

# ----------------------------
# CARGA DEL DATASET
# ----------------------------
uploaded_file = st.file_uploader("Suba el archivo CSV del S&P 500", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Archivo cargado correctamente.")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        st.stop()
else:
    st.info("Por favor, suba el archivo CSV antes de continuar.")
    st.stop()

# ----------------------------
# PROCESAR PREGUNTA
# ----------------------------
if st.button("Analizar pregunta"):
    if not api_key:
        st.error("Debe ingresar la clave API para continuar.")
        st.stop()

    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=api_key)

    # Para evitar prompts demasiado largos, solo se pasan las primeras filas
    df_string = df.head(10).to_string()

    system_prompt = (
        "Eres un analista financiero especializado en empresas del S&P 500. "
        "Tienes acceso a un dataset que incluye columnas como: Exchange, Symbol, "
        "Shortname, Longname, Sector, Industry, Currentprice, MarketCap, Ebitda, "
        "RevenueGrowth, City, State, Country, Fulltimeemployees y "
        "Longbusinesssummary. "
        "El dataset describe características financieras y corporativas. "
        "Si la pregunta del usuario no está relacionada con esta información, "
        "debes responder amablemente que la pregunta está fuera del alcance del dataset."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Muestra del dataset:\n{df_string}"},
                {"role": "user", "content": question}
            ],
            temperature=0.4
        )

        answer = response.choices[0].message.content
        st.subheader("Respuesta del modelo:")
        st.write(answer)

    except Exception as e:
        st.error(f"Error al consultar el modelo: {e}")
