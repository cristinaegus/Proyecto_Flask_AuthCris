from flask import Blueprint, jsonify, request, redirect, url_for, render_template, session, make_response
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    get_jwt
)
from Ejercicio_Pagina_Personalizada.extensions import jwt, db
from ..models.usuario import Usuario
from datetime import datetime, timezone
from Ejercicio_Pagina_Personalizada.utils.validators import validate_email, validate_password
from Ejercicio_Pagina_Personalizada.decorators import roles_required

auth_bp = Blueprint('auth', __name__)

# Lista negra de tokens revocados (en producción usar Redis)
BLACKLIST = set()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Mostrar el formulario de registro
        return render_template('inicio.html')

    # Soportar datos enviados como formulario estándar o JSON
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Validaciones
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return render_template('inicio.html', mensaje='Username, email y contraseña son requeridos')

    if not validate_email(data['email']):
        return render_template('inicio.html', mensaje='Email inválido')

    if not validate_password(data['password']):
        return render_template('inicio.html', mensaje='Contraseña debe tener al menos 6 caracteres')

    if Usuario.query.filter_by(username=data['username']).first():
        return render_template('inicio.html', mensaje='Username ya existe')

    if Usuario.query.filter_by(email=data['email']).first():
        return render_template('inicio.html', mensaje='Email ya registrado')

    # Crear nuevo usuario
    usuario = Usuario.from_dict(data)
    usuario.set_password(data['password'])

    db.session.add(usuario)
    db.session.commit()

    return render_template('inicio.html', mensaje='Usuario creado exitosamente')

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

    # Crear token JWT con el rol incluido en el payload
    additional_claims = {"rol": usuario.rol}
    access_token = create_access_token(identity=str(usuario.id), additional_claims=additional_claims)

    response = jsonify({
        'access_token': access_token,
        'usuario': usuario.to_dict(),
        'rol': usuario.rol
    })
    response.set_cookie(
        'access_token_cookie',
        access_token,
        httponly=True,
        samesite='Lax',
        path='/'
    )
    return response

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

@auth_bp.route('/admin')
@roles_required('admin')
def admin_panel():
    usuarios = Usuario.query.all()
    # Si tienes tokens asociados a usuarios, añade la lógica aquí para incluirlos en el diccionario
    usuarios_dict = []
    for usuario in usuarios:
        user_dict = usuario.to_dict()
        user_dict['token'] = getattr(usuario, 'token', None)  # Si tienes un campo token
        usuarios_dict.append(user_dict)
    return render_template('admin.html', usuarios=usuarios_dict)

@auth_bp.route('/admin_dashboard')
@roles_required('admin')
def admin_dashboard():
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.get(current_user_id)
    if not usuario:
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', username=usuario.username)

# El panel de administración ahora está en admin.py



