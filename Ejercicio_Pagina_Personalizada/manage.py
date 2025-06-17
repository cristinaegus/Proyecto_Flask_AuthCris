from Ejercicio_Pagina_Personalizada.app_ejerciciologin import app, db
from flask_migrate import Migrate

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
