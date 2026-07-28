from pathlib import Path
import shutil

# -----------------------------
# Configuration
# -----------------------------
SOURCE_DIR = Path(r"E:\PythonRender\image_renderer")
ARCHIVE_DIR = SOURCE_DIR / "old_timelines"

TIMELINE_PREFIX = "MemberEventTimeline_FULL_"
KEEP_LATEST = 3

# -----------------------------
# Find latest timeline in source
# -----------------------------
timeline_files = list(SOURCE_DIR.glob(f"{TIMELINE_PREFIX}*.csv"))

if not timeline_files:
    raise FileNotFoundError(
        f"No files found matching {TIMELINE_PREFIX}*.csv in {SOURCE_DIR}"
    )

latest_timeline = max(timeline_files, key=lambda p: p.stat().st_mtime)
print(f"[INFO] Latest timeline detected: {latest_timeline.name}")

# -----------------------------
# Move latest timeline to archive
# -----------------------------
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
destination = ARCHIVE_DIR / latest_timeline.name

shutil.move(str(latest_timeline), destination)
print(f"[DONE] Moved to archive: {destination}")

# -----------------------------
# Cleanup old timelines (keep last N)
# -----------------------------
archived_files = sorted(
    ARCHIVE_DIR.glob(f"{TIMELINE_PREFIX}*.csv"),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

if len(archived_files) <= KEEP_LATEST:
    print(
        f"[INFO] Archive contains {len(archived_files)} file(s). "
        f"No cleanup needed (keeping {KEEP_LATEST})."
    )
else:
    files_to_delete = archived_files[KEEP_LATEST:]

    for f in files_to_delete:
        f.unlink()
        print(f"[REMOVED] Deleted old timeline: {f.name}")

    print(
        f"[DONE] Cleanup complete. "
        f"Kept {KEEP_LATEST}, removed {len(files_to_delete)}."
    )
