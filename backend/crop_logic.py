import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 1. The "Master Crop Database" (Internal Storage)
MASTER_CROP_DB = {
    "Himalayan": {
        "description": "Cold, Mountainous, Temperate",
        "crops": ["Apple", "Walnut", "Saffron", "Cherry", "Plum"],
        "soil": "Mountain Soil (Forest Soil)",
        "water": "Rainfed / Snowmelt"
    },
    "Northern_Plains": {
        "description": "Temperate, Fertile Alluvial Soil",
        "crops": ["Wheat", "Mustard", "Sugarcane", "Potato", "Sunflower"],
        "soil": "Alluvial Soil",
        "water": "Irrigated (Canal/Tube well)"
    },
    "Arid": {
        "description": "Hot, Dry, Desert-like",
        "crops": ["Date Palm", "Bajra", "Jowar", "Guar", "Aloe Vera"],
        "soil": "Desert/Sandy Soil",
        "water": "Drought Resistant / Drip Irrigation"
    },
    "Deccan_Plateau": {
        "description": "Semi-Arid, Black/Red Soil",
        "crops": ["Cotton", "Soybean", "Tur (Pigeon Pea)", "Custard Apple", "Maize"],
        "soil": "Black Cotton Soil / Red Loamy",
        "water": "Rainfed / Tank Irrigation"
    },
    "Coastal": {
        "description": "Hot, Humid, High Rainfall",
        "crops": ["Rice", "Coconut", "Rubber", "Black Pepper", "Arecanut", "Banana"],
        "soil": "Laterite / Coastal Alluvium",
        "water": "Rainfed / High Moisture"
    },
    "Eastern_Delta": {
        "description": "Wet, Marshy, Heavy Rainfall",
        "crops": ["Jute", "Rice", "Betel nut"],
        "soil": "Peaty / Marshy Soil",
        "water": "Flood Prone / Abundant Water"
    }
}

def analyze_location(lat, lon):
    """
    Simulates a 4-Factor Analysis based on Latitude/Longitude.
    Returns a dictionary with the detected zone, soil, water, and recommended crops.
    """
    try:
        lat = float(lat)
        lon = float(lon)
        
        # --- 1. Geography Analysis (Simplified Logic for Demo) ---
        if lat > 31.0:
            zone_key = "Himalayan"
        elif 28.0 <= lat <= 31.0:
            # Punjab, Haryana, UP
            zone_key = "Northern_Plains"
        elif 23.0 <= lat < 28.0:
            # Central India split
            # West of 76E is roughly Rajasthan (Arid)
            if lon < 76.0:
                zone_key = "Arid"
            else:
                # MP, parts of Maharashtra/UP
                zone_key = "Northern_Plains" if lat > 25 else "Deccan_Plateau"
        elif lat < 23.0:
            # South India
            # Deep South (Kerala/TN) is mostly tropical/coastal
            if lat < 13.0:
                zone_key = "Coastal"
            # West Coast (Konkan) < 74.5E
            # East Coast (Andhra) > 79.5E
            elif lon < 74.5 or lon > 79.5:
                zone_key = "Coastal"
            else:
                zone_key = "Deccan_Plateau"
        else:
            # Fallback
            zone_key = "Deccan_Plateau"
            
        # Special case for Eastern Delta (West Bengal / North East)
        if lon > 87.0 and 21.0 < lat < 27.0:
            zone_key = "Eastern_Delta"

        # --- 2. Retrieve Data from Master DB ---
        zone_data = MASTER_CROP_DB.get(zone_key, MASTER_CROP_DB["Deccan_Plateau"])

        return {
            "status": "success",
            "zone": zone_key,
            "description": zone_data["description"],
            "recommended_crops": zone_data["crops"],
            "soil_type": zone_data["soil"],
            "water_source": zone_data["water"],
            "factors": {
                "geography": f"Latitude {lat:.2f} indicates {zone_key} region.",
                "soil": zone_data["soil"],
                "water": zone_data["water"],
                "weather": zone_data["description"]
            }
        }

    except Exception as e:
        print(f"Error in analyze_location: {e}")
        return {
            "status": "error",
            "message": str(e),
            "recommended_crops": []
        }

def get_gemini_recommendation(lat, lon, zone_info):
    """
    Uses Google Gemini to refine the recommendation with local specifics.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Acting as a local expert farmer for coordinates {lat}, {lon} (Region: {zone_info.get('zone')}).
        
        1. Confirm the likely soil type (e.g., Red Loamy vs Black Cotton) for this specific micro-location.
        2. Confirm water access situation (River basin vs Dryland).
        3. Suggest 3 specific high-yield crop varieties (e.g., not just 'Rice', but 'Basmati 370' or 'Sona Masuri') suited for this micro-climate.
        
        Keep the response concise and structured as JSON.
        Format:
        {{
            "soil_confirmation": "...",
            "water_confirmation": "...",
            "varieties": ["Crop A (Variety X)", "Crop B (Variety Y)", "Crop C (Variety Z)"]
        }}
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None
