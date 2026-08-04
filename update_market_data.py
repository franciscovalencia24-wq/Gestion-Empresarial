import sys
import re

def update_file():
    with open('src/osint/market_data_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target = "data['impacto_local']['commodities'] = commodity_stats"
    
    replace_with = """data['impacto_local']['commodities'] = commodity_stats
            
            if mode == 'auto_chile':
                # El usuario solicitó que para noticias de Chile, todo se muestre como NEUTRAL y LEVE
                # para no generar falsas alarmas de impacto por una noticia local.
                for region, indices in global_stats.items():
                    for idx in indices:
                        idx['efecto'] = 'NEUTRAL'
                        idx['relevancia'] = 'LEVE'
                        
                for item in data['impacto_local'].get('monedas', []):
                    item['efecto'] = 'NEUTRAL'
                    item['relevancia'] = 'LEVE'
                    
                for item in data['impacto_local'].get('commodities', []):
                    item['efecto'] = 'NEUTRAL'
                    item['relevancia'] = 'LEVE'
                    
                for item in data['impacto_local'].get('fondos_mutuos', []):
                    item['efecto'] = 'NEUTRAL'
                    item['relevancia'] = 'LEVE'
                    
                for item in data['impacto_local'].get('multifondos', []):
                    item['efecto'] = 'NEUTRAL'
                    item['relevancia'] = 'LEVE'"""

    if target in content:
        content = content.replace(target, replace_with)
        with open('src/osint/market_data_engine.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated successfully")
    else:
        print("Target not found")

update_file()
