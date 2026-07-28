from pathlib import Path

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

# ==========================================================
# Excel Database
# ==========================================================

EXCEL_FILE = PROJECT_ROOT / "Member Database SP.xlsx"

# ==========================================================
# Local Pipeline Files
# ==========================================================

TIMELINE_CSV = PROJECT_ROOT / "MemberEventTimeline.csv"

TO_RENDER_CSV = PROJECT_ROOT / "ToRender.csv"

OLD_TIMELINES = PROJECT_ROOT / "old_timelines"
OLD_CSVS = PROJECT_ROOT / "old_csvs"

# ==========================================================
# GitHub Repository
# ==========================================================

# Change this one line if the repo ever moves

GITHUB_REPO = PROJECT_ROOT

GITHUB_DOCS = GITHUB_REPO / "docs"

GITHUB_DATA = GITHUB_REPO / "data"

APP_ASSETS = GITHUB_DOCS / "app-assets"

# ==========================================================
# Image Locations
# ==========================================================

# Shared badge images (used by both the app and renderer)
BASE_IMAGES = GITHUB_DOCS / "app-assets"

# Renderer-only assets
BACKGROUND_IMAGES = GITHUB_DOCS / "backgrounds"

OTHER_IMAGES = PROJECT_ROOT / "other_images"

LOCAL_RENDER_OUTPUT = PROJECT_ROOT / "renders_script"

MANUAL_RENDER_OUTPUT = PROJECT_ROOT / "renders_manual"
