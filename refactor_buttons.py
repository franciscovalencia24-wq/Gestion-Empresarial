with open('src/web/client_management_ui_new.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('        if has_360_data:'):
        start_idx = i
        break

for i in range(start_idx, len(lines)):
    if line.startswith('        st.markdown("---")'):
        pass # this doesn't help

# Let's find the exact block to replace.
# The block ends after `st.rerun()` in the `if not is_b2b:` else branch.
# Let's read the file and replace it properly.
