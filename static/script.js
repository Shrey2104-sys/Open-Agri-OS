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

    // --- Dashboard Chart ---
    const ctx = document.getElementById('marketChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Wheat Price (₹/quintal)',
                    data: [2100, 2150, 2120, 2180, 2200, 2250, 2230],
                    borderColor: '#28A745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
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

    // --- Agri-Scout (Map) ---
    let map;
    if (document.getElementById('map')) {
        map = L.map('map').setView([12.97, 77.59], 10); // Default Bangalore
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }

    const scoutBtn = document.getElementById('scout-btn');
    if (scoutBtn) {

        scoutBtn.addEventListener('click', async () => {
            const placeName = document.getElementById('place-input').value;
            if (!placeName) return showToast("Please enter a location", "error");

            scoutBtn.textContent = "Analyzing...";

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
                    // Update Map
                    const [lat, lon] = data.coords;
                    map.setView([lat, lon], 12);
                    L.marker([lat, lon]).addTo(map)
                        .bindPopup(`<b>${placeName}</b><br>Season: ${data.recommendation.season}`)
                        .openPopup();

                    // Add Heatmap Circle
                    L.circle([lat, lon], {
                        color: '#28A745',
                        fillColor: '#28A745',
                        fillOpacity: 0.4,
                        radius: 3000
                    }).addTo(map);

                    // Show Results
                    document.getElementById('scout-results').classList.remove('hidden');
                    document.getElementById('crop-advice-content').innerHTML = `
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
            dropZone.style.borderColor = '#28A745';
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
            const reader = new FileReader();
            reader.onload = (e) => {
                dropZone.innerHTML = `<img src="${e.target.result}" style="max-height: 200px; border-radius: 10px;">`;
            };
            reader.readAsDataURL(file);

        } catch (e) {
            console.error(e);
            showToast("Error analyzing image", "error");
            dropZone.innerHTML = `<p style="color:red">Error. Try again.</p>`;
        }
    }

    async function getTreatment(disease) {
        const btn = document.getElementById('treatment-btn');
        btn.textContent = "Consulting AI Agronomist...";

        try {
            const response = await fetch('/api/get_advice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ disease: disease, ndvi: "Critical" })
            });
            const data = await response.json();

            document.getElementById('treatment-plan').classList.remove('hidden');
            // Convert simple markdown to HTML (basic)
            const htmlAdvice = data.advice.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
            document.getElementById('treatment-content').innerHTML = htmlAdvice;

        } catch (e) {
            console.error(e);
            showToast("Error fetching treatment", "error");
        } finally {
            btn.textContent = "💊 Generate AI Treatment Plan";
        }
    }

});
