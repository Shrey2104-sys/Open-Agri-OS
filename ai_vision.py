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
        
    model_path = 'model.h5'
    if os.path.exists(model_path):
        try:
            _MODEL = tf.keras.models.load_model(model_path)
            print(f"Model loaded from {model_path}")
            return _MODEL
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    else:
        print(f"Warning: {model_path} not found. Returning None placeholder.")
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
        
        # Normalize (divide by 255.0)
        img_array = img_array / 255.0
        
        # Expand dimensions to match model input shape (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Prediction
        prediction = model.predict(img_array)
        
        # Interpretation
        class_names = ['Healthy', 'Early Blight', 'Late Blight']
        predicted_class_index = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        if 0 <= predicted_class_index < len(class_names):
            disease_name = class_names[predicted_class_index]
        else:
            disease_name = "Unknown Class"
            
        # Simple recommendation logic based on disease
        recommendations = {
            "Healthy": "Crop is healthy. Continue standard monitoring.",
            "Early Blight": "Apply copper-based fungicides. Improve air circulation.",
            "Late Blight": "Remove infected parts immediately. Apply systemic fungicides.",
            "Unknown Class": "Consult an expert for manual verification."
        }
        
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
