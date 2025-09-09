from fastapi.testclient import TestClient
from backend.main import app
import io

client = TestClient(app)

def test_upload_csv():
    # Simulo un archivo CSV en memoria
    csv_content = "nombre,edad\nAna,30\nLuis,25"
    file = io.BytesIO(csv_content.encode("utf-8"))

    # Envío el archivo al endpoint /upload
    response = client.post(
        "/upload",
        files={"file": ("test.csv", file, "text/csv")}
    )

    # Verifico que la respuesta sea exitosa
    assert response.status_code == 200

    # Extraigo el contenido JSON
    data = response.json()

    # Verifico que se hayan detectado las columnas correctamente
    assert data["columnas"] == ["nombre", "edad"]

    # Verifico que se hayan identificado los tipos de datos
    assert "nombre" in data["tipos"]
    assert "edad" in data["tipos"]

    # Verifico que se hayan calculado estadísticas para la columna numérica
    assert "edad" in data["estadísticas"]
