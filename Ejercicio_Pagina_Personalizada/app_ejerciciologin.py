from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
# Importar CSRFProtect para proteger contra ataques CSRF
from flask_wtf.csrf import CSRFProtect
from Ejercicio_Pagina_Personalizada.extensions import db
import os
from flask import send_from_directory
from Ejercicio_Pagina_Personalizada.blueprints.auth import auth_bp
from Ejercicio_Pagina_Personalizada.blueprints.admin import admin_bp
from Ejercicio_Pagina_Personalizada.models.usuario import Usuario
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
from flask import jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from Ejercicio_Pagina_Personalizada.decorators import roles_required

app = Flask(__name__)

# Cargar configuración desde instance/config.py (ruta absoluta)
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
app.config.from_pyfile(os.path.join(instance_path, 'config.py'))
app.secret_key = app.config['SECRET_KEY']
csrf = CSRFProtect(app)
# Configuración de CSRF
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = app.config['CSRF_SECRET_KEY']

db.init_app(app)
migrate = Migrate(app, db)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp)

# Inicializar JWTManager
jwt = JWTManager(app)

class LoginUsuario(db.Model):
    __tablename__ = 'login_usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Tarea:
    def __init__(self, descripcion, estado):
        self.descripcion = descripcion
        self.estado = estado

def get_tareas_usuario():
    email = session.get('email')
    if not email:
        return []
    tareas_por_usuario = session.get('tareas_por_usuario', {})
    return tareas_por_usuario.get(email, [])

def add_tarea_usuario(descripcion, estado):
    email = session.get('email')
    if not email:
        return
    tareas_por_usuario = session.get('tareas_por_usuario', {})
    tareas = tareas_por_usuario.get(email, [])
    tareas.append({'descripcion': descripcion, 'estado': estado})
    tareas_por_usuario[email] = tareas
    session['tareas_por_usuario'] = tareas_por_usuario

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )
@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/configurar', methods=['GET', 'POST'])
def configurar():
    color = request.cookies.get('color')
    mensaje = None
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        color = request.form.get('color')
        # Verificar si el email ya existe antes de guardar
        existe = LoginUsuario.query.filter_by(email=email).first()
        if existe:
            mensaje = 'Error: el email ya está registrado.'
        else:
            nuevo_usuario = LoginUsuario(nombre=nombre, apellido=apellido, email=email)
            db.session.add(nuevo_usuario)
            try:
                db.session.commit()
                mensaje = 'Usuario guardado correctamente en la base de datos.'
            except Exception as e:
                db.session.rollback()
                mensaje = 'Error al guardar el usuario.'
        resp = make_response(redirect(url_for('bienvenida')))
        resp.set_cookie('color', color)
        session['nombre'] = nombre
        session['email'] = email
        session['mensaje'] = mensaje
        # Inicializar tareas para el nuevo usuario si no existen
        tareas_por_usuario = session.get('tareas_por_usuario', {})
        if email not in tareas_por_usuario:
            tareas_por_usuario[email] = []
            session['tareas_por_usuario'] = tareas_por_usuario
        return resp
    if not color:
        color = '#ffffff'
    mensaje = session.pop('mensaje', None)
    return render_template('configurar.html', nombre='', apellido='', email='', color=color, mensaje=mensaje)

@app.route('/bienvenida', methods=['GET', 'POST'])
def bienvenida():
    nombre = session.get('nombre')
    email = session.get('email')
    color = request.cookies.get('color')
    if not nombre or not email:
        resp = make_response(redirect(url_for('configurar')))
        resp.set_cookie('color', '', expires=0)
        return resp
    if not color:
        color = '#ffffff'
    if request.method == 'POST':
        descripcion = request.form.get('descripcion')
        estado = request.form.get('estado')
        # Validación: ambos campos deben estar presentes
        if not descripcion or not estado:
            tareas = [Tarea(t['descripcion'], t['estado']) for t in get_tareas_usuario()]
            return render_template('inicio.html', nombre=nombre, color=color, tareas=tareas, mensaje_tarea='Debes completar todos los campos de la tarea.')
        add_tarea_usuario(descripcion, estado)
        return redirect(url_for('bienvenida'))
    tareas = [Tarea(t['descripcion'], t['estado']) for t in get_tareas_usuario()]
    return render_template('mi_web.html', nombre=nombre, color=color, tareas=tareas)

@app.route('/borrar_tarea/<int:idx>', methods=['POST'])
def borrar_tarea(idx):
    email = session.get('email')
    if not email:
        return redirect(url_for('bienvenida'))
    tareas_por_usuario = session.get('tareas_por_usuario', {})
    tareas = tareas_por_usuario.get(email, [])
    if 0 <= idx < len(tareas):
        tareas.pop(idx)
        tareas_por_usuario[email] = tareas
        session['tareas_por_usuario'] = tareas_por_usuario
    return redirect(url_for('bienvenida'))

@app.route('/olvidar')
def olvidar():
    session.pop('nombre', None)
    session.pop('email', None)
    resp = make_response(redirect(url_for('configurar')))
    resp.set_cookie('color', '', expires=0)
    return resp

@app.route('/salir')
def salir():
    session.clear()
    resp = make_response(redirect(url_for('root')))
    resp.set_cookie('color', '', expires=0)
    return resp

@app.route('/verificar_usuario', methods=['GET'])
def verificar_usuario():
    username = request.args.get('username')
    if not username:
        return {'error': 'Falta el parámetro username'}, 400
    usuario = db.session.query(Usuario).filter_by(username=username).first()
    if usuario:
        return {'acceso': True, 'usuario': usuario.to_dict()}
    else:
        return {'acceso': False, 'error': 'Usuario no encontrado'}, 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask import render_template, request, session
    mensaje = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            mensaje = 'Email y contraseña requeridos.'
        else:
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario and usuario.check_password(password):
                session['nombre'] = usuario.nombre or usuario.username
                session['email'] = usuario.email
                # Crear el token de acceso
                access_token = create_access_token(identity=str(usuario.id))
                response = jsonify({
                    'access_token': access_token,
                    'usuario': usuario.to_dict()
                })
                # Guardar el token en una cookie segura
                response.set_cookie('access_token_cookie', access_token, httponly=True, samesite='Lax')
                return response
            else:
                mensaje = 'Email o contraseña incorrectos.'
    return render_template('login.html', mensaje=mensaje)

@app.route('/admin/promote', methods=['GET', 'POST'])
@roles_required('admin')
def promote_admin_web():
    from Ejercicio_Pagina_Personalizada.models.usuario import Usuario
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        usuario = Usuario.query.get(user_id)
        if usuario:
            usuario.rol = 'admin'
            db.session.commit()
            flash(f"Usuario {usuario.email} ahora es administrador.", "success")
        else:
            flash("Usuario no encontrado.", "danger")
        return redirect(url_for('promote_admin_web'))
    usuarios = Usuario.query.all()
    return render_template('promote_admin.html', usuarios=usuarios)

# El decorador roles_required ahora está en decorators.py

if __name__ == '__main__':
    app.run(debug=True)
