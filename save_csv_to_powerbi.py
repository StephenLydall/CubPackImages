import pandas as pd

from config import (
    TIMELINE_CSV,
    GITHUB_DATA,
)

# -----------------------------
# Configuration
# -----------------------------
OUTPUT_FILE = GITHUB_DATA / "MemberEventKey.csv"

REQUIRED_COLUMNS = ["MemberEventKey", "ImageFile"]

# -----------------------------
# Load timeline CSV
# -----------------------------
if not TIMELINE_CSV.exists():
    raise FileNotFoundError(f"{TIMELINE_CSV} not found.")

print(f"[INFO] Using timeline: {TIMELINE_CSV.name}")

# -----------------------------
# Load and validate CSV
# -----------------------------
df = pd.read_csv(TIMELINE_CSV)

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
GITHUB_DATA.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"[DONE] {OUTPUT_FILE.name} created")
print(f"[INFO] Total keys: {len(df)}")
