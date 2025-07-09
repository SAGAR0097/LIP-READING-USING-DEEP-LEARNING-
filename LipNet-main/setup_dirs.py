import os
import shutil

def setup_project():
    print("=== Setting up LipNet Project Structure ===")
    
    # Get the current directory
    base_dir = os.getcwd()
    print(f"Current directory: {base_dir}")
    
    # Define source and destination paths
    source_video = r"C:\Users\amubh\Desktop\PROJECT\MPROJECT\CODE\LipNet-main\data\s1\aa011.mpg"
    
    # Create required directories
    dirs_to_create = [
        os.path.join(base_dir, 'data', 's1'),
        os.path.join(base_dir, 'data', 'alignments', 's1')
    ]
    
    # Create directories
    print("\nCreating directories...")
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created: {dir_path}")
    
    # Copy video file
    dest_video = os.path.join(base_dir, 'data', 's1', 'aa011.mpg')
    print(f"\nCopying video file...")
    print(f"From: {source_video}")
    print(f"To: {dest_video}")
    
    try:
        shutil.copy2(source_video, dest_video)
        print("Video file copied successfully!")
    except Exception as e:
        print(f"Error copying video: {str(e)}")
    
    # Verify setup
    print("\nVerifying setup...")
    if os.path.exists(dest_video):
        print(f"✓ Video file exists at: {dest_video}")
        print(f"✓ Video file size: {os.path.getsize(dest_video)} bytes")
    else:
        print("✗ Video file not found in destination")

if __name__ == "__main__":
    setup_project()
    input("\nPress Enter to continue...")
