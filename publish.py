from pathlib import Path
import subprocess

from config import GITHUB_REPO

COMMIT_MESSAGE = "Automated render update"

# -----------------------------
# Git pull first
# -----------------------------
subprocess.run(
    ["git", "pull", "origin", "main", "--rebase"],
    cwd=GITHUB_REPO,
    check=True
)

# -----------------------------
# Stage all changes
# -----------------------------
subprocess.run(
    ["git", "add", "."],
    cwd=GITHUB_REPO,
    check=True
)

# -----------------------------
# Check if anything changed
# -----------------------------
status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=GITHUB_REPO,
    capture_output=True,
    text=True,
    check=True
)

if not status.stdout.strip():
    print("✅ No changes to commit.")
else:
    subprocess.run(
        ["git", "commit", "-m", COMMIT_MESSAGE],
        cwd=GITHUB_REPO,
        check=True
    )

    subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=GITHUB_REPO,
        check=True
    )

    print("✅ Changes committed and pushed.")
