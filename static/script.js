document.addEventListener('DOMContentLoaded', () => {

    // --- Navigation ---
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.module-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // Remove active class
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(sec => sec.classList.remove('active'));

            // Add active class
            item.classList.add('active');
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');

            // Resize map if scout is active (Leaflet quirk)
            if (targetId === 'scout' && map) {
                setTimeout(() => map.invalidateSize(), 100);
            }
        });
    });

    // --- Toast Notifications ---
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="icon">${type === 'success' ? '✅' : '⚠️'}</span>
            <span>${message}</span>
        `;
        container.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // --- AI Overlay Helper ---
    let safetyTimer = null; // Global timer reference

    // Global Close Handler
    const overlay = document.getElementById('ai-overlay');
    const closeBtn = document.getElementById('force-close-ai');

    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation(); // Stop bubbling
            console.log("Force closing AI overlay");
            overlay.classList.add('hidden');
            if (safetyTimer) clearTimeout(safetyTimer);
        });
    }

    function showAIOverlay(title, detail, callback) {
        // Overlay Disabled by User Request (Restoring "Yesterday's" behavior)
        // We simply run the callback immediately without showing the UI.
        console.log(`[AI Action] ${title}: ${detail}`);
        return callback();
    }

    // --- Dashboard Chart ---
    const ctx = document.getElementById('marketChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Wheat Price (₹/quintal)',
                    data: [2100, 2150, 2120, 2180, 2200, 2250, 2280], // Slight upward trend
                    borderColor: '#0ea5e9', // Blue/Teal
                    backgroundColor: 'rgba(14, 165, 233, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }

    // --- Yield History Chart ---
    const yieldCtx = document.getElementById('yieldChart');
    if (yieldCtx) {
        new Chart(yieldCtx, {
            type: 'bar',
            data: {
                labels: ['2020', '2021', '2022', '2023', '2024'],
                datasets: [{
                    label: 'Wheat Yield (Quintals/Acre)',
                    data: [18, 20, 19, 22, 24],
                    backgroundColor: '#10b981', // Green
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }

    // --- Agri-Scout (Map) ---
    let map;
    let scoutLayerGroup; // Group to hold markers and heatmaps

    if (document.getElementById('map')) {
        // Davanagere Coordinates
        const davanagere = [14.4644, 75.9218];

        map = L.map('map', {
            center: davanagere,
            zoom: 13
        });

        // Esri World Imagery (Satellite)
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri, Maxar, Earthstar Geographics'
        }).addTo(map);

        // Initialize LayerGroup
        scoutLayerGroup = L.layerGroup().addTo(map);
    }

    const scoutBtn = document.getElementById('scout-btn');
    if (scoutBtn) {

        scoutBtn.addEventListener('click', async () => {
            const placeName = document.getElementById('place-input').value;
            if (!placeName) return showToast("Please enter a location", "error");

            scoutBtn.textContent = "Analyzing...";

            showAIOverlay("Initializing Satellite Link...", "Analyzing Sentinel-2 Multispectral Data...", async () => {
                try {
                    const response = await fetch('/api/scout_info', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ place_name: placeName })
                    });
                    const data = await response.json();

                    if (data.error) {
                        showToast(data.error, "error");
                    } else {
                        // Update Map View
                        const [lat, lon] = data.coords;
                        map.setView([lat, lon], 13);

                        // Clear previous results safely
                        scoutLayerGroup.clearLayers();

                        // Add Marker
                        const marker = L.marker([lat, lon])
                            .bindPopup(`<b>${placeName}</b><br>NDVI Analysis Complete<br>Season: ${data.recommendation.season}`)
                            .addTo(scoutLayerGroup);

                        setTimeout(() => marker.openPopup(), 500);

                        // Check for Davanagere (Real Image Overlay)
                        if (placeName.toLowerCase().includes('davanagere') || placeName.toLowerCase().includes('davangere')) {
                            const imageUrl = '/static/ndvi_demo.jpg';
                            const imageBounds = [[lat - 0.02, lon - 0.02], [lat + 0.02, lon + 0.02]];
                            L.imageOverlay(imageUrl, imageBounds).addTo(scoutLayerGroup);
                        } else {
                            // Generate Static NDVI Heatmap Data for others
                            const heatData = getStaticNDVIData(placeName, lat, lon);

                            // Add Heatmap to Group
                            L.heatLayer(heatData, {
                                radius: 30,
                                blur: 20,
                                maxZoom: 17,
                                gradient: { 0.2: 'red', 0.4: 'yellow', 0.6: 'lime', 1.0: 'green' }
                            }).addTo(scoutLayerGroup);
                        }

                        // Show Results Panel
                        document.getElementById('scout-results').classList.remove('hidden');
                        document.getElementById('crop-advice-content').innerHTML = `
                            <div style="margin-bottom: 15px; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <strong>NDVI Legend:</strong><br>
                                <span style="color: green">■</span> High Vigor
                                <span style="color: lime">■</span> Healthy
                                <span style="color: yellow">■</span> Moderate
                                <span style="color: red">■</span> Stressed/Low
                            </div>
                            <p><b>Season:</b> ${data.recommendation.season}</p>
                            <p><b>Soil:</b> ${data.recommendation.soil}</p>
                            <p><b>Recommended Crops:</b> ${data.recommendation.crops.join(', ')}</p>
                        `;
                    }
                } catch (e) {
                    console.error(e);
                    showToast("Error fetching scout data", "error");
                } finally {
                    scoutBtn.textContent = "Analyze";
                }
            });
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
        // Show scanning state
        dropZone.innerHTML = `<div class="spinner"></div><p>Scanning cellular structure...</p>`;
        dropZone.classList.add('scanning');

        showAIOverlay("Analyzing Cellular Structure...", "Running Convolutional Neural Network...", async () => {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/predict_disease', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                // Show Result
                document.getElementById('diagnosis-result').classList.remove('hidden');

                // Update Confidence
                const confPercent = Math.round(data.confidence * 100);
                document.getElementById('confidence-bar').style.width = `${confPercent}%`;
                document.getElementById('confidence-text').textContent = `${confPercent}%`;

                // Update Status
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

                // Reset Upload Zone (preview)
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
                // Convert simple markdown to HTML (basic)
                const htmlAdvice = data.advice.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
                document.getElementById('treatment-plan-content').innerHTML = htmlAdvice;

                // Close modal logic
                document.querySelector('.close-modal').onclick = () => {
                    document.getElementById('treatment-modal').classList.add('hidden');
                };

            } catch (e) {
                console.error(e);
                showToast("Error fetching treatment", "error");
            }
        });
    }

    // Helper: Generate Static NDVI Patterns
    function getStaticNDVIData(placeName, lat, lon) {
        const data = [];
        const name = placeName.toLowerCase();

        if (name.includes('davanagere') || name.includes('davangere')) {
            // Pattern: Dense, Healthy Fields (Rectangular Blocks)
            for (let i = 0; i < 600; i++) {
                // Block 1: Main Irrigated Area (Green)
                let latOffset = (Math.random() - 0.5) * 0.03;
                let lonOffset = (Math.random() - 0.5) * 0.03;
                data.push([lat + latOffset, lon + lonOffset, 0.9 + Math.random() * 0.1]);

                // Block 2: Outskirts (Mixed)
                if (i % 2 === 0) {
                    latOffset = (Math.random() - 0.5) * 0.06;
                    lonOffset = (Math.random() - 0.5) * 0.06;
                    data.push([lat + latOffset, lon + lonOffset, 0.5 + Math.random() * 0.3]);
                }
            }
        } else if (name.includes('mangalore') || name.includes('mangaluru')) {
            // Pattern: Coastal Strip (Linear)
            for (let i = 0; i < 500; i++) {
                // Linear strip along the coast (North-South roughly)
                let latOffset = (Math.random() - 0.5) * 0.08;
                let lonOffset = (Math.random() - 0.5) * 0.01 - 0.02; // Shifted slightly West
                data.push([lat + latOffset, lon + lonOffset, 0.7 + Math.random() * 0.3]);
            }
        } else if (name.includes('coorg') || name.includes('madikeri') || name.includes('kodagu')) {
            // Pattern: Scattered Hill Patches
            for (let i = 0; i < 500; i++) {
                // Create 3 distinct clusters
                const cluster = i % 3;
                let latOff, lonOff;

                if (cluster === 0) { latOff = 0.02; lonOff = 0.02; }
                else if (cluster === 1) { latOff = -0.02; lonOff = -0.01; }
                else { latOff = 0.01; lonOff = -0.03; }

                let rLat = (Math.random() - 0.5) * 0.015;
                let rLon = (Math.random() - 0.5) * 0.015;

                data.push([lat + latOff + rLat, lon + lonOff + rLon, 0.6 + Math.random() * 0.4]);
            }
        } else {
            // Fallback: Random Cloud for other locations
            for (let i = 0; i < 300; i++) {
                const latOffset = (Math.random() - 0.5) * 0.04;
                const lonOffset = (Math.random() - 0.5) * 0.04;
                let intensity = Math.random();
                if (Math.random() > 0.8) intensity = 0.2;
                data.push([lat + latOffset, lon + lonOffset, intensity]);
            }
        }
        return data;
    }

});
