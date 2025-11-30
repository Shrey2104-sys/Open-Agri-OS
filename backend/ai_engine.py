import os
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import img_to_array

# --- Configuration ---
MODEL_PATH = 'model.h5'

# --- Model Loading ---
def load_model():
    """
    Loads the trained model if available, otherwise loads pre-trained MobileNetV2.
    """
    if os.path.exists(MODEL_PATH):
        try:
            print(f"Loading custom model from {MODEL_PATH}...")
            return tf.keras.models.load_model(MODEL_PATH)
        except Exception as e:
            print(f"Error loading custom model: {e}")
            return None
    else:
        print("Custom model not found. Loading MobileNetV2 (ImageNet weights)...")
        return MobileNetV2(weights='imagenet')

# Initialize model globally to avoid reloading
model = load_model()

# --- Prediction Logic ---
def predict_disease(image_file):
    """
    Analyzes an image file and returns the predicted disease/class.
    
    Args:
        image_file: File object or path to image.
        
    Returns:
        dict: {'class': str, 'confidence': float}
    """
    global model
    if model is None:
         model = load_model()

    try:
        # Preprocess
        img = Image.open(image_file).convert('RGB')
        img = img.resize((224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Predict
        predictions = model.predict(img_array)
        
        # Interpret Results
        if os.path.exists(MODEL_PATH):
            # Custom Model Logic (Assuming softmax output)
            # You would need a mapping of index to class names here
            # For now, we'll simulate it or return the index
            class_index = np.argmax(predictions[0])
            confidence = float(np.max(predictions[0]))
            
            # Placeholder class names - in a real app, load these from a file
            class_names = ['Healthy', 'Early Blight', 'Late Blight'] 
            predicted_class = class_names[class_index] if class_index < len(class_names) else f"Class {class_index}"
            
        else:
            # MobileNetV2 (ImageNet) Logic
            decoded = decode_predictions(predictions, top=1)[0][0]
            predicted_class = decoded[1] # Class name
            confidence = float(decoded[2]) # Confidence

        return {
            'class': predicted_class,
            'confidence': confidence
        }

    except Exception as e:
        print(f"Prediction Error: {e}")
        return {
            'class': 'Error',
            'confidence': 0.0,
            'details': str(e)
        }
