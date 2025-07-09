import cv2
import os

def test_video_files():
    print("\n=== Video File Test ===")
    
    # Path to video directory
    video_dir = os.path.join('..', 'data', 's1')
    print(f"Looking in directory: {os.path.abspath(video_dir)}")
    
    # List all video files
    video_files = os.listdir(video_dir)
    print(f"\nFound {len(video_files)} files")
    
    # Test each video file
    for video_name in video_files:
        print(f"\nTesting: {video_name}")
        video_path = os.path.join(video_dir, video_name)
        
        # Check file size
        file_size = os.path.getsize(video_path)
        print(f"File size: {file_size} bytes")
        
         # Try to open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("ERROR: Could not open video!")
            continue
            
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Resolution: {width}x{height}")
        print(f"FPS: {fps}")
        print(f"Frame count: {frame_count}")
        
        # Try to read first frame
        ret, frame = cap.read()
        if ret:
            print("Successfully read first frame")
        else:
            print("ERROR: Could not read frames!")
            
        cap.release()

if __name__ == "__main__":
    test_video_files()
    input("\nPress Enter to exit...")
