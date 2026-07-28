import os
import pandas as pd
from glob import glob

# -----------------------------
# Step 1: Find latest CSV
# -----------------------------
csv_files = glob("MemberEventTimeline_FULL_*.csv")
if not csv_files:
    raise FileNotFoundError("No MemberEventTimeline CSV files found in folder.")

latest_csv = max(csv_files, key=os.path.getctime)
print(f"Using latest CSV: {latest_csv}")

df = pd.read_csv(latest_csv)

# -----------------------------
# Step 2: Unique FullCodes
# -----------------------------
if "FullCode" not in df.columns:
    raise ValueError("CSV does not contain 'FullCode' column!")

unique_codes = df["FullCode"].dropna().unique()

# -----------------------------
# Step 3: List all files in folders
# -----------------------------
folders = {
    "renders_manual": "renders_manual",
    "renders_script": "renders_script"
}

file_lists = {}
for key, folder in folders.items():
    if os.path.exists(folder):
        file_lists[key] = [
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(".png")
        ]
    else:
        print(f"Warning: folder '{folder}' does not exist")
        file_lists[key] = []

# -----------------------------
# Step 4: Build debug DataFrame
# -----------------------------
debug_rows = []

# normalize file lists
manual_files_norm = [f.lower().strip() for f in file_lists["renders_manual"]]
script_files_norm = [f.lower().strip() for f in file_lists["renders_script"]]

for code in unique_codes:
    code_clean = code.strip()
    expected_filename = code_clean.replace(",", "_").lower() + ".png"

    in_manual = expected_filename in manual_files_norm
    in_script = expected_filename in script_files_norm
    to_render = not (in_manual or in_script)

    debug_rows.append({
        "FullCode": code_clean,
        "ExpectedFileName": expected_filename,
        "IsIn_renders_manual": in_manual,
        "IsIn_renders_script": in_script,
        "ToRender": to_render
    })

debug_df = pd.DataFrame(debug_rows)

# -----------------------------
# Step 5: Filter only rows where ToRender is True
# -----------------------------
to_render_df = debug_df[debug_df["ToRender"] == True]

# -----------------------------
# Step 6: Output CSV
# -----------------------------
output_csv = "ToRender.csv"
to_render_df.to_csv(output_csv, index=False)
print(f"[DONE] Filtered ToRender CSV created: {output_csv}")


