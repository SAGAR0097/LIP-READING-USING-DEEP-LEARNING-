import cv2
import numpy as np
import os
import argparse

def select_crop_region(video_path):
    """
    Allow user to select crop region interactively
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return None

    # Read first frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read video frame")
        return None

    # Create window and set mouse callback
    window_name = "Select Crop Region (Press 'c' to confirm, 'r' to reset)"
    cv2.namedWindow(window_name)
    
    # Initialize crop region
    crop_region = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
    drawing = False
    start_point = None
    end_point = None

    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, start_point, end_point, frame
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)
            end_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                end_point = (x, y)
                temp_frame = frame.copy()
                cv2.rectangle(temp_frame, start_point, end_point, (0, 255, 0), 2)
                cv2.imshow(window_name, temp_frame)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            end_point = (x, y)
            crop_region['x1'] = min(start_point[0], end_point[0])
            crop_region['y1'] = min(start_point[1], end_point[1])
            crop_region['x2'] = max(start_point[0], end_point[0])
            crop_region['y2'] = max(start_point[1], end_point[1])

    cv2.setMouseCallback(window_name, mouse_callback)
    cv2.imshow(window_name, frame)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):  # Confirm selection
            break
        elif key == ord('r'):  # Reset selection
            start_point = None
            end_point = None
            cv2.imshow(window_name, frame)
        elif key == ord('q'):  # Quit
            cap.release()
            cv2.destroyAllWindows()
            return None

    cap.release()
    cv2.destroyAllWindows()
    return crop_region

def crop_video(input_path, output_path, x1=0, y1=0, x2=0, y2=0):
    """
    Crop a video file to focus on the lip region
    Args:
        input_path: Path to input video
        output_path: Path to save cropped video
        x1, y1, x2, y2: Coordinates for cropping (if 0, will use default values)
    """
    # Open the video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {input_path}")
        return False

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Set default crop values if not provided
    if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
        # Default crop values for lip region
        x1 = width // 4
        y1 = height // 3
        x2 = (width * 3) // 4
        y2 = (height * 2) // 3

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (x2-x1, y2-y1))

    print(f"Processing video: {input_path}")
    print(f"Total frames: {total_frames}")
    print(f"Crop region: ({x1}, {y1}) to ({x2}, {y2})")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Crop the frame
        cropped_frame = frame[y1:y2, x1:x2]
        
        # Write the cropped frame
        out.write(cropped_frame)
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processed {frame_count}/{total_frames} frames")

    # Release resources
    cap.release()
    out.release()
    print(f"Video processing complete. Output saved to: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Crop video to focus on lip region')
    parser.add_argument('--input', '-i', help='Input video path')
    parser.add_argument('--output', '-o', help='Output video path')
    parser.add_argument('--interactive', '-t', action='store_true', help='Use interactive crop region selection')
    args = parser.parse_args()

    if not args.input:
        args.input = input("Enter input video path: ").strip()
    
    if not args.output:
        # Generate output path based on input path
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = os.path.join(os.path.dirname(args.input), f"{base_name}_cropped.mp4")

    if args.interactive:
        crop_region = select_crop_region(args.input)
        if crop_region:
            crop_video(args.input, args.output, 
                      crop_region['x1'], crop_region['y1'],
                      crop_region['x2'], crop_region['y2'])
    else:
        crop_video(args.input, args.output)

if __name__ == "__main__":
    main() 