from flask import Blueprint, render_template
from Ejercicio_Pagina_Personalizada.decorators import roles_required
from Ejercicio_Pagina_Personalizada.models.usuario import Usuario

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@roles_required('admin')
def admin_panel():
    usuarios = Usuario.query.all()
    usuarios_dict = []
    for usuario in usuarios:
        user_dict = usuario.to_dict()
        user_dict['token'] = getattr(usuario, 'token', None)
        usuarios_dict.append(user_dict)
    return render_template('admin.html', usuarios=usuarios_dict)
