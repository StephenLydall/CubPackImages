import subprocess
import sys
from pathlib import Path

# List scripts in the exact order they must run
SCRIPTS = [
    "build_member_event_timeline.py",
    "find_images_to_render.py",
    "render.py",
    "save_csv_to_powerbi.py",
    "archive_csv.py",
    "publish.py",
]

def run_script(script_name):
    script_path = Path(script_name)

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_name}")

    print(f"\n-- Running {script_name} ...")
    
    subprocess.run(
        [sys.executable, script_name],
        check=True
    )

    print(f"[OK] Finished {script_name}")

def main():
    print("Starting update_keys pipeline")

    for script in SCRIPTS:
        run_script(script)

    print("\nAll scripts completed successfully")

if __name__ == "__main__":
    main()
