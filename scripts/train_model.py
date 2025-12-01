import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os

# --- Configuration ---
# Using the specific folder provided by the user
DATASET_DIR = r"C:\Users\shrey\Documents\IWP\OpenAgriOS\sample for mobilenetv2"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 5
MODEL_SAVE_PATH = r"C:\Users\shrey\Documents\IWP\OpenAgriOS\model.h5"

def train_model():
    print(f"TensorFlow Version: {tf.__version__}")
    
    if not os.path.exists(DATASET_DIR):
        print(f"Error: Dataset directory not found at {DATASET_DIR}")
        return

    print(f"\n--- Loading Data from {DATASET_DIR} ---")
    
    # Load Training Data (80%)
    try:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            DATASET_DIR,
            validation_split=0.2,
            subset="training",
            seed=123,
            image_size=IMG_SIZE,
            batch_size=BATCH_SIZE
        )

        # Load Validation Data (20%)
        val_ds = tf.keras.utils.image_dataset_from_directory(
            DATASET_DIR,
            validation_split=0.2,
            subset="validation",
            seed=123,
            image_size=IMG_SIZE,
            batch_size=BATCH_SIZE
        )
    except ValueError as e:
        print(f"Error loading dataset: {e}")
        print("Ensure the dataset folder contains subfolders for each class.")
        return

    # Get class names
    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"Classes found: {class_names}")

    # Optimize for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # 2. Build Model (Transfer Learning)
    print("\n--- Building MobileNetV2 Model ---")
    
    # Load Base Model (Pre-trained on ImageNet)
    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False, 
        weights='imagenet'
    )
    
    # Freeze the base model
    base_model.trainable = False

    # Add Custom Head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    # Combine
    model = Model(inputs=base_model.input, outputs=predictions)

    # 3. Compile
    print("\n--- Compiling Model ---")
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    model.summary()

    # 4. Train
    print(f"\n--- Starting Training for {EPOCHS} Epochs ---")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS
    )

    # 5. Save
    print(f"\n--- Saving Model to {MODEL_SAVE_PATH} ---")
    model.save(MODEL_SAVE_PATH)
    print("✅ Model saved successfully!")
    print(f"Class Names: {class_names}")

if __name__ == "__main__":
    train_model()
