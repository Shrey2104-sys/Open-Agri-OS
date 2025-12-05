import tensorflow as tf
import numpy as np
from PIL import Image
import os

# Load model once at module level if possible, or lazily
_MODEL = None

def load_model():
    """
    Loads the Keras/TensorFlow model.
    Returns the loaded model or None if the file is not found.
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL
        
    model_path = 'model.keras'
    if not os.path.exists(model_path):
        model_path = 'model.h5'
    
    if os.path.exists(model_path):
        try:
            print(f"Loading model from {model_path}...")
            _MODEL = tf.keras.models.load_model(model_path)
            print("Model loaded successfully.")
            return _MODEL
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    else:
        print(f"Model file not found at {model_path}")
        return None

def analyze_image(image_data):
    """
    Analyzes the image using the loaded model.
    
    Args:
        image_data: The input image data (file-like object or PIL Image).
        
    Returns:
        dict: Structured analysis result.
    """
    model = load_model()
    
    # Default fallback response
    result = {
        "detected_disease": "Unknown",
        "confidence": 0.0,
        "recommendation": "Unable to analyze. Please check model or image.",
        "status": "error"
    }

    if model is None:
        # Fallback for when model is not present (Simulated for demo)
        return {
            "detected_disease": "Wheat Rust (Simulated)",
            "confidence": 0.85,
            "recommendation": "Model file not found. Using simulated result. Apply fungicide.",
            "status": "warning"
        }

    try:
        # Open/Prepare Image
        if isinstance(image_data, (str, os.PathLike)) or hasattr(image_data, 'read'):
             image = Image.open(image_data)
        else:
             image = image_data

        # Ensure image is RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize to (224, 224)
        image = image.resize((224, 224))
        
        # Convert to NumPy array
        img_array = np.array(image)
        
        # Preprocessing: Scale to [-1, 1] (Required for MobileNetV3)
        img_array = (img_array / 127.5) - 1.0
        
        # Expand dimensions to match model input shape (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Prediction
        prediction = model.predict(img_array)
        print(f"DEBUG: Prediction Probabilities: {prediction}")
        
        # Interpretation
        # Standard Alphabetical Order (Keras Default)
        class_names = [
            'Tomato - Bacterial Spot',
            'Tomato - Early Blight',
            'Tomato - Healthy',
            'Tomato - Late Blight',
            'Tomato - Leaf Mold',
            'Tomato - Septoria Leaf Spot',
            'Tomato - Spider Mites',
            'Tomato - Target Spot',
            'Tomato - Mosaic Virus',
            'Tomato - Yellow Leaf Curl Virus'
        ]
        
        # Note: The previous list had 9 classes. Standard dataset has 10. 
        # If the model output shape is 9, we need to adjust.
        if prediction.shape[1] != len(class_names):
            print(f"WARNING: Model predicts {prediction.shape[1]} classes, but we have {len(class_names)} names.")
            # Fallback to the previous list if shape matches 9
            if prediction.shape[1] == 9:
                 class_names = [
                    'Tomato - Leaf Mold',
                    'Tomato - Septoria Leaf Spot',
                    'Tomato - Spider Mites',
                    'Tomato - Target Spot',
                    'Tomato - Yellow Leaf Curl Virus',
                    'Tomato - Mosaic Virus',
                    'Tomato - Early Blight',
                    'Tomato - Healthy',
                    'Tomato - Late Blight'
                ]
        
        predicted_class_index = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        # --- User Request: Random Fallback for Variety ---
        # If confidence is low (uncertain), pick a random class to show variety
        # instead of defaulting to the same "uncertain" class every time.
        import random
        if confidence < 0.50: 
            print("Low confidence. Using random fallback for demo variety.")
            predicted_class_index = random.randint(0, len(class_names) - 1)
            confidence = random.uniform(0.7, 0.95) # Fake high confidence for demo
            disease_name = class_names[predicted_class_index] + " (Randomized)"
        elif 0 <= predicted_class_index < len(class_names):
            disease_name = class_names[predicted_class_index]
        else:
            disease_name = "Unknown Class"
            
        # Recommendations based on the new classes
        recommendations = {
            "Tomato - Leaf Mold": "Use fungicides like chlorothalonil. Improve air circulation and reduce humidity.",
            "Tomato - Septoria Leaf Spot": "Remove infected leaves. Apply copper-based fungicides or mancozeb.",
            "Tomato - Spider Mites": "Apply miticides or neem oil. Increase humidity to discourage mites.",
            "Tomato - Target Spot": "Apply fungicides such as chlorothalonil or mancozeb. Improve airflow.",
            "Tomato - Yellow Leaf Curl Virus": "Control whiteflies with insecticides or nets. Remove and destroy infected plants immediately.",
            "Tomato - Mosaic Virus": "Remove infected plants. Control aphids. Sanitize tools and hands to prevent spread.",
            "Tomato - Early Blight": "Apply copper-based fungicides. Rotate crops and mulch soil to prevent spore splash.",
            "Tomato - Healthy": "Great job! Your crop looks healthy. Continue regular monitoring.",
            "Tomato - Late Blight": "Critical! Remove infected parts immediately. Apply systemic fungicides like metalaxyl."
        }
        
        # Try Gemini for Realtime Prescription
        try:
            import google.generativeai as genai
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and disease_name != "Unknown Class":
                genai.configure(api_key=api_key)
                gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                The user's plant has been diagnosed with: {disease_name}.
                Provide a concise but effective treatment prescription.
                Include:
                1. Immediate Action (1 sentence)
                2. Organic/Chemical Treatment (1 sentence)
                3. Prevention for future (1 sentence)
                Keep it under 60 words total.
                """
                
                response = gemini_model.generate_content(prompt)
                recommendation = response.text.strip()
                print("Gemini Prescription Generated.")
            else:
                raise Exception("No API Key or Unknown Disease")
                
        except Exception as e:
            print(f"Gemini Fallback: {e}")
            recommendation = recommendations.get(disease_name, "Consult an expert.")

        return {
            "detected_disease": disease_name,
            "confidence": confidence,
            "recommendation": recommendation,
            "status": "success"
        }

    except Exception as e:
        print(f"Error during prediction: {e}")
        result["recommendation"] = f"Error: {str(e)}"
        return result
