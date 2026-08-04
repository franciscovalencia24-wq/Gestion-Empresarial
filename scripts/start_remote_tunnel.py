import os
import sys
import urllib.request
import subprocess
import re
import time

def ensure_cloudflared():
    bin_dir = os.path.join(os.getcwd(), "scripts", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    exe_path = os.path.join(bin_dir, "cloudflared.exe")

    if not os.path.exists(exe_path):
        print("📥 Descargando motor de túnel remoto seguro de Cloudflare (cloudflared.exe)...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        urllib.request.urlretrieve(url, exe_path)
        print("✅ Descarga completada exitosamente.")

    return exe_path

def start_tunnel(port=8501):
    exe_path = ensure_cloudflared()
    print(f"🚀 Iniciando Túnel Remoto Seguro para http://localhost:{port}...")
    
    cmd = [exe_path, "tunnel", "--url", f"http://localhost:{port}"]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[-a-zA-Z0-9.]+\.trycloudflare\.com")

    # Read output line by line until URL is found
    for line in iter(process.stdout.readline, ''):
        match = url_pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            break

    if tunnel_url:
        url_file = os.path.join(os.getcwd(), "REMOTE_MOBILE_URL.txt")
        with open(url_file, "w", encoding="utf-8") as f:
            f.write(tunnel_url)

        print("\n" + "=" * 70)
        print("🌐 TÚNEL REMOTO PRIVADO Y SEGURO ACTIVO FOR ANTIGRAVITY MOBILE")
        print("=" * 70)
        print("👉 Abre esta URL en Safari o Chrome desde tu celular en 4G/5G:")
        print(f"\n   🔗 {tunnel_url}\n")
        print("📌 Tu PC local (localhost:8501) ya está conectada en tiempo real.")
        print("📌 Ingresa a la opción '📱 5. Chat Remoto Antigravity' e ingresa tu PIN (2026).")
        print("=" * 70 + "\n")
    else:
        print("⚠️ No se pudo obtener la URL automáticamente. Revisa la consola de cloudflared.")

    # Keep process running
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Túnel remoto finalizado.")
        process.terminate()

if __name__ == "__main__":
    start_tunnel(8501)
