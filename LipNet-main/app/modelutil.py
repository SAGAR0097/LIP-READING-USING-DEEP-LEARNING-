import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.layers import MaxPool3D, Activation, Reshape, SpatialDropout3D
from tensorflow.keras.layers import BatchNormalization, TimeDistributed, Flatten
import os

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
    
    model.add(Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True)))
    model.add(Dropout(.5))
    
    model.add(Dense(41, kernel_initializer='he_normal', activation='softmax'))
    
    # Load pre-trained weights if available
    checkpoint_path = os.path.join('..', 'models', 'checkpoint')
    if os.path.exists(checkpoint_path):
        model.load_weights(checkpoint_path)
    
    return model
