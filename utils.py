import os
import cv2
import tensorflow as tf
from typing import List, Tuple

# Define vocabulary
VOCAB = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]

# Create character to number and number to character layers
char_to_num = tf.keras.layers.StringLookup(vocabulary=VOCAB, oov_token="")
num_to_char = tf.keras.layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True
)

def load_video(path: str) -> tf.Tensor:
    """Load and preprocess video frames."""
    cap = cv2.VideoCapture(path)
    frames = []
    for _ in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, frame = cap.read()
        frame = tf.image.rgb_to_grayscale(frame)
        frames.append(frame[190:236, 80:220, :])
    cap.release()
    
    frames = tf.convert_to_tensor(frames)
    mean = tf.math.reduce_mean(frames)
    std = tf.math.reduce_std(tf.cast(frames, tf.float32))
    return tf.cast((frames - mean), tf.float32) / std

def load_alignments(path: str) -> tf.Tensor:
    """Load and process alignment files."""
    with open(path, 'r') as f:
        lines = f.readlines()
    tokens = []
    for line in lines:
        line = line.split()
        if line[2] != 'sil':
            tokens = [*tokens, ' ', line[2]]
    return char_to_num(tf.reshape(tf.strings.unicode_split(tokens, input_encoding='UTF-8'), (-1)))[1:]

def load_data(path: str) -> Tuple[tf.Tensor, tf.Tensor]:
    """Load both video and alignment data."""
    if isinstance(path, bytes):
        path = bytes.decode(path)
    
    file_name = path.split('\\')[-1].split('.')[0]
    video_path = os.path.join('data', 's1', f'{file_name}.mpg')
    alignment_path = os.path.join('data', 'alignments', 's1', f'{file_name}.align')
    
    frames = load_video(video_path)
    alignments = load_alignments(alignment_path)
    
    return frames, alignments

def download_data():
    """Download the dataset if not present."""
    if not os.path.exists('data'):
        import gdown
        url = 'https://drive.google.com/uc?id=1YlvpDLix3S-U8fd-gqRwPcWXAXm8JwjL'
        output = 'data.zip'
        gdown.download(url, output, quiet=False)
        gdown.extractall('data.zip') 