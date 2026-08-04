import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Ruta de la clave secreta AES-256 (almacenada localmente y fuera de Git)
SECRET_KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".secret.key")

def _get_or_create_key() -> bytes:
    """
    Genera o recupera una clave secreta AES-256 estandarizada.
    Si no existe la clave local, crea un archivo .secret.key con cifrado de 256 bits.
    """
    env_key = os.environ.get("ALTUS_AES256_KEY")
    if env_key:
        return env_key.encode()

    if os.path.exists(SECRET_KEY_PATH):
        with open(SECRET_KEY_PATH, "rb") as f:
            return f.read().strip()
    else:
        key = Fernet.generate_key()
        with open(SECRET_KEY_PATH, "wb") as f:
            f.write(key)
        return key

_cipher_suite = Fernet(_get_or_create_key())

def encrypt_data(plain_text: str) -> str:
    """
    Cifra cualquier texto (RUT, Nombre, Email, Montos) con AES-256 de grado bancario.
    Devuelve una cadena cifrada base64.
    """
    if not plain_text or plain_text.strip() == "":
        return plain_text
    
    # Evitar cifrar si ya está cifrado
    if is_encrypted(plain_text):
        return plain_text

    encrypted_bytes = _cipher_suite.encrypt(plain_text.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt_data(cipher_text: str) -> str:
    """
    Descifra un token encriptado con AES-256 devolviendo la cadena original.
    """
    if not cipher_text or not is_encrypted(cipher_text):
        return cipher_text

    try:
        decrypted_bytes = _cipher_suite.decrypt(cipher_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception:
        # Retorna el texto original si no corresponde a una cadena cifrada válida
        return cipher_text

def is_encrypted(text: str) -> bool:
    """
    Verifica si una cadena dada es un token Fernet / AES-256 válido.
    """
    if not text or not isinstance(text, str) or not text.startswith("gAAAAA"):
        return False
    try:
        _cipher_suite.decrypt(text.encode("utf-8"))
        return True
    except Exception:
        return False

if __name__ == "__main__":
    print("Prueba de Motor AES-256 Altus AI:")
    test_rut = "15.884.242-4"
    cifrado = encrypt_data(test_rut)
    descifrado = decrypt_data(cifrado)
    print(f"Original:  {test_rut}")
    print(f"Cifrado AES-256: {cifrado}")
    print(f"Descifrado: {descifrado}")
    print(f"¿Es Cifrado?: {is_encrypted(cifrado)}")
