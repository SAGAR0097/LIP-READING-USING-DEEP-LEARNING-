import os
import struct

def verify_mpg_file():
    print("\n=== MPG File Verification ===")
    
    # Get absolute path
    video_path = os.path.join(os.getcwd(), 'data', 's1', 'aa011.mpg')
    print(f"Checking file: {video_path}")
    
    if not os.path.exists(video_path):
        print("ERROR: File does not exist!")
        return
    
    # Check file size
    size = os.path.getsize(video_path)
    print(f"\nFile size: {size} bytes")
    
    try:
        with open(video_path, 'rb') as f:
            # Read first few bytes
            header = f.read(4)
            
            # Check for MPEG file signature
            if header.startswith(b'\x00\x00\x01\xBA'):
                print("Valid MPEG Program Stream detected")
            elif header.startswith(b'\x00\x00\x01\xB3'):
                print("Valid MPEG Sequence Header detected")
            else:
                print(f"Unknown format. First 4 bytes: {header.hex()}")
                
            # Read and show first 100 bytes for analysis
            f.seek(0)
            content = f.read(100)
            print("\nFirst 100 bytes of file:")
            print(content.hex())
            
    except Exception as e:
        print(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    verify_mpg_file()
    input("\nPress Enter to exit...")
