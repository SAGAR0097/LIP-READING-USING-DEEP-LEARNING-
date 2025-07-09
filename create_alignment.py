import cv2
import os
import time

def find_video_file(video_name):
    """
    Find video file with any supported extension
    """
    supported_extensions = ['.mpg', '.mpeg', '.mp4', '.avi', '.mov']
    base_path = os.path.join('data', 's1', video_name)
    
    for ext in supported_extensions:
        video_path = base_path + ext
        if os.path.exists(video_path):
            return video_path
    
    return None

def create_alignment_for_video(video_name="aa011"):
    """
    Create alignment file for the specified video with improved visibility
    """
    # Find video file with correct extension
    video_path = find_video_file(video_name)
    if not video_path:
        print(f"Error: Video not found for '{video_name}'")
        print("Supported formats: .mpg, .mpeg, .mp4, .avi, .mov")
        print("Please check if the video exists in data/s1/ directory")
        return
    
    align_path = os.path.join('data', 'alignments', 's1', f'{video_name}.align')
    
    # Create alignments directory if it doesn't exist
    os.makedirs(os.path.dirname(align_path), exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video at {video_path}")
        print("Please check if the file is corrupted or the format is supported")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_ms = int((total_frames / fps) * 1000)
    
    print("\n=== Video Information ===")
    print(f"Video path: {video_path}")
    print(f"Duration: {duration_ms/1000:.2f} seconds")
    print(f"FPS: {fps}")
    print(f"Total frames: {total_frames}")
    
    print("\n=== INSTRUCTIONS ===")
    print("1. You will see a window titled 'Video Alignment'")
    print("2. The video will play in slow motion")
    print("3. Press SPACE when each word starts")
    print("4. Type the word in the terminal")
    print("5. Press 'q' to quit when done")
    
    input("\nPress Enter to start the video...")
    
    # Create window with larger size
    cv2.namedWindow('Video Alignment', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video Alignment', 800, 600)
    
    # Store word timings
    timings = []
    current_frame = 0
    
    print("\nVideo is now playing... Look for a window titled 'Video Alignment'")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Make the frame larger
        frame = cv2.resize(frame, (800, 600))
        
        # Add text overlay to make it more visible
        cv2.putText(frame, 
                   "Press SPACE when a word starts, 'q' to quit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (0, 255, 0), 2)
        
        # Show frame
        cv2.imshow('Video Alignment', frame)
        current_time = int((current_frame / fps) * 1000)
        
        # Slow down playback for better accuracy
        key = cv2.waitKey(100)  # Slower playback (adjust this value if needed)
        
        if key == ord(' '):  # Space pressed - mark word
            # Pause video and show message
            overlay = frame.copy()
            cv2.putText(overlay, 
                       "PAUSED - Enter word in terminal", 
                       (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 
                       1.5, (0, 0, 255), 3)
            cv2.imshow('Video Alignment', overlay)
            
            # Get word from user
            word = input(f"\nEnter word at {current_time}ms: ").lower().strip()
            timings.append((current_time, word))
            print(f"Marked word: '{word}' at {current_time}ms")
            
        elif key == ord('q'):  # Q pressed - quit
            break
        
        current_frame += 1
    
    cap.release()
    cv2.destroyAllWindows()
    
    if not timings:
        print("\nNo words were marked! Please try again and remember to press SPACE when words are spoken.")
        return
    
    # Create alignment file
    print("\nCreating alignment file...")
    with open(align_path, 'w') as f:
        # Initial silence
        f.write(f"0 {timings[0][0]} sil\n")
        
        # Write words and pauses
        for i in range(len(timings)):
            start_time = timings[i][0]
            word = timings[i][1]
            
            if i < len(timings) - 1:
                end_time = timings[i + 1][0]
                # Word
                f.write(f"{start_time} {end_time-200} {word}\n")
                # Short pause
                f.write(f"{end_time-200} {end_time} sp\n")
            else:
                # Last word
                end_time = min(start_time + 1000, duration_ms - 1000)
                f.write(f"{start_time} {end_time} {word}\n")
        
        # Final silence
        f.write(f"{end_time} {duration_ms} sil\n")
    
    print(f"\nAlignment file created at: {align_path}")
    print("\nAlignment contents:")
    with open(align_path, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    print("=== Video Alignment Creation Tool ===")
    video_name = input("Enter video name (default: aa011): ").strip() or "aa011"
    create_alignment_for_video(video_name)