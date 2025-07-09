import os 
from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import Conv3D, LSTM, Dense, Dropout, Bidirectional, MaxPool3D, Activation, Reshape, SpatialDropout3D, BatchNormalization, TimeDistributed, Flatten

def load_model() -> Sequential: 
    model = Sequential()

    model.add(Conv3D(128, 3, input_shape=(75,46,140,1), padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPool3D((1,2,2)))

    model.add(Conv3D(256, 3, padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPool3D((1,2,2)))

    model.add(Conv3D(75, 3, padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPool3D((1,2,2)))

    model.add(TimeDistributed(Flatten()))

    model.add(Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True), name='bidirectional_1'))
    model.add(Dropout(.5))

    model.add(Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True), name='bidirectional_2'))
    model.add(Dropout(.5))

    model.add(Dense(41, kernel_initializer='he_normal', activation='softmax'))

    # Get the base directory (LipNet-main)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checkpoint_path = os.path.join(base_dir, 'models', 'checkpoint')
    
    print(f"Loading model from: {checkpoint_path}")
    if not os.path.exists(checkpoint_path):
        raise ValueError(f"Model checkpoint not found at: {checkpoint_path}")
    
    # Print model summary
    model.summary()
    
    # Load weights
    try:
        model.load_weights(checkpoint_path)
        print("Model weights loaded successfully")
        
        # Verify weights were loaded
        for layer in model.layers:
            if layer.weights:
                print(f"Layer {layer.name} has {len(layer.weights)} weights")
                for w in layer.weights:
                    print(f"  - {w.name}: shape={w.shape}")
    except Exception as e:
        print(f"Error loading weights: {str(e)}")
        raise

    return model