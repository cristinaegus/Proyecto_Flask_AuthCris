SQLALCHEMY_DATABASE_URI = 'postgresql://FlaskEjercicioConnect_owner:npg_4SBm3VXpFwIE@ep-floral-frost-a2tieivc-pooler.eu-central-1.aws.neon.tech/FlaskEjercicioConnect?sslmode=require'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_RECYCLE = 280
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True
}
SECRET_KEY = 'tu_clave_secreta_ultrasegura'
CSRF_SECRET_KEY = 'tu_clave_secreta_csrf'
WTF_CSRF_ENABLED = True
