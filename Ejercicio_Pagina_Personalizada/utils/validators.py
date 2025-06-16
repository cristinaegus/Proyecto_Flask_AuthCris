import re

def validate_email(email):
    """Valida el formato de un email básico."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valida que la contraseña tenga al menos 6 caracteres."""
    return len(password) >= 6
