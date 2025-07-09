import cv2
import os
import time

def test_video():
    # Get the absolute path to the video
    video_path = os.path.join(os.getcwd(), 'data', 's1', 'aa011.mpg')
    
    print("\n=== Video Test Tool ===")
    print(f"Looking for video at: {video_path}")
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found!")
        print("Please make sure aa011.mpg is in the data/s1 directory")
        return
    
    print("\nVideo file found! Trying to open it...")
    
    # Try to open the video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("ERROR: Could not open video file!")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print("\nVideo properties:")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    
    print("\nTrying to display video...")
    print("You should see a window titled 'Video Test'")
    print("Press 'q' to quit")
    
    # Create window and make it bigger
    cv2.namedWindow('Video Test', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video Test', 800, 600)
    
    # Add a delay to make sure window is created
    time.sleep(2)
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Make frame bigger
        frame = cv2.resize(frame, (800, 600))
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add instructions
        cv2.putText(frame, "Press 'q' to quit", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the frame
        cv2.imshow('Video Test', frame)
        
        # Slow down playback
        key = cv2.waitKey(100)  # Wait 100ms between frames
        if key == ord('q'):
            break
            
        frame_count += 1
        
        # Print progress every 10 frames
        if frame_count % 10 == 0:
            print(f"Playing frame {frame_count}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\nVideo playback finished")
    print(f"Total frames played: {frame_count}")

if __name__ == "__main__":
    test_video()
    input("\nPress Enter to exit...")