import shutil
from pathlib import Path
import subprocess

# -----------------------------
# Configuration
# -----------------------------
SOURCE_DIR = Path(r"E:\PythonRender\image_renderer\renders_script")
REPO_DIR = Path(r"E:\GitHub\CubPackImages")
DEST_DIR = REPO_DIR / "docs"

COMMIT_MESSAGE = "Automated render update"

# -----------------------------
# Step 1: Copy rendered images to repo
# -----------------------------
DEST_DIR.mkdir(parents=True, exist_ok=True)

for img_file in SOURCE_DIR.glob("*.png"):
    dest_file = DEST_DIR / img_file.name
    shutil.copy2(img_file, dest_file)
    print(f"[COPY] {img_file.name}")

# -----------------------------
# Step 2: Git pull first to avoid push errors
# -----------------------------
subprocess.run(["git", "pull", "origin", "main", "--rebase"], cwd=REPO_DIR)

# -----------------------------
# Step 3: Git add / commit / push
# -----------------------------
# Stage changes
subprocess.run(["git", "add", "."], cwd=REPO_DIR)

# Check if there’s anything to commit
status_result = subprocess.run(
    ["git", "status", "--porcelain"], cwd=REPO_DIR, capture_output=True, text=True
)

if status_result.stdout.strip() == "":
    print("✅ No changes to commit.")
else:
    # Commit changes
    subprocess.run(["git", "commit", "-m", COMMIT_MESSAGE], cwd=REPO_DIR)
    # Push to remote
    subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR)
    print("[PUSH] Changes committed and pushed to GitHub.")