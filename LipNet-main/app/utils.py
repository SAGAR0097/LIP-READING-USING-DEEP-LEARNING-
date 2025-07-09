import tensorflow as tf
from typing import List
import cv2
import os
import numpy as np

# Define vocabulary
vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]

# Create character to number and number to character layers
char_to_num = tf.keras.layers.StringLookup(vocabulary=vocab, oov_token="")
num_to_char = tf.keras.layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True
)

def load_video(path: str) -> List[float]:
    """Load and preprocess video frames with better error handling."""
    print(f"\nAttempting to load video: {path}")
    
    # Verify file exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"Video file not found: {path}")
    
    # Open video
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {path}")
    
    try:
        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video properties:")
        print(f"Frame count: {frame_count}")
        print(f"Resolution: {width}x{height}")
        
        frames = []
        successful_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            try:
                # Ensure frame is not None and has the correct shape
                if frame is None:
                    print(f"Warning: Skipping frame {successful_frames} (None frame)")
                    continue
                
                if frame.size == 0:
                    print(f"Warning: Skipping frame {successful_frames} (Empty frame)")
                    continue
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to float32 before creating tensor
                frame_float = frame_rgb.astype(np.float32)
                
                # Create tensor
                frame_tensor = tf.convert_to_tensor(frame_float)
                
                # Convert to grayscale
                frame_gray = tf.image.rgb_to_grayscale(frame_tensor)
                
                # Ensure frame is large enough to crop
                if frame_gray.shape[0] >= 236 and frame_gray.shape[1] >= 220:
                    # Crop the region of interest
                    cropped = frame_gray[190:236, 80:220, :]
                    frames.append(cropped)
                    successful_frames += 1
                else:
                    print(f"Warning: Frame {successful_frames} too small for cropping: {frame_gray.shape}")
                
            except Exception as e:
                print(f"Warning: Error processing frame {successful_frames}: {str(e)}")
                continue
        
        print(f"Successfully processed {successful_frames} frames")
        
        if not frames:
            raise ValueError(f"No valid frames were read from video: {path}")
        
        # Stack frames
        frames_tensor = tf.stack(frames)
        
        # Normalize
        mean = tf.math.reduce_mean(frames_tensor)
        std = tf.math.reduce_std(tf.cast(frames_tensor, tf.float32))
        normalized_frames = tf.cast((frames_tensor - mean), tf.float32) / std
        
        print(f"Final tensor shape: {normalized_frames.shape}")
        return normalized_frames
        
    except Exception as e:
        print(f"Error in load_video: {str(e)}")
        raise
        
    finally:
        cap.release()

def load_alignments(path: str) -> List[str]:
    """Load and process alignment files."""
    print(f"\nLoading alignments from: {path}")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Alignment file not found: {path}")
    
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
        
        tokens = []
        for line in lines:
            line = line.split()
            if line[2] != 'sil':
                tokens = [*tokens, ' ', line[2]]
        
        result = char_to_num(tf.reshape(tf.strings.unicode_split(tokens, input_encoding='UTF-8'), (-1)))[1:]
        print(f"Processed {len(tokens)} tokens")
        return result
        
    except Exception as e:
        print(f"Error in load_alignments: {str(e)}")
        raise

def load_data(path: str):
    """Load both video and alignment data."""
    print(f"\nStarting data loading process for: {path}")
    
    try:
        # Convert tensor path to string if necessary
        if isinstance(path, tf.Tensor):
            path = bytes.decode(path.numpy())
        
        # Get the file name
        file_name = path.split('\\')[-1].split('.')[0]
        print(f"Processing file: {file_name}")
        
        # Construct paths
        video_path = os.path.join('..', 'data', 's1', f'{file_name}.mpg')
        alignment_path = os.path.join('..', 'data', 'alignments', 's1', f'{file_name}.align')
        
        print(f"Video path: {video_path}")
        print(f"Alignment path: {alignment_path}")
        
        # Load video frames and alignments
        frames = load_video(video_path)
        alignments = load_alignments(alignment_path)
        
        return frames, alignments
        
    except Exception as e:
        print(f"Error in load_data: {str(e)}")
        raise
