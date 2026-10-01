import os
import glob
import json
import re

def get_latest_posts(base_dir, max_posts=3):
    # Find all post_*.md files in date folders
    search_pattern = os.path.join(base_dir, "202*", "post_*.md")
    files = glob.glob(search_pattern)
    
    # Sort files by the folder date descending
    files.sort(key=lambda x: os.path.basename(os.path.dirname(x)), reverse=True)
    
    posts = []
    
    for file_path in files[:max_posts]:
        date_str = os.path.basename(os.path.dirname(file_path))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        title = ""
        body_lines = []
        
        # Clean lines
        lines = [line.strip() for line in lines if line.strip() and not line.startswith('---')]
        
        # Find Title and Body
        for line in lines:
            if "Título sugerido" in line or "Titulo sugerido" in line:
                continue
            if not title:
                title = line.strip('#').strip()
                continue
            body_lines.append(line)
            
        if not title:
            title = "Perspectiva de Mercado"
            
        full_body = " ".join(body_lines)
        
        # Clean markdown characters for excerpt
        clean_body = re.sub(r'[\*\_]', '', full_body)
        
        # Create excerpt (around 20 words or ~120 chars)
        words = clean_body.split()
        excerpt = " ".join(words[:25]) + "..." if len(words) > 25 else clean_body
        
        posts.append({
            "date": date_str,
            "title": title,
            "excerpt": excerpt,
            "link": "https://www.linkedin.com/in/francisco-valencia/recent-activity/all/"
        })
        
    return posts

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    posts_dir = os.path.join(current_dir, "..", "linkedin_posts")
    public_dir = os.path.join(current_dir, "public")
    
    os.makedirs(public_dir, exist_ok=True)
    
    posts = get_latest_posts(posts_dir, 3)
    
    output_path = os.path.join(public_dir, "news.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        
    print(f"Sincronizados {len(posts)} posts en {output_path}")
