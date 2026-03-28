from fastapi.testclient import TestClient
from app.main import app

#TestClient lar os lare som vi er en nettleser som besøker API-en
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Velkommen til Brannrisiko API!"}
