import os
import requests
import json
from dotenv import load_dotenv

def create_linkedin_post():
    # 1. Cargar el token desde .env
    load_dotenv()
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ Error: No se encontró LINKEDIN_ACCESS_TOKEN en el archivo .env")
        return
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    print("🔍 Obteniendo el ID interno del autor...")
    user_info_url = "https://api.linkedin.com/v2/userinfo"
    res_user = requests.get(user_info_url, headers=headers)
    
    if res_user.status_code != 200:
        print(f"❌ Error al obtener tu ID: {res_user.json()}")
        return
        
    sub = res_user.json().get("sub")
    author_urn = f"urn:li:person:{sub}"
    name = res_user.json().get("given_name", "Autor")
    
    print(f"✅ ¡Hola {name}! Tu ID interno de LinkedIn es: {author_urn}")
    print("🚀 Preparando la publicación de la Recomendación Táctica...")

    # 2. Armar el contenido del Post
    # El texto de la publicación
    post_text = (
        "📊 [Visión Macro Consolidada - FV Asesorías e Inversiones]\n\n"
        "Hemos actualizado nuestra recomendación táctica con base en un compilado estratégico "
        "de reportes públicos de las principales instituciones financieras chilenas y globales.\n\n"
        "El mercado global presenta oportunidades clave que debes conocer para proteger "
        "e incrementar tu patrimonio en el actual escenario.\n\n"
        "Lee el análisis completo y revisa nuestra perspectiva del S&P 500 en nuestra web:\n"
        "👉 https://fv-inversiones.com/"
    )

    # El cuerpo de la solicitud para la API de LinkedIn
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": "https://fv-inversiones.com/",
                        "title": {
                            "text": "Visión Macro Consolidada | FV Inversiones"
                        },
                        "description": {
                            "text": "Análisis del mercado y recomendación de asignación de activos."
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # 3. Enviar el POST a LinkedIn
    print("📡 Enviando publicación a LinkedIn...")
    res_post = requests.post(post_url, headers=headers, json=post_data)
    
    if res_post.status_code == 201:
        print("\n🎉 ¡PUBLICACIÓN EXITOSA! 🎉")
        post_id = res_post.json().get("id")
        print(f"ID del Post: {post_id}")
        print("Revisa tu perfil de LinkedIn (Francisco Valencia), ¡ya debería estar publicado!")
        print("\nNota: Una vez que Microsoft apruebe el acceso corporativo, ")
        print("cambiaremos 'urn:li:person' por 'urn:li:organization' para publicar como FV Inversiones.")
    else:
        print(f"\n❌ Falló la publicación: {res_post.status_code}")
        print(res_post.json())

if __name__ == "__main__":
    print("="*60)
    print("🤖 ROBOT PUBLICADOR DE LINKEDIN - FV INVERSIONES")
    print("="*60)
    create_linkedin_post()
