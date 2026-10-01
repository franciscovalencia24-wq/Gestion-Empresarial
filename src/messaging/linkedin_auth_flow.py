import os
import urllib.parse
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ ERROR: No se encontró LINKEDIN_CLIENT_ID o LINKEDIN_CLIENT_SECRET en el archivo .env")
    exit(1)

# Variables globales para guardar el código
auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/callback':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            if 'code' in query_params:
                auth_code = query_params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Autorizacion exitosa!</h1><p>Ya puedes cerrar esta ventana y volver a la terminal.</p></body></html>")
            elif 'error' in query_params:
                error = query_params['error'][0]
                error_description = query_params.get('error_description', [''])[0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"<html><body><h1>Error de Autorizacion</h1><p>{error}: {error_description}</p></body></html>".encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid request")
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        return  # Silenciar logs del servidor

def start_server():
    server = HTTPServer(('localhost', 8000), OAuthHandler)
    while auth_code is None:
        server.handle_request()
    return auth_code

def main():
    print("\n" + "="*50)
    print("🤖 AUTENTICACIÓN DE LINKEDIN PARA FV INVERSIONES")
    print("="*50 + "\n")
    
    # 1. Generar URL de autorización
    auth_url = "https://www.linkedin.com/oauth/v2/authorization"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "w_member_social openid profile email" 
    }
    
    url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    print("👉 Por favor, haz clic en el siguiente enlace para iniciar sesión en LinkedIn y autorizar a la app:")
    print("\n" + url + "\n")
    print("⏳ Esperando a que completes la autorización en el navegador...")
    
    # 2. Iniciar servidor local y esperar el código
    code = start_server()
    print("✅ ¡Código de autorización recibido!")
    
    # 3. Intercambiar código por Access Token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    print("🔄 Obteniendo el Token de Acceso...")
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        print("✅ ¡Token de acceso obtenido con éxito!")
        
        # 4. Guardar token en .env
        env_path = ".env"
        with open(env_path, "a") as f:
            f.write(f"\nLINKEDIN_ACCESS_TOKEN={access_token}\n")
            
        print("\n🎉 ¡Listo! El LINKEDIN_ACCESS_TOKEN se ha guardado automáticamente en tu archivo .env.")
        print("Ya puedes usar la API para publicar contenido de forma automática.")
    else:
        print("❌ Error al obtener el token:", response.text)

if __name__ == "__main__":
    main()
