import pandas as pd
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
SOURCE_DIR = Path(r"E:\PythonRender\image_renderer")
OUTPUT_DIR = Path(r"E:\Solv Design Studio\Solv - Documents\Stephen\PowerBI\PythonCSVs")
OUTPUT_FILE = OUTPUT_DIR / "MemberEventKey.csv"

TIMELINE_PREFIX = "MemberEventTimeline_FULL_"
REQUIRED_COLUMNS = ["MemberEventKey", "ImageFile"]

# -----------------------------
# Find latest timeline CSV
# -----------------------------
timeline_files = list(SOURCE_DIR.glob(f"{TIMELINE_PREFIX}*.csv"))

if not timeline_files:
    raise FileNotFoundError(
        f"No files found matching {TIMELINE_PREFIX}*.csv in {SOURCE_DIR}"
    )

latest_timeline = max(timeline_files, key=lambda p: p.stat().st_mtime)
print(f"[INFO] Using latest timeline: {latest_timeline.name}")

# -----------------------------
# Load and validate CSV
# -----------------------------
df = pd.read_csv(latest_timeline)

missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing_cols:
    raise ValueError(
        f"Timeline CSV missing required columns: {', '.join(missing_cols)}"
    )

df = df[REQUIRED_COLUMNS].copy()

# -----------------------------
# Deduplicate (last occurrence wins)
# -----------------------------
original_count = len(df)
df = df.drop_duplicates(subset="MemberEventKey", keep="last")
deduped_count = len(df)

if deduped_count < original_count:
    print(
        f"[WARN] Deduplicated MemberEventKey list: "
        f"{original_count - deduped_count} duplicates removed"
    )

# -----------------------------
# Write output CSV
# -----------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"[DONE] MemberEventKey mapping written to:")
print(f"   {OUTPUT_FILE}")
print(f"   Total keys: {len(df)}")
