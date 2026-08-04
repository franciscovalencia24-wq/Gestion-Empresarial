import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 60)
    print("ACCESO DESDE TU CELULAR EN LA MISMA RED WI-FI:")
    print(f"Abre Safari o Chrome en tu celular e ingresa a:")
    print(f"http://{ip}:8501")
    print("=" * 60)
