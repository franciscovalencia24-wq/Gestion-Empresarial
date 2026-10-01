import glob

files = glob.glob('src/**/*.py', recursive=True)
count = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'use_container_width=True' in content or 'use_container_width=False' in content:
        new_content = content.replace('use_container_width=True', 'width="stretch"').replace('use_container_width=False', 'width="content"')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        count += 1
        print(f'Updated {f}')

print(f'\nTotal files updated: {count}')
