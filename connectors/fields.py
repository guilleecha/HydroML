# connectors/fields.py

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet, MultiFernet

# Bloque de inicialización de Fernet
try:
    # Soporte para rotación de claves
    fernet_keys = [Fernet(k.encode()) for k in settings.FERNET_KEYS]
    f = MultiFernet(fernet_keys)
except AttributeError:
    raise ImproperlyConfigured("No se encontró la configuración FERNET_KEYS en settings.py")
except Exception as e:
    raise ImproperlyConfigured(f"Una de tus FERNET_KEYS no es válida. Error: {e}")


class EncryptedCharField(models.CharField):
    """
    Un CharField personalizado que encripta su valor usando cryptography.fernet.
    """
    
    def from_db_value(self, value, expression, connection):
        """ Desencripta el valor al leerlo de la base de datos. """
        if value is None:
            return value
        try:
            # El valor en la BD está como texto, lo desencriptamos
            decrypted_value = f.decrypt(value.encode()).decode()
            return decrypted_value
        except Exception:
            # Si hay un error (ej. el valor no está encriptado), devolvemos el valor original
            return value

    def get_prep_value(self, value):
        """ Encripta el valor antes de guardarlo en la base de datos. """
        if value is None:
            return value
        
        # Encriptamos el valor y lo devolvemos como una cadena de texto
        return f.encrypt(str(value).encode()).decode()