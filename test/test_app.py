import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_login_page(client):
    respuesta = client.get("/login")
    assert respuesta.status_code == 200


def test_registro_page(client):
    respuesta = client.get("/registro")
    assert respuesta.status_code == 200


def test_api_vehiculo(client):
    respuesta = client.get("/api/vehiculo_actual")
    assert respuesta.status_code == 200
    assert respuesta.is_json


def test_redireccion_index(client):
    respuesta = client.get("/", follow_redirects=False)
    assert respuesta.status_code == 302
