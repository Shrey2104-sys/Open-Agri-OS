# 🎤 Hackathon Judge Q&A Cheat Sheet

**Project**: Open-Agri OS
**Goal**: Be prepared for every tough question.

---

## 🏗️ Technical Architecture ("The How")

**Q1: Why did you choose Flask (Python) instead of a modern frontend framework like React or Next.js?**
*   **Answer**: "We prioritized **speed of development** and **integration**. Since our core AI and data processing logic (TensorFlow, Geopy, Pandas) is in Python, Flask allows us to keep a unified codebase without the complexity of a separate frontend build pipeline. For a hackathon, this reduces context switching and deployment friction."

**Q2: Your database is SQLite. How does this scale to thousands of users?**
*   **Answer**: "For this MVP and hackathon demo, SQLite is perfect because it's serverless and zero-config. However, we used **SQLAlchemy** as our ORM. This means switching to PostgreSQL for production is literally a one-line configuration change in `app.py`. We built it to be database-agnostic from Day 1."

**Q3: Why a Monolithic architecture? Wouldn't Microservices be better?**
*   **Answer**: "Microservices add network latency and deployment complexity, which is overkill for an MVP. We chose a **Modular Monolith** approach. Our code is organized into distinct modules (`frontend`, `backend`, `ai_engine`), so we can easily extract the AI service into a separate microservice (e.g., using FastAPI) when we need to scale independently."

**Q4: How do you handle offline access for farmers in remote areas?**
*   **Answer**: "Currently, the app requires internet. However, our roadmap includes implementing PWA (Progressive Web App) features. We can cache the static assets and use `localStorage` for recent data. For the AI, we are exploring **TensorFlow.js** to run the plant disease model directly in the browser, removing the need for server connectivity for diagnosis."

---

## 🧠 AI & Machine Learning ("The Brains")

**Q5: What model are you using for disease detection, and why?**
*   **Answer**: "We are using **MobileNetV2**. We chose it because it's lightweight and optimized for mobile/edge devices, which is critical for farmers with low-end smartphones. It gives us a great balance between accuracy (~92% on our validation set) and inference speed."

**Q6: Why use Google Gemini API instead of a custom NLP model?**
*   **Answer**: "Training a custom LLM for agricultural advice requires massive compute and data. **Gemini 1.5 Flash** provides state-of-the-art reasoning capabilities out of the box. We use 'Prompt Engineering' to ground it in agronomy, ensuring it acts as an expert consultant rather than a generic chatbot. It's cost-effective and highly accurate for generating treatment plans."

**Q7: How do you validate the satellite data (NDVI)?**
*   **Answer**: "We use the **Sentinel Hub API** to fetch real-time Sentinel-2 L2A imagery. We calculate NDVI using the standard formula `(NIR - Red) / (NIR + Red)`. In our backend `agri_data.py`, we have an `evalscript` that processes the raw bands. We also have a fallback mechanism to serve simulated data if the satellite pass is cloudy or the API is unreachable."

---

## 💼 Product & Viability ("The Business")

**Q8: Who is your target audience?**
*   **Answer**: "Our primary target is **small-to-medium holder farmers** who lack access to expensive precision agriculture tools. Our secondary audience is agricultural extension workers who can use this tool to advise multiple farmers."

**Q9: How is this different from existing apps like Plantix?**
*   **Answer**: "Most competitors focus *only* on disease detection. Open-Agri OS is an **Operating System** approach. We combine:
    1.  **Macro View**: Satellite intelligence (Agri-Scout).
    2.  **Micro View**: Disease diagnosis (Agri-Doctor).
    3.  **Context**: Hyper-local weather.
    We provide a holistic ecosystem, not just a single utility."

**Q10: What is your business model?**
*   **Answer**: "We operate on a **Freemium** model:
    *   **Free**: Basic disease diagnosis and weather.
    *   **Premium**: Historical satellite analysis, detailed AI treatment plans, and market price alerts.
    *   **B2B**: API access for agri-input companies to integrate our diagnostics."

---

## 🔮 Future Roadmap ("The Vision")

**Q11: What is the next big feature you will build?**
*   **Answer**: "**IoT Integration**. We want to connect directly to soil moisture sensors and automated irrigation systems. This will close the loop—not just *telling* the farmer to water, but *automatically* watering based on our data."

**Q12: How will you handle regional languages?**
*   **Answer**: "Localization is a priority. Since we use Gemini for advice generation, we can easily modify our system prompt to request the output in Hindi, Kannada, or any other regional language, making the app accessible to non-English speakers instantly."

---

## ⚡ "Show Me" Challenges (Be Ready!)

*   **"Show me the AI Code"**: Open `backend/ai_vision.py` -> Show `predict_disease()`.
*   **"Show me the Satellite Logic"**: Open `backend/agri_data.py` -> Show `get_sentinel_ndvi()`.
*   **"Show me the API Routes"**: Open `frontend/app.py` -> Show `@app.route('/api/analyze')`.
*   **"Show me the Frontend Logic"**: Open `frontend/static/script.js` -> Show `fetch()`.
