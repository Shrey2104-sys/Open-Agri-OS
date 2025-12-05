import os
import zipfile
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV3Large
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils.class_weight import compute_class_weight

# --- Configuration ---
DATA_DIR = r"c:\Users\shrey\Documents\IWP\sd\sample for mobilenetv2"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_PHASE_1 = 1
EPOCHS_PHASE_2 = 1

def setup_dataset():
    """Checks if local dataset exists."""
    if os.path.exists(DATA_DIR):
        print(f"Using local dataset at {DATA_DIR}")
        return True
    else:
        print(f"Error: Dataset not found at {DATA_DIR}")
        return False

def create_data_generators():
    """Creates training and validation generators with augmentation."""
    # MobileNetV3 specific preprocessing
    preprocess_input = tf.keras.applications.mobilenet_v3.preprocess_input

    # Use validation_split since we have a flat directory structure
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2
    )

    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory not found at {DATA_DIR}")
        return None, None

    train_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True,
        subset='training'
    )

    valid_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False,
        subset='validation'
    )

    return train_generator, valid_generator

def build_model(num_classes):
    """Builds MobileNetV3Large with custom head."""
    base_model = MobileNetV3Large(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
        pooling='avg' # GlobalAveragePooling built-in
    )

    x = base_model.output
    x = Dense(1024, activation='relu')(x)
    x = Dropout(0.2)(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    return model, base_model

def get_class_weights(train_generator):
    """Calculates class weights to handle imbalance."""
    class_indices = train_generator.class_indices
    class_counts = np.bincount(train_generator.classes)
    total_samples = np.sum(class_counts)
    num_classes = len(class_indices)
    
    weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_generator.classes),
        y=train_generator.classes
    )
    
    class_weight_dict = dict(enumerate(weights))
    print("Class Weights:", class_weight_dict)
    return class_weight_dict

def main():
    if not setup_dataset():
        return

    train_gen, valid_gen = create_data_generators()
    if not train_gen:
        return

    num_classes = train_gen.num_classes
    print(f"Detected {num_classes} classes.")

    class_weights = get_class_weights(train_gen)

    # --- Step 2: Model Architecture ---
    model, base_model = build_model(num_classes)

    # --- Step 3: Training Strategy ---
    
    # Phase 1: Transfer Learning (Warm-up)
    print("\n--- Phase 1: Transfer Learning (Warm-up) ---")
    for layer in base_model.layers:
        layer.trainable = False

    model.compile(
        optimizer=Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(
        train_gen,
        epochs=EPOCHS_PHASE_1,
        validation_data=valid_gen,
        class_weight=class_weights
    )

    # Phase 2: Fine-Tuning
    print("\n--- Phase 2: Fine-Tuning ---")
    
    # Unfreeze top 30 layers
    for layer in base_model.layers:
        layer.trainable = False # Reset
    
    # Unfreeze the last 30 layers
    for layer in base_model.layers[-30:]:
        layer.trainable = True

    print("Re-compiling with Low Learning Rate (1e-5)...")
    model.compile(
        optimizer=Adam(learning_rate=1e-5), # Very Low LR
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint('model.h5', save_best_only=True)
    ]

    model.fit(
        train_gen,
        epochs=EPOCHS_PHASE_2,
        validation_data=valid_gen,
        class_weight=class_weights,
        callbacks=callbacks
    )

    print("Training Complete. Model saved as 'model.keras'")
    # Save explicitly to ensure it overwrites
    model.save('model.keras')

if __name__ == '__main__':
    main()
