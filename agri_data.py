import os
import time
import random
import google.generativeai as genai
from geopy.geocoders import Nominatim

def get_coordinates(place_name):
    """
    Geocodes a place name to (lat, lon).
    """
    try:
        geolocator = Nominatim(user_agent="open_agri_os_v3")
        location = geolocator.geocode(place_name)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None

def get_weather(lat, lon):
    """
    Simulates fetching weather data for a location.
    """
    # Mock data - in production, use OpenWeatherMap API
    conditions = ["Sunny", "Partly Cloudy", "Overcast", "Light Rain"]
    return {
        "temp": round(random.uniform(20, 35), 1),
        "humidity": random.randint(40, 80),
        "wind_speed": round(random.uniform(5, 15), 1),
        "condition": random.choice(conditions),
        "forecast": "Good conditions for spraying." if random.random() > 0.5 else "Avoid spraying today."
    }

def get_crop_recommendation(lat, lon):
    """
    Provides crop recommendations based on location and simulated season.
    """
    # Simple rule-based logic
    if lat > 20: # North India
        return {
            "season": "Rabi (Winter)",
            "crops": ["Wheat", "Mustard", "Barley", "Peas"],
            "soil": "Alluvial Soil",
            "sowing_window": "Oct - Dec"
        }
    elif 10 < lat <= 20: # Central/South India
        return {
            "season": "Kharif (Monsoon)",
            "crops": ["Rice", "Cotton", "Maize", "Soybean"],
            "soil": "Black Cotton Soil",
            "sowing_window": "June - July"
        }
    else: # Tropics
        return {
            "season": "All Year",
            "crops": ["Coconut", "Arecanut", "Spices", "Rubber"],
            "soil": "Laterite Soil",
            "sowing_window": "Year-round"
        }

def get_sentinel_ndvi(coords):
    """
    Simulates Sentinel Hub API.
    """
    time.sleep(1.0) 
    possible_paths = ["scout_demo_map.jpg", "scout_demo_map.png"]
    image_path = None
    for path in possible_paths:
        if os.path.exists(path):
            image_path = path
            break
    
    if image_path:
        return {
            "status": "success",
            "image_path": image_path,
            "ndvi_mean": 0.72,
            "message": "Satellite data acquired."
        }
    else:
        return {
            "status": "error",
            "message": "No satellite data found."
        }

def get_gemini_advice(disease_name, ndvi_status):
    """
    Generates treatment plan using Gemini.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return {
            "status": "warning",
            "advice": "⚠️ API Key missing. Mock Advice: Ensure proper drainage and apply fungicide.",
            "source": "System Mock (Missing Key)"
        }
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as an expert agronomist.
        Disease Detected: {disease_name}
        Field Health: {ndvi_status}
        
        Provide a structured treatment plan in Markdown:
        1. **Immediate Action**: What to do right now.
        2. **Chemical Control**: Specific fungicides/pesticides (if needed).
        3. **Organic Alternative**: Non-chemical options.
        4. **Prevention**: How to stop it next season.
        
        Keep it concise and actionable for a farmer.
        """
        
        response = model.generate_content(prompt)
        return {
            "status": "success",
            "advice": response.text,
            "source": "Google Gemini 1.5 Flash"
        }
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {
            "status": "error",
            "advice": "⚠️ API Error. Mock Advice: Ensure proper drainage and apply fungicide.",
            "error_details": str(e),
            "source": "System Mock (Error)"
        }
