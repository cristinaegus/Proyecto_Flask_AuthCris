from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('Ejercicio_Pagina_Personalizada.config.Config')

    with app.app_context():
        from Ejercicio_Pagina_Personalizada import main
        app.register_blueprint(main)

    return app