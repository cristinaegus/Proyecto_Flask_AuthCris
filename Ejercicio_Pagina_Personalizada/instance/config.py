SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://FlaskEjercicioConnect_owner:npg_4SBm3VXpFwIE@ep-floral-frost-a2tieivc-pooler.eu-central-1.aws.neon.tech/FlaskEjercicioConnect?sslmode=require'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_RECYCLE = 280
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True
}
SECRET_KEY = 'tu_clave_secreta_ultrasegura'
CSRF_SECRET_KEY = 'tu_clave_secreta_csrf'
WTF_CSRF_ENABLED = True

# Configuración JWT necesaria para flask_jwt_extended
JWT_SECRET_KEY = 'clave_jwt_supersegura'
JWT_TOKEN_LOCATION = ['headers', 'cookies']
JWT_HEADER_NAME = 'Authorization'
JWT_HEADER_TYPE = 'Bearer'
JWT_COOKIE_SECURE = False  # Cambia a True en producción con HTTPS
JWT_ACCESS_COOKIE_PATH = '/'
JWT_REFRESH_COOKIE_PATH = '/token/refresh'
JWT_COOKIE_CSRF_PROTECT = True
JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
JWT_ACCESS_CSRF_HEADER_NAME = 'X-CSRF-TOKEN'
JWT_REFRESH_CSRF_HEADER_NAME = 'X-CSRF-TOKEN-REFRESH'
JWT_ACCESS_CSRF_FIELD_NAME = 'csrf_access_token'
JWT_REFRESH_CSRF_FIELD_NAME = 'csrf_refresh_token'
