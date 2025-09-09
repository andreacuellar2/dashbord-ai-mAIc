from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import BytesIO

# Inicializo la aplicación FastAPI
app = FastAPI()

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
        "columnas": list(df.columns),  # Nombres de las columnas
        "tipos": df.dtypes.astype(str).to_dict(),  # Tipos de datos por columna
        "estadísticas": df.describe().to_dict()  # Estadísticas básicas (solo numéricas)
    }

    # Devuelvo el resumen como respuesta
    return summary