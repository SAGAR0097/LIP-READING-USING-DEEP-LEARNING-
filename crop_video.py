import cv2
import os
import argparse
import sys
import numpy as np

def get_video_dimensions(video_path):
    """Get video dimensions and frame count."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    return width, height, fps, frame_count

def crop_video(input_path, output_path):
    """Crop video to fixed dimensions."""
    # Get video dimensions
    width, height, fps, frame_count = get_video_dimensions(input_path)
    print(f"\nVideo dimensions: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Total frames: {frame_count}")
    
    # Fixed crop dimensions
    x = (width - 140) // 2  # Center horizontally
    y = (height - 46) // 2  # Center vertically
    w = 140  # Fixed width
    h = 46   # Fixed height
    
    print(f"\nCropping video to fixed dimensions: {w}x{h}")
    
    # Open video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {input_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    
    # Process frames
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Crop frame
        cropped = frame[y:y+h, x:x+w]
        
        # Write frame
        out.write(cropped)
        frame_count += 1
        
        # Print progress
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames...")
    
    # Clean up
    cap.release()
    out.release()
    
    print(f"\nVideo processing complete!")
    print(f"Output saved to: {output_path}")
    print(f"Final dimensions: {w}x{h}")
    print(f"Total frames processed: {frame_count}")

def main():
    parser = argparse.ArgumentParser(description='Crop video to fixed dimensions (140x46)')
    parser.add_argument('input', help='Input video file path')
    parser.add_argument('--output', '-o', help='Output video file path')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found: {args.input}")
    
    # Set default output path if not provided
    if not args.output:
        input_dir = os.path.dirname(args.input)
        input_filename = os.path.basename(args.input)
        name, ext = os.path.splitext(input_filename)
        args.output = os.path.join(input_dir, f"{name}_cropped{ext}")
    
    try:
        crop_video(args.input, args.output)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 