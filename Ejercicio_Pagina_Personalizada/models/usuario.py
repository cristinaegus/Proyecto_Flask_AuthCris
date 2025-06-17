from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from Ejercicio_Pagina_Personalizada.extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    nombre = db.Column(db.String(100), nullable=True)
    apellido = db.Column(db.String(100), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    rol = db.Column(db.String(20), default='usuario')
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def set_password(self, password):
        """Hashea y guarda la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convierte el objeto a diccionario para JSON"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            'rol': self.rol
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
    
    @staticmethod
    def from_dict(data):
        """Crea un usuario desde un diccionario"""
        usuario = Usuario(
            username=data.get('username'),
            email=data.get('email'),
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            activo=data.get('activo', True),
            rol=data.get('rol', 'usuario')
        )
        if 'password' in data:
            usuario.set_password(data['password'])
        return usuario

    # Agregar método para verificar si el usuario está activo
    def is_active(self):
        return self.activo
