import tensorflow as tf
from typing import List
import cv2
import os 
import numpy as np

# Define vocabulary and print it for debugging
vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]
print("\nVocabulary:", vocab)
print("Vocabulary size:", len(vocab))

char_to_num = tf.keras.layers.StringLookup(vocabulary=vocab, oov_token="")
# Mapping integers back to original characters
num_to_char = tf.keras.layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True
)

# Print character to number mapping for debugging
print("\nCharacter to number mapping:")
for char in vocab:
    num = char_to_num([char]).numpy()[0]
    print(f"'{char}' -> {num}")

def load_video(path:str) -> List[float]: 
    print(f"Loading video from: {path}")
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {path}")
        
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video properties:")
    print(f"- Total frames: {total_frames}")
    print(f"- FPS: {fps}")
    print(f"- Resolution: {width}x{height}")
    
    if total_frames == 0:
        raise ValueError(f"Video file appears to be empty or corrupted: {path}")
    
    # Read all frames first
    all_frames = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        try:
            # Convert to grayscale
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Check frame dimensions
            if frame.shape[0] < 236 or frame.shape[1] < 220:
                print(f"Warning: Frame {frame_count} too small ({frame.shape[0]}x{frame.shape[1]}), skipping")
                continue
                
            # Crop the frame to focus on the mouth region
            try:
                cropped = frame[190:236, 80:220]
            except IndexError as e:
                print(f"Error cropping frame {frame_count}: {str(e)}")
                print(f"Frame shape: {frame.shape}")
                continue
            
            # Normalize the frame
            normalized = cv2.normalize(cropped, None, 0, 255, cv2.NORM_MINMAX)
            
            # Convert to tensor format
            frame_tensor = tf.convert_to_tensor(normalized, dtype=tf.float32)
            frame_tensor = tf.expand_dims(frame_tensor, axis=-1)  # Add channel dimension
            
            all_frames.append(frame_tensor)
            frame_count += 1
            
            if frame_count % 10 == 0:
                print(f"Processed {frame_count} frames...")
                
        except Exception as e:
            print(f"Error processing frame {frame_count}: {str(e)}")
            continue
    
    cap.release()
    
    if not all_frames:
        raise ValueError(f"No valid frames were processed from video: {path}")
        
    print(f"Successfully read {len(all_frames)} frames")
    
    # Now sample or pad to get exactly 75 frames
    if len(all_frames) > 75:
        # Sample evenly
        indices = np.linspace(0, len(all_frames)-1, 75, dtype=int)
        frames = [all_frames[i] for i in indices]
        print(f"Sampled {len(frames)} frames from {len(all_frames)} original frames")
    elif len(all_frames) < 75:
        # Pad with last frame
        frames = all_frames + [all_frames[-1]] * (75 - len(all_frames))
        print(f"Padded {len(all_frames)} frames to {len(frames)} frames")
    else:
        frames = all_frames
        print("Using all frames (exactly 75)")
    
    print(f"Final frame count: {len(frames)}")
    
    # Stack frames and normalize
    frames_tensor = tf.stack(frames)
    mean = tf.math.reduce_mean(frames_tensor)
    std = tf.math.reduce_std(tf.cast(frames_tensor, tf.float32))
    normalized = tf.cast((frames_tensor - mean), tf.float32) / std
    
    print(f"Final tensor shape: {normalized.shape}")
    print(f"Value range: min={tf.reduce_min(normalized)}, max={tf.reduce_max(normalized)}")
    
    return normalized
    
def load_alignments(path:str) -> List[str]: 
    print(f"Loading alignments from: {path}")
    if not os.path.exists(path):
        raise ValueError(f"Alignment file not found: {path}")
        
    with open(path, 'r') as f: 
        lines = f.readlines() 
    
    print("\nOriginal alignment lines:")
    for line in lines:
        print(line.strip())
    
    tokens = []
    for line in lines:
        line = line.split()
        # Skip 'sil' and 'sp' tokens
        if line[2] not in ['sil', 'sp']: 
            # Add space before each word except the first one
            if tokens:  # if not empty
                tokens.append(' ')
            tokens.append(line[2])
    
    print("\nProcessed tokens:", tokens)
    
    # Convert to tensor and get character indices
    char_indices = char_to_num(tf.reshape(tf.strings.unicode_split(tokens, input_encoding='UTF-8'), (-1)))
    
    # Debug: Convert back to characters to verify
    decoded = num_to_char(char_indices)
    decoded_text = tf.strings.reduce_join(decoded).numpy().decode('utf-8')
    print("\nDecoded text from indices:", decoded_text)
    
    return char_indices

def load_data(path: str): 
    path = bytes.decode(path.numpy())
    file_name = path.split('/')[-1].split('.')[0]
    # File name splitting for windows
    file_name = path.split('\\')[-1].split('.')[0]
    
    # Get the base directory (LipNet-main)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Try multiple video extensions
    video_extensions = ['.mp4', '.mpeg', '.mpg', '.avi', '.mov']
    video_path = None
    
    for ext in video_extensions:
        temp_path = os.path.join(base_dir, 'data', 's1', f'{file_name}{ext}')
        if os.path.exists(temp_path):
            video_path = temp_path
            break
    
    if video_path is None:
        # If not found in s1 directory, try the root data directory
        for ext in video_extensions:
            temp_path = os.path.join(base_dir, 'data', f'{file_name}{ext}')
            if os.path.exists(temp_path):
                video_path = temp_path
                break
    
    if video_path is None:
        raise ValueError(f"Video file not found for {file_name} with extensions {video_extensions}")
    
    # Try to find alignment file in multiple locations
    alignment_paths = [
        os.path.join(base_dir, 'data', 'alignments', 's1', f'{file_name}.align'),
        os.path.join(base_dir, 'data', 'alignments', f'{file_name}.align'),
        os.path.join(base_dir, 'data', f'{file_name}.align')
    ]
    
    alignment_path = None
    for path in alignment_paths:
        if os.path.exists(path):
            alignment_path = path
            break
    
    if alignment_path is None:
        print(f"Warning: No alignment file found for {file_name}. Using empty alignment.")
        # Create empty alignment with just silence
        alignments = char_to_num(tf.reshape(tf.strings.unicode_split(['sil'], input_encoding='UTF-8'), (-1)))
    else:
        alignments = load_alignments(alignment_path)
    
    print(f"Video path: {video_path}")
    print(f"Alignment path: {alignment_path if alignment_path else 'None (using empty alignment)'}")
    
    frames = load_video(video_path)
    
    return frames, alignments

video_path = os.path.join('..', 'data', 's1', 'aa.mpeg')
print(f"Video file exists: {os.path.exists(video_path)}")
print(f"Video file path: {os.path.abspath(video_path)}")