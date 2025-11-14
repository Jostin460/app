import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import re

# ----------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# ----------------------------
st.title("S&P 500 Data Analysis Assistant")
st.write("Realice consultas sobre el dataset del S&P 500. "
         "El sistema puede realizar cálculos numéricos directamente sobre el dataset.")

# ----------------------------
# ENTRADAS DEL USUARIO
# ----------------------------
question = st.text_area(
    "Escriba su pregunta relacionada con el dataset:",
    placeholder="Ejemplo: ¿Qué empresa tiene el mayor MarketCap?"
)

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
# FUNCIONES DE ANÁLISIS NUMÉRICO
# ----------------------------

def detect_numeric_intent(q):
    """Clasifica si la pregunta requiere cálculo numérico."""
    numeric_keywords = [
        "mayor", "menor", "promedio", "media", "mediana",
        "máximo", "mínimo", "cuánto", "sumar", "suma",
        "top", "ordenar", "promediar", "desviación"
    ]
    return any(word in q.lower() for word in numeric_keywords)


def compute_answer(q, df):
    """Interpreta matemáticamente la pregunta y ejecuta el cálculo."""
    q = q.lower()

    # Mayor MarketCap
    if "mayor" in q and "marketcap" in q:
        row = df.loc[df["MarketCap"].idxmax()]
        return f"La empresa con mayor MarketCap es {row['Shortname']} con un valor de {row['MarketCap']}."

    # Menor MarketCap
    if "menor" in q and "marketcap" in q:
        row = df.loc[df["MarketCap"].idxmin()]
        return f"La empresa con menor MarketCap es {row['Shortname']} con un valor de {row['MarketCap']}."

    # Promedio de precios
    if ("promedio" in q or "media" in q) and "price" in q:
        avg = df["Currentprice"].mean()
        return f"El precio promedio de las empresas es {avg:.2f}."

    # Empresa con mayor precio
    if "mayor" in q and "price" in q:
        row = df.loc[df["Currentprice"].idxmax()]
        return f"La empresa con el precio más alto es {row['Shortname']} con un precio de {row['Currentprice']}."

    # Empresa con menor precio
    if "menor" in q and "price" in q:
        row = df.loc[df["Currentprice"].idxmin()]
        return f"La empresa con el precio más bajo es {row['Shortname']} con un precio de {row['Currentprice']}."

    # Promedio de MarketCap
    if "promedio" in q and "marketcap" in q:
        avg = df["MarketCap"].mean()
        return f"El MarketCap promedio es {avg:.2f}."

    # Si no se reconoce el patrón numérico
    return None


# ----------------------------
# PROCESAR PREGUNTA
# ----------------------------
if st.button("Analizar pregunta"):

    if not api_key:
        st.error("Debe ingresar la clave API para continuar.")
        st.stop()

    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=api_key)

    # ¿Pregunta requiere cálculo real?
    numeric_intent = detect_numeric_intent(question)
    numeric_response = None

    if numeric_intent:
        numeric_response = compute_answer(question, df)

    # Si se pudo resolver con cálculos:
    if numeric_response is not None:
        st.subheader("Resultado numérico obtenido del dataset:")
        st.write(numeric_response)
        st.stop()

    # ----------------------------
    # Si NO requiere cálculo → usar modelo
    # ----------------------------
    sample_string = df.head(10).to_string()

    system_prompt = (
        "Eres un analista financiero especializado en empresas del S&P 500. "
        "Debes responder únicamente preguntas directamente relacionadas con las columnas del dataset: "
        "Exchange, Symbol, Shortname, Longname, Sector, Industry, Currentprice, "
        "MarketCap, Ebitda, RevenueGrowth, City, State, Country, "
        "Fulltimeemployees y Longbusinesssummary. "
        "Si la pregunta está fuera de este dominio, responde de forma amable indicando que no se puede responder."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Muestra del dataset:\n{sample_string}"},
                {"role": "user", "content": question}
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        st.subheader("Respuesta del modelo:")
        st.write(answer)

    except Exception as e:
        st.error(f"Error al consultar el modelo: {e}")
