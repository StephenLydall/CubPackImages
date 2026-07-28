import pandas as pd
from datetime import datetime

EXCEL_PATH = r"E:\Solv Design Studio\Solv - Documents\Stephen\Member Database SP.xlsx"

# -------------------------------------------------
# BLOCK 1: Load tables
# -------------------------------------------------

participation = pd.read_excel(
    EXCEL_PATH,
    sheet_name="Participation Table",
    header=8,
    engine="openpyxl"
)
participation.columns = participation.columns.str.strip()

programs = pd.read_excel(
    EXCEL_PATH,
    sheet_name="Program Table",
    header=2,
    engine="openpyxl"
)
programs.columns = programs.columns.str.strip()

sixlog = pd.read_excel(
    EXCEL_PATH,
    sheet_name="SixLog",
    header=0,
    engine="openpyxl"
)
sixlog.columns = sixlog.columns.str.strip()

interest_badges = pd.read_excel(
    EXCEL_PATH,
    sheet_name="Interest Badge Log",
    header=0,
    engine="openpyxl"
)
interest_badges.columns = interest_badges.columns.str.strip()

advancements = pd.read_excel(
    EXCEL_PATH,
    sheet_name="Advancement Log",
    header=0,
    engine="openpyxl"
)
advancements.columns = advancements.columns.str.strip()

# -------------------------------------------------
# BLOCK 2: Build participation timeline
# -------------------------------------------------

participation = participation.drop(
    columns=[c for c in ["Date", "ProgramDate"] if c in participation.columns]
)

timeline = participation.merge(
    programs,
    on="ProgramCode",
    how="left"
).rename(columns={"Date": "ProgramDate"})

timeline["ProgramDate"] = pd.to_datetime(timeline["ProgramDate"])

timeline["MemberEventKey"] = (
    timeline["MemberID"].astype(str) + "|" +
    timeline["ProgramCode"].astype(str)
)

final_df = timeline[
    ["MemberEventKey", "MemberID", "ProgramCode", "ProgramDate", "ParticipationStatus"]
].copy()

final_df = final_df.sort_values(
    ["MemberID", "ProgramDate"]
).reset_index(drop=True)

# -------------------------------------------------
# BLOCK 3: Rank calculation (with Investiture boundary + Legacy handling)
# -------------------------------------------------

investiture_log = advancements[
    advancements["AdvancementCode"] == "AD001"
].copy()

investiture_log["InvestitureDate"] = pd.to_datetime(
    investiture_log["AdvancementDate.1"],
    errors="coerce"
)

investiture_info = {}

for member_id, grp in investiture_log.groupby("MemberID"):
    min_date = grp["InvestitureDate"].min()
    has_null = grp["InvestitureDate"].isna().any()

    investiture_info[member_id] = {
        "date": min_date,
        "legacy": has_null and pd.isna(min_date)
    }

def calculate_rank(member_id, program_date):
    rank = "Chum"

    invest_info = investiture_info.get(member_id)

    if invest_info:
        invest_date = invest_info["date"]
        is_legacy = invest_info["legacy"]

        if pd.notna(invest_date) and program_date >= invest_date:
            rank = "Member"
        elif is_legacy:
            rank = "Member"

    logs = sixlog[
        (sixlog["MemberID"] == member_id) &
        (sixlog["SixDateJoin"] <= program_date)
    ]

    if not logs.empty:
        latest_six = logs.sort_values("SixDateJoin").iloc[-1]["SixPosition"]
        if latest_six in ["Second", "Sixer", "Senior Sixer"]:
            rank = latest_six

    return rank

final_df["Rank"] = final_df.apply(
    lambda r: calculate_rank(r["MemberID"], r["ProgramDate"]),
    axis=1
)

# -------------------------------------------------
# BLOCK 4: CorrectedRank (carry forward across absences)
# -------------------------------------------------

final_df["CorrectedRank"] = None

for member_id, grp in final_df.groupby("MemberID"):
    last_rank = None

    for idx in grp.index:
        if final_df.at[idx, "ParticipationStatus"] == 1:
            last_rank = final_df.at[idx, "Rank"]
            final_df.at[idx, "CorrectedRank"] = last_rank
        else:
            if last_rank is None:
                final_df.at[idx, "CorrectedRank"] = final_df.at[idx, "Rank"]
                last_rank = final_df.at[idx, "Rank"]
            else:
                final_df.at[idx, "CorrectedRank"] = last_rank

# -------------------------------------------------
# BLOCK 4b: Map CorrectedRank to R-codes
# -------------------------------------------------

RANK_MAP = {
    "Chum": "R01",
    "Member": "R02",
    "Second": "R03",
    "Sixer": "R04",
    "Senior Sixer": "R05"
}

final_df["RankCode"] = final_df["CorrectedRank"].map(RANK_MAP)

# -------------------------------------------------
# BLOCK 5: Promotion detection
# -------------------------------------------------

PROMOTION_RULES = {
    ("Member", "Second"),
    ("Member", "Sixer"),
    ("Member", "Senior Sixer"),
    ("Second", "Sixer"),
    ("Second", "Senior Sixer"),
    ("Sixer", "Senior Sixer"),
}

final_df["Promotion"] = None
final_df["PromotionFrom"] = None
final_df["PromotionTo"] = None

for member_id, grp in final_df.groupby("MemberID"):
    prev_rank = None
    for idx in grp.index:
        curr_rank = final_df.at[idx, "CorrectedRank"]
        if prev_rank and curr_rank and (prev_rank, curr_rank) in PROMOTION_RULES:
            final_df.at[idx, "Promotion"] = f"{prev_rank} → {curr_rank}"
            final_df.at[idx, "PromotionFrom"] = prev_rank
            final_df.at[idx, "PromotionTo"] = curr_rank
        prev_rank = curr_rank

# -------------------------------------------------
# BLOCK 6: First & last attended dates
# -------------------------------------------------

attended = final_df[final_df["ParticipationStatus"] == 1]

first_attended = attended.groupby("MemberID")["ProgramDate"].min()
last_attended = attended.groupby("MemberID")["ProgramDate"].max()

# -------------------------------------------------
# BLOCK 7: Identify Pack Programs (PP) – null-safe
# -------------------------------------------------

# Null-safe PP determination: null counts as not disqualifying
programs["IsPP"] = (
    ((programs["Location"].isna()) | (programs["Location"] == "Home")) &
    ((programs["Participation"].isna()) | (programs["Participation"] == "All")) &
    ((programs["Branch"].isna()) | (programs["Branch"] == "Pack"))
)

# Sort by date and build GroupCode
programs = programs.sort_values("Date").reset_index(drop=True)
programs["GroupCode"] = None

for i, row in programs.iterrows():
    if i == 0:
        programs.at[i, "GroupCode"] = row["ProgramCode"]
    else:
        prev_overnight = programs.at[i - 1, "OverNight"]
        if prev_overnight:
            programs.at[i, "GroupCode"] = programs.at[i - 1, "GroupCode"]
        else:
            programs.at[i, "GroupCode"] = row["ProgramCode"]

# Identify camps: multiple programs share the same GroupCode
group_counts = programs.groupby("GroupCode")["ProgramCode"].nunique()
programs["IsCamp"] = programs["GroupCode"].map(lambda x: group_counts[x] > 1)

# Final PP: must satisfy conditions and not be a camp
programs["IsPP"] = programs["IsPP"] & (~programs["IsCamp"])

# -------------------------------------------------
# BLOCK 8: Apply awards
# -------------------------------------------------

def assign_pp_badges(log_df, code_col, date_col, program_table):
    result = {}

    log_df[date_col] = pd.to_datetime(log_df[date_col], errors="coerce")
    pp_programs = program_table[program_table["IsPP"]].copy()
    pp_programs["ProgramDate"] = pd.to_datetime(pp_programs["Date"], errors="coerce")

    for _, row in log_df.iterrows():
        member = row["MemberID"]
        award = row[code_col]
        award_date = row[date_col]

        if pd.isna(award_date):
            continue
        if member not in first_attended:
            continue
        if award_date < first_attended[member]:
            continue

        # Include IsPP in merge to avoid KeyError
        eligible = attended[
            (attended["MemberID"] == member) &
            (attended["ProgramDate"] >= award_date)
        ].merge(
            pp_programs[["ProgramCode", "ProgramDate", "IsPP"]],  # <-- fix applied
            left_on="ProgramCode",
            right_on="ProgramCode",
            how="left",
            suffixes=("", "_pp")
        )

        eligible = eligible[eligible["IsPP"].fillna(False)]

        if not eligible.empty:
            chosen_date = eligible["ProgramDate"].min()
        else:
            chosen_date = last_attended[member]

        mek = final_df[
            (final_df["MemberID"] == member) &
            (final_df["ProgramDate"] == chosen_date)
        ]["MemberEventKey"].iloc[0]

        result.setdefault(mek, []).append(award)

    return {k: ",".join(sorted(set(v))) for k, v in result.items()}

badge_map = assign_pp_badges(
    interest_badges,
    "BadgeCode",
    "AwardDate.1",
    programs
)

def assign_awards(log_df, code_col, date_col):
    result = {}

    log_df[date_col] = pd.to_datetime(log_df[date_col], errors="coerce")

    for _, row in log_df.iterrows():
        member = row["MemberID"]
        award = row[code_col]
        award_date = row[date_col]

        if pd.isna(award_date):
            continue
        if member not in first_attended:
            continue
        if award_date < first_attended[member]:
            continue

        eligible = attended[
            (attended["MemberID"] == member) &
            (attended["ProgramDate"] >= award_date)
        ]

        if not eligible.empty:
            chosen_date = eligible["ProgramDate"].min()
        else:
            chosen_date = last_attended[member]

        mek = final_df[
            (final_df["MemberID"] == member) &
            (final_df["ProgramDate"] == chosen_date)
        ]["MemberEventKey"].iloc[0]

        result.setdefault(mek, []).append(award)

    return {k: ",".join(sorted(set(v))) for k, v in result.items()}

adv_map = assign_awards(
    advancements,
    "AdvancementCode",
    "AdvancementDate.1"
)

final_df["InterestBadges"] = final_df["MemberEventKey"].map(badge_map).fillna("")
final_df["Advancements"] = final_df["MemberEventKey"].map(adv_map).fillna("")

# -------------------------------------------------
# BLOCK 9: Build PCode
# -------------------------------------------------

def build_pcode(row):
    if row.get("ParticipationStatus", 0) == 0:
        return "0"

    P = row.get("PromotionTo")
    AD = [a.strip() for a in str(row.get("Advancements", "")).split(",") if a.strip()]
    I = [i.strip() for i in str(row.get("InterestBadges", "")).split(",") if i.strip()]
    num_AD = len(AD)
    num_I = len(I)
    x = (1 if pd.notna(P) else 0) + num_AD + num_I

    if x == 0:
        return "Tick"

    if x <= 6:
        code_list = []
        if pd.notna(P): code_list.append(P)
        code_list.extend(AD)
        code_list.extend(I)
        return ",".join(code_list)

    code_list = []

    if pd.notna(P):
        code_list.append(P)
        if num_AD == 3:
            code_list.extend(AD[:3])
            code_list.append(I[1])
            code_list.append("b")
        elif num_AD == 2:
            code_list.extend(AD[:2])
            code_list.extend(I[:2])
            code_list.append("b")
        elif num_AD == 1:
            code_list.extend(AD[:1])
            code_list.extend(I[:3])
            code_list.append("b")
        elif num_AD == 0:
            code_list.extend(I[:4])
            code_list.append("b")
        elif num_I == 2:
            code_list.extend(AD[:2])
            code_list.append("a")
            code_list.extend(I[:2])
        elif num_I == 1:
            code_list.extend(AD[:3])
            code_list.append("a")
            code_list.extend(I[:1])
        elif num_I == 0:
            code_list.extend(AD[:4])
            code_list.append("a")
        else:
            code_list.extend(AD[:2])
            code_list.extend(I[:2])
            code_list.append("ab")
    else:
        if num_AD == 3:
            code_list.extend(AD[:3])
            code_list.extend(I[:2])
            code_list.append("b")
        elif num_AD == 2:
            code_list.extend(AD[:2])
            code_list.extend(I[:3])
            code_list.append("b")
        elif num_AD == 1:
            code_list.extend(AD[:1])
            code_list.extend(I[:4])
            code_list.append("b")
        elif num_AD == 0:
            code_list.extend(I[:5])
            code_list.append("b")
        elif num_I == 3:
            code_list.extend(AD[:2])
            code_list.append("a")
            code_list.extend(I[:3])
        elif num_I == 2:
            code_list.extend(AD[:3])
            code_list.append("a")
            code_list.extend(I[:2])
        elif num_I == 1:
            code_list.extend(AD[:4])
            code_list.append("a")
            code_list.extend(I[:1])
        elif num_I == 0:
            code_list.extend(AD[:5])
            code_list.append("a")
        else:
            code_list.extend(AD[:3])
            code_list.extend(I[:2])
            code_list.append("ab")

    return ",".join(code_list)

final_df["PCode"] = final_df.apply(build_pcode, axis=1)

# -------------------------------------------------
# BLOCK 10: Build FullCode
# -------------------------------------------------

final_df["FullCode"] = final_df["RankCode"] + "," + final_df["PCode"]

# -------------------------------------------------
# BLOCK 10b: Build Image filename
# -------------------------------------------------

final_df["ImageFile"] = (
    final_df["FullCode"]
    .str.replace(",", "_", regex=False)
    .str.strip()
    + ".png"
)

# -------------------------------------------------
# BLOCK 11: Export
# -------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"MemberEventTimeline_FULL_{timestamp}.csv"

final_df.to_csv(output_file, index=False)

print(f"[DONE] {output_file} created")
print(final_df.head(10))