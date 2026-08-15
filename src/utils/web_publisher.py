import os
import re
import subprocess
import markdown

def publish_consensus_to_vercel(texto_consenso: str, periodo: str):
    """
    Publica el consenso de mercado a fv-inversiones.com localmente y empuja los cambios a git.
    """
    try:
        # 1. Convert markdown to HTML
        html_content = markdown.markdown(texto_consenso)
        
        # 2. Add inline styles to standard markdown tags to match the glass-card dark theme
        html_content = html_content.replace('<h3>', '<h3 style="color: #fff; margin-top: 24px; margin-bottom: 12px; font-size: 20px;">')
        html_content = html_content.replace('<h2>', '<h2 style="color: #fff; margin-top: 24px; margin-bottom: 16px; font-size: 22px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">')
        html_content = html_content.replace('<p>', '<p style="margin-bottom: 16px;">')
        html_content = html_content.replace('<ul>', '<ul style="list-style-type: none; padding-left: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">')
        html_content = html_content.replace('<li>', '<li style="display: flex; align-items: flex-start; gap: 12px;"><div style="width: 8px; height: 8px; background: var(--color-primary-gold); border-radius: 50%; margin-top: 8px; flex-shrink: 0;"></div> ')
        html_content = html_content.replace('<strong>', '<strong style="color: #fff;">')
        
        # Structure the container based on the template
        final_html = f"""
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 24px; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 16px;">
              <i data-lucide="bar-chart-2" style="color: var(--color-primary-gold); width: 32px; height: 32px;"></i>
              <h3 style="font-size: 24px; font-weight: 700; color: #fff; margin: 0;">Recomendación Táctica</h3>
            </div>
            <span style="background: rgba(197, 160, 89, 0.1); color: var(--color-primary-gold); padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; border: 1px solid rgba(197, 160, 89, 0.3);">
              Actualización: {periodo}
            </span>
          </div>
          
          <div style="color: #cbd5e1; font-size: 16px; line-height: 1.8;" class="consensus-body">
            {html_content}
          </div>
"""
        
        # Locate index.html
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        index_path = os.path.join(project_root, "frontend", "index.html")
        
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Replace between markers
        pattern = r"<!-- CONSENSO_START -->.*?<!-- CONSENSO_END -->"
        replacement = f"<!-- CONSENSO_START -->\n{final_html}\n          <!-- CONSENSO_END -->"
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        # Push to git
        subprocess.run(["git", "add", "frontend/index.html"], cwd=project_root, check=True)
        subprocess.run(["git", "commit", "-m", f"update: Consenso Mercado {periodo} inyectado"], cwd=project_root, check=True)
        subprocess.run(["git", "push"], cwd=project_root, check=True)
        
        return True, "Publicado y enviado a Vercel con éxito."
    except Exception as e:
        return False, str(e)
