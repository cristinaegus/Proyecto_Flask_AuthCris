from Ejercicio_Pagina_Personalizada.app_ejerciciologin import app, db
from flask_migrate import Migrate
from Ejercicio_Pagina_Personalizada.models.usuario import Usuario
from Ejercicio_Pagina_Personalizada.extensions import db
import click

migrate = Migrate(app, db)

@app.cli.command('promote-admin')
@click.argument('email')
def promote_admin(email):
    """Promueve un usuario a administrador por email."""
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        usuario.rol = 'admin'
        db.session.commit()
        click.echo(f"Usuario {email} ahora es administrador.")
    else:
        click.echo("Usuario no encontrado.")

if __name__ == '__main__':
    app.run()
