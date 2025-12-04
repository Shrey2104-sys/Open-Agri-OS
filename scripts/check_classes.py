import tensorflow as tf
import os

DATASET_DIR = r"C:\Users\shrey\Documents\IWP\sd\sample for mobilenetv2"

try:
    ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        image_size=(224, 224),
        batch_size=32,
        shuffle=False
    )
    print("--- TENSORFLOW CLASS NAMES ---")
    for i, name in enumerate(ds.class_names):
        print(f"{i}: {name}")
    print("------------------------------")
except Exception as e:
    print(f"Error: {e}")
