document.addEventListener('DOMContentLoaded', () => {

    // --- Navigation ---
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.module-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(sec => sec.classList.remove('active'));
            item.classList.add('active');
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');

            if (targetId === 'scout' && AgriMap.map) {
                setTimeout(() => AgriMap.map.invalidateSize(), 100);
            }
        });
    });

    // --- Toast Helper ---
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span class="icon">${type === 'success' ? '✅' : '⚠️'}</span><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // --- AI Overlay Helper ---
    function showAIOverlay(title, detail, callback) {
        console.log(`[AI Action] ${title}: ${detail}`);
        return callback();
    }

    // --- Agri-Scout Module (Map & Search) ---
    const AgriMap = {
        map: null,
        baseLayer: null,
        ndviLayerGroup: null,
        currentMode: 'map', // 'map' or 'ndvi'
        init: function () {
            if (!document.getElementById('map')) return;

            // Default: Davanagere
            this.map = L.map('map', { zoomControl: false }).setView([14.4644, 75.9218], 13);

            // Esri World Imagery (Base)
            this.baseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri, Maxar, Earthstar Geographics',
                maxZoom: 19
            }).addTo(this.map);

            this.ndviLayerGroup = L.layerGroup().addTo(this.map);
            L.control.zoom({ position: 'bottomright' }).addTo(this.map);

            // Add Overlay Card
            this.addOverlayCard();
            this.setupToggle();
        },
        setupToggle: function () {
            const mapBtn = document.getElementById('view-map-btn');
            const ndviBtn = document.getElementById('view-ndvi-btn');

            if (!mapBtn || !ndviBtn) return;

            mapBtn.addEventListener('click', () => {
                this.currentMode = 'map';
                mapBtn.classList.add('active');
                ndviBtn.classList.remove('active');
                this.baseLayer.setOpacity(1.0);
                this.ndviLayerGroup.clearLayers();
            });

            ndviBtn.addEventListener('click', () => {
                this.currentMode = 'ndvi';
                ndviBtn.classList.add('active');
                mapBtn.classList.remove('active');
                this.baseLayer.setOpacity(0.5); // Dim base layer
                // Trigger NDVI fetch for current view
                const center = this.map.getCenter();
                triggerAnalysis("Current View", center.lat, center.lng);
            });
        },
        flyTo: function (lat, lon, zoom = 14) {
            this.map.flyTo([lat, lon], zoom, { duration: 2 });
            this.updateOverlayCard(lat, lon);
        },
        addMarker: function (lat, lon, text) {
            L.marker([lat, lon]).addTo(this.map).bindPopup(text).openPopup();
        },
        addNDVILayer: function (url, bounds) {
            this.ndviLayerGroup.clearLayers();
            // Use map bounds if in NDVI mode to cover view
            const overlayBounds = this.currentMode === 'ndvi' ? this.map.getBounds() : bounds;
            L.imageOverlay(url, overlayBounds, { opacity: 0.7, interactive: true }).addTo(this.ndviLayerGroup);
            showToast("NDVI Heatmap Loaded", "success");
        },
        addOverlayCard: function () {
            const card = document.createElement('div');
            card.className = 'map-overlay-card';
            card.id = 'map-overlay';
            card.innerHTML = `
                <h4>🌱 Agronomist Insight</h4>
                <p><strong>Region:</strong> Davanagere</p>
                <p><strong>Soil:</strong> Loamy / Alluvial</p>
                <p><strong>Season:</strong> Rabi (Winter)</p>
                <p><strong>Best Crop:</strong> Wheat, Mustard</p>
            `;
            document.querySelector('.map-container').appendChild(card);
        },
        updateOverlayCard: function (lat, lon) {
            const card = document.getElementById('map-overlay');
            if (card) {
                card.innerHTML = `
                    <h4>🌱 Agronomist Insight</h4>
                    <p><strong>Coords:</strong> ${lat.toFixed(3)}, ${lon.toFixed(3)}</p>
                    <p><strong>Soil:</strong> Clay Loam (Detected)</p>
                    <p><strong>Season:</strong> Rabi (Optimal)</p>
                    <p><strong>Best Crop:</strong> Wheat, Chickpea</p>
                `;
            }
        }
    };

    // Initialize Map
    try {
        AgriMap.init();
    } catch (e) {
        console.error("Map initialization failed:", e);
        showToast("Map failed to load", "error");
    }

    // --- Weather Integration ---
    async function fetchWeather(lat, lon, placeName) {
        try {
            const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`);
            const data = await response.json();
            const weather = data.current_weather;

            // Update Weather Module
            document.getElementById('w-temp').textContent = `${weather.temperature}°C`;
            document.getElementById('w-wind').textContent = `${weather.windspeed} km/h`;

            // Update Dashboard Weather Card
            const dashTemp = document.getElementById('weather-temp');
            const dashLoc = document.getElementById('weather-location');
            if (dashTemp) dashTemp.textContent = `${weather.temperature}°C`;
            if (dashLoc) dashLoc.textContent = placeName || "Selected Region";

        } catch (error) {
            console.error("Weather Fetch Error:", error);
            // Silent fail for weather to not disrupt flow
        }
    }

    // ... (Live Search Logic remains same) ...

    // --- Analysis Trigger ---
    const scoutBtn = document.getElementById('scout-btn');
    const locateBtn = document.getElementById('locate-btn');
    const placeInput = document.getElementById('place-input');

    async function triggerAnalysis(placeName, lat = null, lon = null) {
        // Allow analysis without placeName if we have coords (e.g. from NDVI toggle)
        if (!placeName && (!lat || !lon)) return showToast("Please enter a location", "error");

        const originalText = scoutBtn.textContent;
        scoutBtn.textContent = "Analyzing...";
        scoutBtn.disabled = true;
        if (locateBtn) locateBtn.disabled = true;

        showAIOverlay("Initializing Satellite Link...", "Analyzing Sentinel-2 Multispectral Data...", async () => {
            try {
                // Fly to location immediately if coords are known
                if (lat && lon) {
                    AgriMap.flyTo(lat, lon);
                    if (placeName !== "Current View") AgriMap.addMarker(lat, lon, placeName);
                    // Fetch Weather
                    fetchWeather(lat, lon, placeName);
                }

                const payload = { place_name: placeName || "Custom Location" };
                if (lat && lon) {
                    payload.lat = lat;
                    payload.lon = lon;
                }

                const response = await fetch('/api/scout_info', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();

                if (data.error) {
                    showToast(data.error, "error");
                } else {
                    const [resLat, resLon] = data.coords;

                    // If we didn't have coords before, fly now
                    if (!lat || !lon) {
                        AgriMap.flyTo(resLat, resLon);
                        AgriMap.addMarker(resLat, resLon, placeName);
                        fetchWeather(resLat, resLon, placeName);
                    }

                    // Update NDVI
                    if (data.ndvi && data.ndvi.image_path) {
                        AgriMap.addNDVILayer(data.ndvi.image_path, data.ndvi.bbox);
                    }

                    // Update Advice UI
                    const resultsDiv = document.getElementById('scout-results');
                    const contentDiv = document.getElementById('crop-advice-content');
                    resultsDiv.classList.remove('hidden');

                    contentDiv.innerHTML = `
                        <div class="advice-card">
                            <h4>Recommended Crop: ${data.recommendation.crop}</h4>
                            <p><strong>Season:</strong> ${data.recommendation.season}</p>
                            <p><strong>Soil Type:</strong> ${data.recommendation.soil}</p>
                            <p><strong>Water:</strong> ${data.recommendation.water}</p>
                            <p class="reason">"${data.recommendation.reason}"</p>
                        </div>
                    `;
                    showToast("Analysis Complete", "success");
                }
            } catch (error) {
                console.error(error);
                showToast("Connection Error", "error");
            } finally {
                scoutBtn.textContent = originalText;
                scoutBtn.disabled = false;
                if (locateBtn) locateBtn.disabled = false;
            }
        });
    }

    if (scoutBtn) {
        scoutBtn.addEventListener('click', () => triggerAnalysis(placeInput.value));
    }

    if (locateBtn) {
        locateBtn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                return showToast("Geolocation not supported", "error");
            }

            locateBtn.innerHTML = "⏳";

            const geoOptions = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };

            navigator.geolocation.getCurrentPosition(async (pos) => {
                const { latitude: lat, longitude: lon } = pos.coords;
                try {
                    // Reverse Geocode
                    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                    const data = await res.json();
                    const city = data.address.city || data.address.town || data.address.village || "My Location";
                    placeInput.value = `📍 ${city}`;
                    triggerAnalysis(city, lat, lon);
                } catch (e) {
                    console.error("Reverse geocode failed", e);
                    triggerAnalysis("My Location", lat, lon);
                } finally {
                    locateBtn.innerHTML = "📍";
                }
            }, (err) => {
                console.warn(`ERROR(${err.code}): ${err.message}`);
                showToast("Location access denied or failed. Using default.", "warning");
                locateBtn.innerHTML = "📍";
            }, geoOptions);
        });
    }

    // --- Agri-Doctor (Upload) ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    if (dropZone) {
        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) handleFileUpload(e.target.files[0]);
        });
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#10b981';
        });
        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#ccc';
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#ccc';
            if (e.dataTransfer.files.length > 0) handleFileUpload(e.dataTransfer.files[0]);
        });
    }

    async function handleFileUpload(file) {
        dropZone.innerHTML = `<div class="spinner"></div><p>Scanning cellular structure...</p>`;
        dropZone.classList.add('scanning');

        showAIOverlay("Analyzing Cellular Structure...", "Running Convolutional Neural Network...", async () => {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/predict_disease', { method: 'POST', body: formData });
                const data = await response.json();

                document.getElementById('diagnosis-result').classList.remove('hidden');
                const confPercent = Math.round(data.confidence * 100);
                document.getElementById('confidence-bar').style.width = `${confPercent}%`;
                document.getElementById('confidence-text').textContent = `${confPercent}%`;

                const statusBox = document.getElementById('disease-status');
                if (data.detected_disease === "Healthy") {
                    statusBox.className = "status-box status-healthy";
                    statusBox.innerHTML = `<h2>✅ Healthy</h2><p>No pathogens detected.</p>`;
                    document.getElementById('treatment-btn').classList.add('hidden');
                } else {
                    statusBox.className = "status-box status-disease";
                    statusBox.innerHTML = `<h2>⚠️ ${data.detected_disease}</h2><p>Pathogen Detected</p>`;
                    const treatBtn = document.getElementById('treatment-btn');
                    treatBtn.classList.remove('hidden');
                    treatBtn.onclick = () => getTreatment(data.detected_disease);
                }

                dropZone.classList.remove('scanning');
                const reader = new FileReader();
                reader.onload = (e) => {
                    dropZone.innerHTML = `<img src="${e.target.result}" style="max-height: 200px; border-radius: 10px;">`;
                };
                reader.readAsDataURL(file);

            } catch (e) {
                console.error(e);
                showToast("Error analyzing image", "error");
                dropZone.classList.remove('scanning');
                dropZone.innerHTML = `<p style="color:red">Error. Try again.</p>`;
            }
        });
    }

    async function getTreatment(disease) {
        showAIOverlay("Consulting AI Agronomist...", "Generating Organic Treatment Plan...", async () => {
            try {
                const response = await fetch('/api/get_advice', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ disease: disease, ndvi: "Critical" })
                });
                const data = await response.json();

                document.getElementById('treatment-modal').classList.remove('hidden');
                const htmlAdvice = data.advice.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
                document.getElementById('treatment-plan-content').innerHTML = htmlAdvice;

                document.querySelector('.close-modal').onclick = () => {
                    document.getElementById('treatment-modal').classList.add('hidden');
                };
            } catch (e) {
                console.error(e);
                showToast("Error fetching treatment", "error");
            }
        });
    }

    // --- Dashboard Charts (Keep existing) ---
    const ctx = document.getElementById('marketChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Wheat Price (₹/quintal)',
                    data: [2100, 2150, 2120, 2180, 2200, 2250, 2280],
                    borderColor: '#1b4332',
                    backgroundColor: 'rgba(27, 67, 50, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } } }
        });
    }

    const yieldCtx = document.getElementById('yieldChart');
    if (yieldCtx) {
        new Chart(yieldCtx, {
            type: 'bar',
            data: {
                labels: ['2020', '2021', '2022', '2023', '2024'],
                datasets: [{
                    label: 'Yield (Quintals/Acre)',
                    data: [18, 20, 19, 22, 24],
                    backgroundColor: '#40916c',
                    borderRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } } }
        });
    }
});
