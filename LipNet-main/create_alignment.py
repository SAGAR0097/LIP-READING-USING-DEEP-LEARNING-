import tensorflow as tf
from typing import List
import cv2
import os 
import numpy as np
import json
from datetime import datetime
import argparse

vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]
char_to_num = tf.keras.layers.StringLookup(vocabulary=vocab, oov_token="")
num_to_char = tf.keras.layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True
)

def load_video(path:str) -> List[float]: 
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {path}")
        
    frames = []
    for _ in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))): 
        ret, frame = cap.read()
        if not ret:
            raise ValueError(f"Failed to read frame from video: {path}")
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = tf.convert_to_tensor(frame)
        frame = tf.image.rgb_to_grayscale(frame)
        frames.append(frame[190:236,80:220,:])
    cap.release()
    
    mean = tf.math.reduce_mean(frames)
    std = tf.math.reduce_std(tf.cast(frames, tf.float32))
    return tf.cast((frames - mean), tf.float32) / std

def load_alignments(path:str) -> List[str]: 
    with open(path, 'r') as f: 
        lines = f.readlines() 
    tokens = []
    for line in lines:
        line = line.split()
        if line[2] != 'sil': 
            tokens = [*tokens,' ',line[2]]
    return char_to_num(tf.reshape(tf.strings.unicode_split(tokens, input_encoding='UTF-8'), (-1)))[1:]

def load_data(path: str): 
    if isinstance(path, tf.Tensor):
        path = bytes.decode(path.numpy())
    file_name = path.split('\\')[-1].split('.')[0]
    video_path = os.path.join('..','data','s1',f'{file_name}.mpg')
    alignment_path = os.path.join('..','data','alignments','s1',f'{file_name}.align')
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    frames = load_video(video_path) 
    alignments = load_alignments(alignment_path)
    
    return frames, alignments 

def create_alignment_for_video(video_name="aa011"):
    # Define paths
    video_path = os.path.join('data', 's1', f'{video_name}.mpg')
    align_path = os.path.join('data', 'alignments', 's1', f'{video_name}.align')
    
    # Ensure directories exist
    os.makedirs(os.path.join('data', 's1'), exist_ok=True)
    os.makedirs(os.path.join('data', 'alignments', 's1'), exist_ok=True)
    
    # Check video file
    if not os.path.exists(video_path):
        print(f"Error: Video not found at {video_path}")
        print(f"Please ensure your video is placed at: {os.path.abspath(video_path)}")
        return
        
    print(f"Found video at: {os.path.abspath(video_path)}")
    
    # Rest of the alignment creation code...

def create_alignment(video_path, output_path):
    """
    Create an alignment file for a video
    Args:
        video_path: Path to the video file
        output_path: Path to save the alignment file
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return False

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"\nVideo Information:")
    print(f"FPS: {fps}")
    print(f"Total frames: {total_frames}")
    print(f"Duration: {duration:.2f} seconds")

    # Initialize alignment data
    alignment = {
        "video_path": video_path,
        "fps": fps,
        "total_frames": total_frames,
        "duration": duration,
        "words": []
    }

    current_word = None
    start_frame = None
    paused = False

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                # If video ends, restart from beginning
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

        # Get current frame number
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        # Display frame
        display_frame = frame.copy()
        
        # Display current time
        current_time = current_frame / fps
        cv2.putText(display_frame, f"Time: {current_time:.2f}s", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display current word if any
        if current_word:
            cv2.putText(display_frame, f"Current word: {current_word}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # Draw progress bar
            bar_width = 200
            bar_height = 20
            bar_x = 10
            bar_y = 100
            progress = (current_frame - start_frame) / (total_frames - start_frame)
            cv2.rectangle(display_frame, (bar_x, bar_y), 
                         (bar_x + int(bar_width * progress), bar_y + bar_height),
                         (0, 255, 0), -1)
            cv2.rectangle(display_frame, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height),
                         (255, 255, 255), 2)

        # Display instructions
        cv2.putText(display_frame, "Controls:", (10, display_frame.shape[0] - 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, "SPACE: Start/End word", (10, display_frame.shape[0] - 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, "P: Pause/Resume", (10, display_frame.shape[0] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, "Q: Quit", (10, display_frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('Video Alignment Tool', display_frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):  # Quit
            break
        elif key == ord('p'):  # Pause/Resume
            paused = not paused
        elif key == ord(' '):  # Space to start/end word
            if current_word is None:
                # Start new word
                word = input("Enter word: ")
                if word:
                    current_word = word
                    start_frame = current_frame
                    print(f"Started word '{word}' at frame {start_frame}")
            else:
                # End current word
                end_frame = current_frame
                alignment["words"].append({
                    "word": current_word,
                    "start_frame": start_frame,
                    "end_frame": end_frame,
                    "start_time": start_frame / fps,
                    "end_time": end_frame / fps
                })
                print(f"Ended word '{current_word}' at frame {end_frame}")
                current_word = None
                start_frame = None

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    # Save alignment data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(alignment, f, indent=4)

    print(f"\nAlignment saved to: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Create alignment file for video')
    parser.add_argument('--input', '-i', help='Input video path')
    parser.add_argument('--output', '-o', help='Output alignment file path')
    args = parser.parse_args()

    if not args.input:
        args.input = input("Enter input video path: ").strip()
    
    if not args.output:
        # Generate output path based on input path
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = os.path.join(os.path.dirname(args.input), f"{base_name}_alignment.json")

    print("\n=== Video Alignment Creation Tool ===")
    print("Instructions:")
    print("1. Press SPACE to start marking a word")
    print("2. Enter the word when prompted")
    print("3. Press SPACE again to end the word")
    print("4. Press P to pause/resume the video")
    print("5. Press Q to quit")
    print("\nPress any key to start...")
    cv2.waitKey(0)
    
    if create_alignment(args.input, args.output):
        print("Alignment creation completed successfully")
    else:
        print("Alignment creation failed")

if __name__ == "__main__":
    main() 