import json
import re

log_path = r'C:\Users\franc\.gemini\antigravity-ide\brain\ca7f332c-87ca-4227-945f-c56f5eeafef5\.system_generated\logs\transcript.jsonl'
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if 'fv-registro' in content or 'fv-gestion' in content:
                print(f"[{data.get('type')}] {content[:150]}")
        except Exception:
            pass
