from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import BytesIO
from ai_utils import construir_prompt, consultar_modelo, corregir_respuesta
from fastapi.middleware.cors import CORSMiddleware
import json

# Inicializo la aplicación FastAPI
app = FastAPI()

# Permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Podés restringir esto a tu dominio si querés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defino el endpoint POST para subir archivos


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Leo el contenido del archivo subido
    content = await file.read()

    # Extraigo la extensión del archivo para saber cómo procesarlo
    extension = file.filename.split('.')[-1]

    # Si el archivo es CSV, lo leo con pandas
    if extension == 'csv':
        df = pd.read_csv(BytesIO(content))
    # Si es Excel, uso read_excel
    elif extension in ['xlsx', 'xls']:
        df = pd.read_excel(BytesIO(content))
    # Si no es un formato soportado, devuelvo un error
    else:
        return {"error": "Formato no soportado"}

    # Armo un resumen básico del DataFrame para enviárselo luego al modelo de IA
    summary = {
        "columnas": list(df.columns),
        "tipos": df.dtypes.astype(str).to_dict(),
        "estadísticas": df.describe().to_dict()
    }

    # Construyo el prompt para el modelo
    prompt = construir_prompt(summary)

    # Consulto al modelo de lenguaje para obtener sugerencias
    sugerencias = consultar_modelo(prompt)

    try:
        if sugerencias.strip().startswith("["):
            sugerencias_dict = json.loads(sugerencias)
        else:
            sugerencias_dict = corregir_respuesta(sugerencias)
    except Exception as e:
        return {
            "error": "La IA devolvió un formato no válido",
            "detalle": str(e),
            "respuesta_original": sugerencias
        }
    # Validamos estructura de cada sugerencia
    for sugerencia in sugerencias_dict:
        if not all(k in sugerencia for k in ["title", "chart_type", "parameters", "insight"]):
            return {
                "error": "Una sugerencia no tiene la estructura esperada",
                "sugerencia": sugerencia
            }

    # Devuelvo el resumen como respuesta
    return {
        "resumen": summary,
        "prompt": prompt,
        "sugerencias": sugerencias_dict
    }
