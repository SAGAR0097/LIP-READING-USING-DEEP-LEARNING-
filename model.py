import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv3D, LSTM, Dense, Dropout, Bidirectional, MaxPool3D, Activation, Reshape, SpatialDropout3D, BatchNormalization, TimeDistributed, Flatten

class LipNet(Model):
    def __init__(self, vocab_size):
        super(LipNet, self).__init__()
        
        # 3D Convolutional layers
        self.conv1 = Conv3D(32, (3, 5, 5), strides=(1, 2, 2), padding='same', kernel_initializer='he_normal')
        self.bn1 = BatchNormalization()
        self.dropout1 = SpatialDropout3D(0.5)
        self.pool1 = MaxPool3D((1, 2, 2), strides=(1, 2, 2))
        
        self.conv2 = Conv3D(64, (3, 5, 5), strides=(1, 1, 1), padding='same', kernel_initializer='he_normal')
        self.bn2 = BatchNormalization()
        self.dropout2 = SpatialDropout3D(0.5)
        self.pool2 = MaxPool3D((1, 2, 2), strides=(1, 2, 2))
        
        self.conv3 = Conv3D(96, (3, 3, 3), strides=(1, 1, 1), padding='same', kernel_initializer='he_normal')
        self.bn3 = BatchNormalization()
        self.dropout3 = SpatialDropout3D(0.5)
        self.pool3 = MaxPool3D((1, 2, 2), strides=(1, 2, 2))
        
        # Bi-directional LSTM layers
        self.reshape = Reshape((-1, 96 * 3 * 6))
        self.dense1 = TimeDistributed(Dense(256))
        
        self.lstm1 = Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True))
        self.lstm2 = Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True))
        
        # Output layer
        self.dense2 = Dense(vocab_size + 1, kernel_initializer='he_normal', activation='softmax')

    def call(self, x, training=False):
        # Conv3D layers
        x = self.conv1(x)
        x = self.bn1(x, training=training)
        x = Activation('relu')(x)
        x = self.dropout1(x, training=training)
        x = self.pool1(x)
        
        x = self.conv2(x)
        x = self.bn2(x, training=training)
        x = Activation('relu')(x)
        x = self.dropout2(x, training=training)
        x = self.pool2(x)
        
        x = self.conv3(x)
        x = self.bn3(x, training=training)
        x = Activation('relu')(x)
        x = self.dropout3(x, training=training)
        x = self.pool3(x)
        
        # Reshape and dense
        x = self.reshape(x)
        x = self.dense1(x)
        
        # LSTM layers
        x = self.lstm1(x)
        x = self.lstm2(x)
        
        # Output
        x = self.dense2(x)
        
        return x

def CTCLoss(y_true, y_pred):
    """Custom CTC loss function."""
    batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
    input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
    label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")

    input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
    label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")

    loss = tf.keras.backend.ctc_batch_cost(y_true, y_pred, input_length, label_length)
    return loss 