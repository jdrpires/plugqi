import shutil
import os

base_path = r"c:\Users\Fenixzin\OneDrive\Documentos\SantosRSystems\Clients\CodeSynergy\plugqi\api\routers"
target_path = os.path.join(base_path, "onboarding")

files_to_move = ["documents.py", "risk.py", "escrow.py"]

if not os.path.exists(target_path):
    os.makedirs(target_path)

for filename in files_to_move:
    src = os.path.join(base_path, filename)
    dst = os.path.join(target_path, filename)
    
    if os.path.exists(src):
        print(f"Moving {src} to {dst}")
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"Error moving {filename}: {e}")
    else:
        print(f"{filename} not found in source, checking target...")
        if os.path.exists(dst):
            print(f"{filename} is already in target.")
        else:
            print(f"{filename} is MISSING entirely!")
