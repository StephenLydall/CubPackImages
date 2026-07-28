from pathlib import Path

import pandas as pd

from config import GITHUB_DOCS, TIMELINE_CSV, TO_RENDER_CSV

# -----------------------------
# Step 1: Load Timeline CSV
# -----------------------------
if not TIMELINE_CSV.exists():
    raise FileNotFoundError(f"{TIMELINE_CSV} not found.")

df = pd.read_csv(TIMELINE_CSV)

# -----------------------------
# Step 2: Unique FullCodes
# -----------------------------
if "FullCode" not in df.columns:
    raise ValueError("Timeline CSV does not contain 'FullCode' column.")

unique_codes = df["FullCode"].dropna().unique()

# -----------------------------
# Step 3: Existing rendered images
# -----------------------------
existing_files = {
    f.name.lower().strip()
    for f in GITHUB_DOCS.glob("*.png")
}

# -----------------------------
# Step 4: Determine which images need rendering
# -----------------------------
debug_rows = []

for code in unique_codes:
    code_clean = code.strip()

    expected_filename = code_clean.replace(",", "_").lower() + ".png"

    exists = expected_filename in existing_files

    debug_rows.append({
        "FullCode": code_clean,
        "ExpectedFileName": expected_filename,
        "Exists": exists,
        "ToRender": not exists
    })

debug_df = pd.DataFrame(debug_rows)

# -----------------------------
# Step 5: Filter only images needing render
# -----------------------------
to_render_df = debug_df[debug_df["ToRender"]]

# -----------------------------
# Step 6: Save ToRender.csv
# -----------------------------
to_render_df.to_csv(TO_RENDER_CSV, index=False)

print(f"[DONE] {len(to_render_df)} images require rendering.")
print(f"[DONE] {TO_RENDER_CSV.name} created")
