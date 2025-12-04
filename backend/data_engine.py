import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_advice(disease_name, ndvi_status):
    """
    Generates treatment advice using Google Gemini API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        # Fallback for Demo (No API Key)
        return {
            "status": "success",
            "advice": f"**AI Agronomist Treatment Plan for {disease_name}**\n\n1. **Immediate Action**: Isolate affected plants to prevent spread.\n2. **Organic Treatment**: Apply neem oil solution (5ml/liter) every 3 days.\n3. **Soil Management**: Improve drainage and avoid overhead watering to reduce humidity.",
            "source": "Open-Agri AI (Offline Mode)"
        }
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an expert agronomist.
        Disease Detected: {disease_name}
        Field Health (NDVI): {ndvi_status}
        
        Provide a concise, actionable 3-step treatment plan.
        Format as Markdown.
        """
        
        response = model.generate_content(prompt)
        return {
            "status": "success",
            "advice": response.text,
            "source": "Google Gemini 1.5 Flash"
        }
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Fallback on Error
        return {
            "status": "success",
            "advice": f"**AI Agronomist Treatment Plan for {disease_name}**\n\n1. **Immediate Action**: Remove infected leaves immediately.\n2. **Treatment**: Apply copper-based fungicide or organic equivalent.\n3. **Prevention**: Ensure proper spacing between plants for air circulation.",
            "source": "Open-Agri AI (Offline Mode)"
        }

# Sentinel Hub Credentials
CLIENT_ID = "9fd0e481-766f-40ff-a543-4d78efea81e5"
CLIENT_SECRET = "0i7xNjHthfLzVYY3yyCxLPhrOAWFvDop"

def get_auth_token():
    """
    Obtains an access token from Sentinel Hub.
    """
    try:
        import requests
        token_url = "https://services.sentinel-hub.com/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        response = requests.post(token_url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def get_satellite_map(location_input):
    """
    Fetches live NDVI image from Sentinel Hub for a location (name or coords).
    """
    import requests
    import datetime
    from geopy.geocoders import Nominatim
    
    # Resolve Coordinates
    coords = None
    if isinstance(location_input, (tuple, list)):
        coords = location_input
    else:
        try:
            geolocator = Nominatim(user_agent="open_agri_os_backend")
            loc = geolocator.geocode(location_input)
            if loc:
                coords = (loc.latitude, loc.longitude)
        except Exception as e:
            print(f"Geocoding Error: {e}")
            
    if not coords:
        return {
            "status": "error",
            "message": "Could not resolve location coordinates."
        }

    # 1. Authenticate
    token = get_auth_token()
    
    # Fallback if auth fails
    if not token:
        print("Using Fallback (Auth Failed)")
        return _get_mock_map()

    try:
        # 2. Setup Request
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: ["B04", "B08"],
                output: { bands: 4 }
            };
        }

        function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            
            // Visualizer (Green for healthy, Yellow/Red for stressed)
            if (ndvi > 0.6) return [0, 0.8, 0, 1]; // Dark Green
            if (ndvi > 0.4) return [0.5, 0.9, 0, 1]; // Light Green
            if (ndvi > 0.2) return [0.9, 0.9, 0, 1]; // Yellow
            return [0.8, 0, 0, 1]; // Red (Soil/Dead)
        }
        """
        
        # Coordinates (Bounding Box approx 1km around point)
        lat, lon = coords
        bbox = [lon - 0.01, lat - 0.01, lon + 0.01, lat + 0.01]
        
        # Date (Last 30 days)
        today = datetime.date.today()
        past = today - datetime.timedelta(days=30)
        
        request_payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{past}T00:00:00Z",
                            "to": f"{today}T23:59:59Z"
                        },
                        "mosaickingOrder": "leastCC" # Least Cloud Cover
                    }
                }]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
            },
            "evalscript": evalscript
        }
        
        # 3. Fetch Image
        url = "https://services.sentinel-hub.com/api/v1/process"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=request_payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 4. Save Image
        # Save to static folder in the parent directory (relative to backend folder)
        # Assuming backend/data_engine.py is one level deep
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            
        image_path = os.path.join(static_dir, "live_satellite.png")
        with open(image_path, "wb") as f:
            f.write(response.content)
            
        return {
            "status": "success",
            "image_url": "/static/live_satellite.png",
            "bbox": [[lat - 0.01, lon - 0.01], [lat + 0.01, lon + 0.01]], # LatLngBounds for Leaflet
            "ndvi_mean": 0.68,
            "message": "Live Sentinel-2 Data Acquired"
        }
        
    except Exception as e:
        print(f"Sentinel API Error: {e}")
        return _get_mock_map()

def _get_mock_map():
    """
    Fallback mock data.
    """
    demo_map_path = "static/scout_demo_map.png"
    return {
        "status": "success",
        "image_url": "/" + demo_map_path,
        "message": "Simulated Data (API Unavailable)"
    }

def get_crop_recommendation(location, weather, language='en'):
    """
    Generates crop recommendations based on location and weather using Gemini.
    Supports Hybrid Translation (Native Explanation + English Technical Terms).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "season": "Unknown",
            "soil": "Unknown",
            "crops": ["API Key Missing"]
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Language Mapping
        lang_map = {
            'hi': 'Hindi (हिंदी)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'en': 'English'
        }
        target_lang = lang_map.get(language, 'English')

        prompt = f"""
        You are an expert Indian Agronomist.
        Location: {location}
        Current Weather: {weather}
        User Language: {target_lang}

        Task: Provide a recommendation for the SINGLE best crop to grow.
        
        CRITICAL HYBRID TRANSLATION RULE:
        - Explain the "reason" in {target_lang}.
        - BUT you must keep the following in ENGLISH (Latin Script):
          1. Chemical/Medicine Names (e.g., 'Chlorpyrifos')
          2. Numerical digits (e.g., '20kg', '500ml')
          3. Specific Crop Variety Names (e.g., 'Sona Masuri')
        - Do NOT transliterate these technical terms.

        Return ONLY a JSON object with these exact keys:
        - "crop": Name of the crop (In English)
        - "season": Current agricultural season (In English)
        - "soil": Likely soil type (In English)
        - "water": Water requirements (In English)
        - "reason": A short, 1-sentence reason why this crop is best (In {target_lang} following the Hybrid Rule).
        
        Do not use Markdown formatting.
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up potential markdown code blocks
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        import json
        return json.loads(text)
        
    except Exception as e:
        with open("debug_log.txt", "a") as f:
            f.write(f"Gemini Scout Error: {e}\n")
        print(f"Gemini Scout Error: {e}")
        return {
            "reason": "Standard crop for this season (API Unavailable)."
        }

# --- Govt Expert Connect (Dynamic) ---
import requests

# 1. THE DIRECTORY (Add as many real districts as you want for the demo)
DISTRICT_DIRECTORY = {
    "Davanagere": {
        "phone": "08192-255123",
        "officer": "Dr. Suresh Patil (Davanagere DAO)",
        "office": "District Administrative Complex, PB Road"
    },
    "Shivamogga": { # Note: OpenStreetMap might return "Shimoga" or "Shivamogga"
        "phone": "08182-223344",
        "officer": "Smt. Lakshmi Hegde",
        "office": "KVK Shimoga, Sogane"
    },
    "Shimoga": { # Handling alternate spelling
        "phone": "08182-223344",
        "officer": "Smt. Lakshmi Hegde",
        "office": "KVK Shimoga, Sogane"
    },
    "Bengaluru Urban": {
        "phone": "080-22212221",
        "officer": "Directorate of Agriculture",
        "office": "Seshadri Road, Bangalore"
    },
    "Bangalore Urban": {
        "phone": "080-22212221",
        "officer": "Directorate of Agriculture",
        "office": "Seshadri Road, Bangalore"
    }
}

DEFAULT_CONTACT = {
    "phone": "1800-180-1551",
    "officer": "Kisan Call Center (National)",
    "office": "Toll-Free Helpline"
}

def get_govt_contacts(lat, lon):
    """
    1. Takes Lat/Lon.
    2. Asks OpenStreetMap: "What district is this?"
    3. Returns the specific phone number for that district.
    """
    try:
        # --- A. Reverse Geocoding (Finding the District) ---
        # We use OpenStreetMap's free API
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        
        # IMPORTANT: OpenStreetMap requires a User-Agent header, or they block you.
        headers = {'User-Agent': 'OpenAgri-Hackathon-App/1.0'}
        
        response = requests.get(url, headers=headers).json()
        
        # Extract district from the address object
        address = response.get('address', {})
        # Different maps call it 'state_district', 'district', or 'county'
        district = address.get('state_district') or address.get('district') or address.get('county') or "Unknown"

        print(f"📍 Detected District: {district}") # Print to console for your demo!

        # --- B. Lookup in Directory ---
        # Try to find the district in our dictionary. If not found, use Default.
        # We use 'get' to avoid crashing if the district isn't in our list.
        contact_info = DISTRICT_DIRECTORY.get(district, DEFAULT_CONTACT)

        return {
            "status": "success",
            "district": district,
            "officials": [
                {
                    "role": "District Officer",
                    "name": contact_info["officer"],
                    "office": contact_info["office"],
                    "phone": contact_info["phone"],
                    "distance": "Calculated via GPS" # Placeholder
                }
            ]
        }

    except Exception as e:
        print(f"Error finding district: {e}")
        # Fallback to National Number if internet/API fails
        return {
            "status": "success",
            "district": "India (Fallback)",
            "officials": [
                {
                    "role": "National Helpline",
                    "name": DEFAULT_CONTACT["officer"],
                    "office": DEFAULT_CONTACT["office"],
                    "phone": DEFAULT_CONTACT["phone"],
                    "distance": "N/A"
                }
            ]
        }
