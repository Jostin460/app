import streamlit as st
import pandas as pd
from openai import OpenAI
import os

st.title("S&P 500 Data Analysis Assistant")
st.write("Realice consultas sobre el dataset del S&P 500 usando análisis REAL del dataframe.")

# Entrada usuario
question = st.text_area("Pregunta:", placeholder="Ejemplo: ¿Cuál es el precio promedio actual?")
api_key = st.text_input("Clave API:", type="password")

# Cargar dataset
uploaded_file = st.file_uploader("Suba el CSV del S&P 500", type="csv")

if uploaded_file is None:
    st.info("Suba un archivo para continuar.")
    st.stop()

df = pd.read_csv(uploaded_file)
st.success("Archivo cargado.")
st.dataframe(df)

# Botón
if st.button("Analizar"):
    if not api_key:
        st.error("Debe ingresar una API key.")
        st.stop()

    client = OpenAI(api_key=api_key)

    # ===== 1) Pedir al modelo una instrucción Python basada en la pregunta =====

    system_prompt = """
Eres un sistema experto en análisis de datos. 
Tu tarea es convertir la pregunta del usuario en una instrucción de Python 
que pueda ejecutarse sobre un DataFrame llamado df.

Reglas:
- Responde SOLO con código Python válido.
- NO incluyas explicaciones.
- Si la pregunta no tiene relación con el dataset, responde: NONE
- Ejemplos de salida válida:
    df['MarketCap'].max()
    df.loc[df['Currentprice'].idxmax()]
    df['RevenueGrowth'].mean()
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0
    )

    python_code = response.choices[0].message.content.strip()

    if python_code == "NONE":
        st.warning("La pregunta está fuera del alcance del dataset.")
        st.stop()

    st.write("🔧 **Código generado:**")
    st.code(python_code, language="python")

    # ===== 2) Ejecutar el código generado =====

    try:
        result = eval(python_code)
    except Exception as e:
        st.error(f"Error al ejecutar el código: {e}")
        st.stop()

    st.write("📊 **Resultado del análisis:**")
    st.write(result)

    # ===== 3) Enviar resultado al modelo para redactar respuesta =====

    final_prompt = f"""
Pregunta del usuario: {question}
Resultado del análisis en Python: {result}

Redacta una respuesta clara, en español, basada en el resultado.
"""

    final_response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Eres un analista financiero profesional."},
            {"role": "user", "content": final_prompt},
        ],
        temperature=0.4
    )

    st.subheader("Respuesta del modelo:")
    st.write(final_response.choices[0].message.content)


