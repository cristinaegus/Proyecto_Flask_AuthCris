import sys
import os
# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Blueprint
import pytest
from Ejercicio_Pagina_Personalizada.app_ejerciciologin import app, db
from Ejercicio_Pagina_Personalizada.models.usuario import Usuario

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Hello, World!"


@pytest.fixture
def client():
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-key'
    })
    app.config['WTF_CSRF_ENABLED'] = False  # Desactiva CSRF para pruebas

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

@pytest.fixture
def token(client):
    client.post('/auth/register', json={
        "username": "tester",
        "email": "tester@test.com",
        "password": "123456"
    })
    res = client.post('/auth/login', json={
        "username": "tester",
        "password": "123456"
    })
    return res.get_json()['access_token']

def test_login_envia_datos_correctos(client):
    # Crear un usuario de prueba en la base de datos SQLite en memoria
    email = 'tester@tester.com'
    password = '123456'
    usuario = Usuario(email=email, username='tester')
    usuario.set_password(password)  # Si tienes un método para hashear la contraseña
    usuario.rol = 'admin'  # O el rol que desees
    with app.app_context():
        db.session.add(usuario)
        db.session.commit()

    response = client.post('/auth/login', json={
        'email': email,
        'password': password
    })
    data = response.get_json()
    print(data)  # Para depuración
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        print(f"Usuario: {usuario.email}, Rol: {usuario.rol}")
    assert response.status_code == 200
    assert 'access_token' in data
    assert data['usuario']['email'] == email
    assert data['usuario']['rol'] == 'admin'

