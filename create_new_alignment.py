import os

def create_new_alignment(video_name="aa011"):
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    align_path = os.path.join(base_dir, 'data', 'alignments', 's1', f'{video_name}.align')
    
    # Create new alignment with proper timing
    alignment_content = """0 333 sil
333 866 32am
866 1700 saturday
1700 2566 august,27
2566 3000 sil"""
    
    # Write the new alignment
    with open(align_path, 'w') as f:
        f.write(alignment_content)
    
    print(f"New alignment file written to: {align_path}")
    print("\nAlignment contents:")
    print(alignment_content)

if __name__ == "__main__":
    video_name = input("Enter video name (default: aa011): ").strip() or "aa011"
    create_new_alignment(video_name) 