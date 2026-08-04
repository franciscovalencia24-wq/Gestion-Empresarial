import json
import sys

log_path = r'C:\Users\franc\.gemini\antigravity-ide\brain\52b2149e-ba09-4b1f-95ee-6137f8c661ac\.system_generated\logs\transcript_full.jsonl'

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        if '"type":"PLANNER_RESPONSE"' in line and '"name":"write_to_file"' in line:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            for call in tool_calls:
                if call['name'] == 'write_to_file':
                    args = call.get('args', {})
                    target = args.get('TargetFile', '')
                    if 'carrusel_diario.html' in target:
                        with open('scratch/carrusel_write.txt', 'w', encoding='utf-8') as out:
                            out.write(args.get('CodeContent', ''))
                    elif 'infografia_diaria.html' in target:
                        with open('scratch/infografia_write.txt', 'w', encoding='utf-8') as out:
                            out.write(args.get('CodeContent', ''))

