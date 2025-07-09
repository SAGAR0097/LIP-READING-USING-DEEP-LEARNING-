import cv2
import os
from utils import download_data

def display_video(video_name='aa.mpg'):
    # First, ensure data is downloaded
    if not os.path.exists(os.path.join('data', 's1')):
        print("Downloading data...")
        download_data()
    
    # Construct the video path
    video_path = os.path.join('data', 's1', video_name)
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return
    
    print("Video properties:")
    print(f"- Frame count: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")
    print(f"- Frame width: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}")
    print(f"- Frame height: {int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"- FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    
    # Create a window
    cv2.namedWindow('Video Display', cv2.WINDOW_NORMAL)
    
    try:
        while True:
            ret, frame = cap.read()
            
            # If frame is read correctly ret is True
            if not ret:
                print("End of video or error reading frame")
                break
                
            # Display the original frame
            cv2.imshow('Video Display', frame)
            
            # Also display the cropped region used in the model
            cropped_frame = frame[190:236, 80:220]
            cv2.imshow('Cropped Lip Region', cropped_frame)
            
            # Wait for 30 milliseconds and check for 'q' key to quit
            key = cv2.waitKey(30)
            if key == ord('q'):
                print("Video display stopped by user")
                break
    
    except Exception as e:
        print(f"Error occurred while displaying video: {str(e)}")
    
    finally:
        # Release everything when done
        cap.release()
        cv2.destroyAllWindows()

def check_video_file(video_name='aa.mpg'):
    """Utility function to check video file status"""
    video_path = os.path.join('data', 's1', video_name)
    print(f"Checking video file: {video_name}")
    print(f"Full path: {os.path.abspath(video_path)}")
    print(f"File exists: {os.path.exists(video_path)}")
    
    if os.path.exists(video_path):
        print(f"File size: {os.path.getsize(video_path)} bytes")

if __name__ == "__main__":
    print("Starting video display program...")
    print("Press 'q' to quit the video display")
    
    # First check the video file
    check_video_file()
    
    # Then try to display it
    display_video()