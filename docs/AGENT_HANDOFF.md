# 🤖 Agent Handoff & Project Context

**Date**: December 2, 2025
**Project**: Open-Agri OS
**Current State**: Stable, Refactored, Split-View UI

## 1. Project Overview
Open-Agri OS is a Flask-based web application for agricultural intelligence. It provides:
- **Dashboard**: Farm stats and charts.
- **Agri-Scout**: Satellite imagery (Sentinel-2) and crop suitability analysis.
- **Agri-Doctor**: AI-based plant disease diagnosis (MobileNetV2/Gemini).
- **Weather**: Real-time weather data (Open-Meteo).

## 2. Architecture & Refactoring (Crucial Context)
The project was recently refactored from a flat directory to a modular structure to support scalability and GitHub best practices.

### Directory Structure
*   **`frontend/`**: Contains the presentation layer.
    *   `app.py`: **Entry Point**. Run this to start the server.
    *   `templates/`: HTML files (`index.html` is the main dashboard).
    *   `static/`: CSS, JS, and uploads.
*   **`backend/`**: Contains core logic.
    *   `agri_data.py`: Handles external APIs (Open-Meteo, Sentinel Hub, Nominatim). **Note**: Asset paths here were updated to point to `../assets/` or `../frontend/static/`.
    *   `ai_vision.py`: Handles image processing and AI inference.
*   **`assets/`**: Stores static resources like `scout_demo_map.png`.
*   **`docs/`**: Documentation and reports.
*   **`tests/`**: Unit tests.

## 3. Recent Critical Changes & Decisions

### A. UI/UX Restoration (Agri-Scout)
*   **History**: The map UI went through several iterations.
    1.  *Original*: Broken/Hidden map.
    2.  *Overlay*: Map with floating controls (rejected by user).
    3.  *Split-View (Current)*: **User Preferred**. A dedicated sidebar on the left for controls/results, and the map taking up the full right side.
*   **Implementation**:
    *   `templates/index.html`: Uses a specific `scout-grid` structure.
    *   `static/style.css`: Defines `.scout-grid`, `.scout-sidebar`, and `.scout-map-wrapper`.
    *   **Do Not Revert** to an overlay layout unless explicitly asked.

### B. Bug Fixes
*   **Corrupted HTML**: `index.html` previously had duplicated content and missing `{% endblock %}` tags. It was completely rewritten to be clean and valid.
*   **Import Errors**: `frontend/app.py` now appends the parent directory to `sys.path` to correctly import `backend` modules.
*   **Asset Paths**: `backend/agri_data.py` was hardcoded to look for files in the root. It now uses relative paths to find assets in `assets/` or save to `frontend/static/`.

## 4. Key Files & Logic
*   **`frontend/app.py`**: The Flask app. It configures the `UPLOAD_FOLDER` and `ASSETS_FOLDER`.
*   **`backend/agri_data.py`**:
    *   `get_sentinel_ndvi()`: Fetches live satellite images. If it fails, it falls back to a mock image.
    *   **Mock Data**: The mock image path is set to `../assets/scout_demo_map.png`.
*   **`templates/index.html`**: A monolithic template containing all modules (Dashboard, Scout, Doctor, Weather). Future work could split this into smaller components (e.g., `scout.html`, `doctor.html`).

## 5. Configuration
*   **`.gitignore`**: Configured with strict rules. It **allows** `model.h5` and `assets/` (for hackathon demo purposes) but ignores standard python artifacts.
*   **`README.md`**: Updated with the correct GitHub repository link: `https://github.com/Shrey2104-sys/Open-Agri-OS`.

## 6. Future Action Plan (Best Course of Action)
If you are a new agent picking this up:
1.  **Run the App**: Always run from root with `python frontend/app.py`.
2.  **Maintain Split-View**: Keep the Agri-Scout layout as Sidebar + Map.
3.  **API Keys**: The project uses some hardcoded/demo keys. For production, move all keys to `.env`.
4.  **Modularize Templates**: `index.html` is large (~300 lines). Breaking it into Jinja2 includes (e.g., `{% include 'modules/scout.html' %}`) would be a great next step for maintainability.

---
*This document was auto-generated to ensure context preservation for future development.*
