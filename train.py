import os
import tensorflow as tf
from utils import load_data, download_data, VOCAB, char_to_num
from model import LipNet, CTCLoss
import glob

def main():
    # Set up GPU memory growth
    physical_devices = tf.config.list_physical_devices('GPU')
    try:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    except:
        print("No GPU available or error in GPU configuration")
        pass

    # Download data if not present
    download_data()

    # Create data pipeline
    data_path = os.path.join('data', 's1', '*.mpg')
    data_files = glob.glob(data_path)

    # Create dataset
    dataset = tf.data.Dataset.from_tensor_slices(data_files)
    dataset = dataset.map(lambda x: tf.py_function(load_data, [x], [tf.float32, tf.int64]))
    dataset = dataset.shuffle(buffer_size=50)
    dataset = dataset.batch(4)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)

    # Split into train and validation
    val_size = int(len(data_files) * 0.2)
    train_dataset = dataset.skip(val_size)
    val_dataset = dataset.take(val_size)

    # Initialize model
    model = LipNet(vocab_size=len(VOCAB))

    # Compile model
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
    model.compile(optimizer=optimizer, loss=CTCLoss)

    # Create checkpoint callback
    checkpoint_path = "checkpoints/lipnet"
    checkpoint_dir = os.path.dirname(checkpoint_path)
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)

    cp_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=True,
        save_best_only=True,
        monitor='val_loss',
        mode='min',
        verbose=1
    )

    # Train model
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=100,
        callbacks=[cp_callback]
    )

    # Save final model
    model.save_weights('models/lipnet_final')

if __name__ == "__main__":
    main() 