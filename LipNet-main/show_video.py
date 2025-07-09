import cv2
import os

def check_and_show_video():
    print("\n=== Video File Check and Display ===")
    
    # Get absolute path to video
    current_dir = os.getcwd()
    video_path = os.path.join(current_dir, 'data', 's1', 'aa011.mpg')
    
    print(f"\nChecking video file:")
    print(f"Path: {video_path}")
    
    # Check if file exists
    if not os.path.exists(video_path):
        print("ERROR: Video file does not exist!")
        return
    
    # Check file size
    file_size = os.path.getsize(video_path)
    print(f"File size: {file_size} bytes")
    
    # Try to open with OpenCV
    print("\nTrying to open video with OpenCV...")
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print("\nERROR: OpenCV could not open the video file!")
        print("\nTrying with absolute path...")
        # Try with absolute path
        cap = cv2.VideoCapture(os.path.abspath(video_path))
        
        if not cap.isOpened():
            print("ERROR: Still could not open video!")
            print("\nTrying to read file content...")
            try:
                with open(video_path, 'rb') as f:
                    first_bytes = f.read(20)
                print(f"First 20 bytes of file: {first_bytes}")
                print("File is readable but might be corrupted or in wrong format")
            except Exception as e:
                print(f"Error reading file: {str(e)}")
            return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print("\nVideo properties:")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Total frames: {frame_count}")
    
    # Create window
    window_name = 'Video Player (Press Q to quit)'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1024, 768)
    
    print("\nStarting video playback...")
    print("Look for a window titled 'Video Player'")
    
    frame_number = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_number += 1
        
        # Resize frame
        frame = cv2.resize(frame, (1024, 768))
        
        # Add frame counter
        cv2.putText(frame, 
                   f"Frame: {frame_number}/{frame_count}", 
                   (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, 
                   (0, 255, 0), 
                   2)
        
        # Show frame
        cv2.imshow(window_name, frame)
        
        # Print progress
        if frame_number % 10 == 0:
            print(f"Playing frame {frame_number}/{frame_count}")
        
        # Wait and check for 'q' key
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("\nVideo playback finished")

if __name__ == "__main__":
    try:
        check_and_show_video()
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    finally:
        input("\nPress Enter to exit...")
