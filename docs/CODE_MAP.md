# 🗺️ Codebase Map: Where is Everything?

Use this cheat sheet when a judge asks "Show me the code for..."

## 🟢 Frontend (The UI)
| File | What it does |
| :--- | :--- |
| **`frontend/app.py`** | **The Brain**. Starts the web server, defines all URL routes (like `/api/analyze`), and connects the frontend to the backend. |
| **`frontend/templates/index.html`** | **The Skeleton**. The main HTML file containing the Dashboard, Agri-Scout (Map), and Agri-Doctor layouts. |
| **`frontend/static/style.css`** | **The Look**. Contains all the styling, including the Glassmorphism effects, colors, and the Split-View map layout. |
| **`frontend/static/script.js`** | **The Muscle**. Handles button clicks, sends images to the backend (fetch API), and updates the UI without reloading. |

## 🔵 Backend (The Logic)
| File | What it does |
| :--- | :--- |
| **`backend/agri_data.py`** | **The Data Hub**. Connects to **Sentinel Hub** (Satellite), **Open-Meteo** (Weather), and **Gemini** (AI Advice). Contains the logic to fetch and process external data. |
| **`backend/ai_vision.py`** | **The Eye**. Loads the **MobileNetV2** model (`model.h5`) and predicts plant diseases from uploaded images. |

## 🟡 Assets & Config
| File | What it does |
| :--- | :--- |
| **`model.h5`** | **The AI Brain**. The pre-trained Deep Learning model file. |
| **`assets/`** | **Images**. Stores the demo satellite map (`scout_demo_map.png`) used when the live API is offline. |
| **`users.db`** | **The Memory**. SQLite database storing user accounts (created automatically). |

---

### ⚡ Quick Scenarios
*   **"Show me the Routes"** -> Open `frontend/app.py`
*   **"Show me the AI Model"** -> Open `backend/ai_vision.py`
*   **"Show me the Satellite API"** -> Open `backend/agri_data.py`
*   **"Show me the Fetch Logic"** -> Open `frontend/static/script.js`
