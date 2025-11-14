import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------
st.title("S&P 500 Data Analysis Assistant")
st.write("Este sistema responde consultas basadas exclusivamente en el dataset del S&P 500 que usted cargue. Si la pregunta no pertenece al ámbito del dataset, se le notificará.")

# ---------------------------------------------------------
# ENTRADAS DEL USUARIO
# ---------------------------------------------------------
question = st.text_area(
    "Escriba su pregunta relacionada con el dataset:",
    placeholder="Ejemplo: ¿Qué empresa tiene el mayor MarketCap?"
)

api_key = st.text_input("Ingrese su clave API de OpenAI:", type="password")

# ---------------------------------------------------------
# CARGA DEL DATASET
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Suba el archivo CSV del S&P 500", type="csv")

if uploaded_file is None:
    st.info("Por favor, suba el archivo CSV antes de continuar.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
    st.success("Archivo cargado correctamente.")
    st.dataframe(df)
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# Convertimos el dataframe a un resumen JSON para que el modelo conozca su estructura
df_metadata = {
    "columnas": list(df.columns),
    "filas": len(df),
    "muestras": df.head(5).to_dict(orient="records")
}

# ---------------------------------------------------------
# PROCESAR PREGUNTA
# ---------------------------------------------------------
if st.button("Analizar pregunta"):
    if not api_key:
        st.error("Debe ingresar la clave API para continuar.")
        st.stop()

    client = OpenAI(api_key=api_key)

    # Instrucciones al modelo
    system_prompt = (
        "Eres un analista financiero especializado en empresas del S&P 500. "
        "Tienes acceso al dataframe completo cargado por el usuario. "
        "Puedes razonar sobre valores numéricos y categóricos, realizar cálculos, "
        "comparaciones, promedios, máximos, mínimos y análisis según las columnas: "
        "Exchange, Symbol, Shortname, Longname, Sector, Industry, Currentprice, "
        "MarketCap, Ebitda, RevenueGrowth, City, State, Country, Fulltimeemployees "
        "y Longbusinesssummary. "
        "Tu razonamiento interno puede utilizar Python, pero nunca debes mostrar el código. "
        "Solo debes devolver una respuesta en lenguaje natural basada en los datos del dataframe. "
        "Si la pregunta está fuera del alcance del dataset, indícalo claramente."
    )

    user_prompt = (
        "Aquí está la descripción del dataset que cargó el usuario:\n"
        f"{df_metadata}\n\n"
        "Pregunta del usuario:\n"
        f"{question}\n\n"
        "Para ayudarte a razonar, aquí está el dataframe completo en formato CSV (no lo muestres al usuario):\n"
        f"{df.to_csv(index=False)}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content

        st.subheader("Respuesta del modelo:")
        st.write(result)

    except Exception as e:
        st.error(f"Error al consultar el modelo: {e}")

