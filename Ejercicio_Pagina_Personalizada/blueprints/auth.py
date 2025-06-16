from flask import Blueprint, jsonify, request, redirect, url_for
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    get_jwt
)
from Ejercicio_Pagina_Personalizada.extensions import jwt, db
from ..models.usuario import Usuario
from datetime import datetime, timezone
from Ejercicio_Pagina_Personalizada.utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

# Lista negra de tokens revocados (en producción usar Redis)
BLACKLIST = set()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Redirigir a la página de inicio si se accede por GET
        return redirect(url_for('root'))

    # Soportar datos enviados como formulario estándar o JSON
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Validaciones
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email y contraseña son requeridos'}), 400

    if not validate_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400

    if not validate_password(data['password']):
        return jsonify({'error': 'Contraseña debe tener al menos 6 caracteres'}), 400

    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username ya existe'}), 400

    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 400

    # Crear nuevo usuario
    usuario = Usuario.from_dict(data)
    usuario.set_password(data['password'])

    db.session.add(usuario)
    db.session.commit()

    return jsonify({
        'mensaje': 'Usuario creado exitosamente',
        'usuario': usuario.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('username') and not data.get('email'):
        return jsonify({'error': 'Username o email requerido'}), 400
    if not data.get('password'):
        return jsonify({'error': 'Contraseña requerida'}), 400

    # Buscar usuario por username o email
    usuario = None
    if data.get('username'):
        usuario = Usuario.query.filter_by(username=data['username']).first()
    if not usuario and data.get('email'):
        usuario = Usuario.query.filter_by(email=data['email']).first()

    if not usuario or not usuario.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    # Actualizar último acceso
    usuario.ultimo_acceso = datetime.now(tz=timezone.utc)
    db.session.commit()

    # Crear token JWT
    access_token = create_access_token(identity=str(usuario.id))

    return jsonify({
        'access_token': access_token,
        'usuario': usuario.to_dict()
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti'] 
    print(jti)
    BLACKLIST.add(jti)
    return jsonify({'mensaje': 'Sesión cerrada exitosamente'})

# Middleware de protección
@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    print(f"Verificando si el token está en BLACKLIST: {jti}")
    return jti in BLACKLIST

@jwt.revoked_token_loader
def revoked_token_response(jwt_header, jwt_payload):
    return jsonify({'msg': 'Token ha sido revocado'}), 401
############


# Endpoint protegido de ejemplo
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.get(current_user_id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict())
