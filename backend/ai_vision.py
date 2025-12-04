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
        
        # Note: The model now includes a preprocessing layer that expects [0, 255] inputs.
        # So we do NOT divide by 255.0 here.
        
        # Expand dimensions to match model input shape (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Prediction
        prediction = model.predict(img_array)
        
        # Interpretation
        # Interpretation
        # Class names must match the alphabetical order of the dataset folders
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
        
        # Map raw folder names to clean names if needed, but here we assume 
        # the model output index corresponds to the sorted folder list:
        # 0: Tomato___Leaf_Mold
        # 1: Tomato___Septoria_leaf_spot
        # 2: Tomato___Spider_mites Two-spotted_spider_mite
        # 3: Tomato___Target_Spot
        # 4: Tomato___Tomato_Yellow_Leaf_Curl_Virus
        # 5: Tomato___Tomato_mosaic_virus
        # 6: tomato early blight
        # 7: tomato heLTHY
        # 8: tomato late blight
        
        predicted_class_index = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        if 0 <= predicted_class_index < len(class_names):
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
