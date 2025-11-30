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
        return {
            "status": "warning",
            "advice": "⚠️ API Key missing. Please set GEMINI_API_KEY in .env file.",
            "source": "System Mock"
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
        return {
            "status": "error",
            "advice": "⚠️ API Error. Unable to fetch advice.",
            "error_details": str(e),
            "source": "System Mock"
        }

def get_satellite_map(location_name):
    """
    Returns the path to the satellite map for a given location.
    For the hackathon, this checks for a static demo file.
    """
    # In a real app, you would use Google Maps Static API or Sentinel Hub here.
    # For now, we check if the demo map exists in the static folder.
    
    demo_map_path = "static/scout_demo_map.png"
    
    if os.path.exists(demo_map_path):
        return {
            "status": "success",
            "image_url": "/" + demo_map_path, # URL path for frontend
            "message": f"Satellite data for {location_name} acquired."
        }
    else:
        return {
            "status": "error",
            "message": "Demo map not found. Please ensure static/scout_demo_map.png exists."
        }
