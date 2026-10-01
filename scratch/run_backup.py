import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.backup_manager import create_system_backup
backup_path = create_system_backup()
print("Backup guardado en:", backup_path)
