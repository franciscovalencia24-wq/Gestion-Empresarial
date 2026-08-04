import os, glob

for f in glob.glob("scratch/test_*.py") + glob.glob("scratch/migrate_*.py") + glob.glob("scratch/find_*.py") + glob.glob("scratch/check_*.py"):
    try:
        os.remove(f)
        print(f"Removed temporary file: {f}")
    except Exception as e:
        print(f"Error removing {f}: {e}")
