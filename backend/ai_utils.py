from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def construir_prompt(data_summary: dict) -> str:
    columnas = data_summary.get("columnas", [])
    tipos = data_summary.get("tipos", {})
    estadisticas = data_summary.get("estadísticas", {})

    prompt = f"""
Tengo un conjunto de datos con las siguientes columnas: {columnas}.
Los tipos de datos por columna son: {tipos}.
Las estadísticas básicas son: {estadisticas}.

Por favor, sugiéreme entre 3 y 5 visualizaciones útiles para este conjunto de datos.
Para cada visualización quiero que se muertre:
- Tipo de gráfico
- Columnas involucradas
- Título sugerido
- Breve análisis que explique qué se puede observar o conclusiones que das

Responde en formato JSON.
    """.strip()

    return prompt

def consultar_modelo(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sos un experto en visualización de datos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content