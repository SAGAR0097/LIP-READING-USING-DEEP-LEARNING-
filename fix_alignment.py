import os

def fix_alignment_file(video_name="aa011"):
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    align_path = os.path.join(base_dir, 'data', 'alignments', 's1', f'{video_name}.align')
    
    # Read the current alignment
    with open(align_path, 'r') as f:
        lines = f.readlines()
    
    # Parse entries
    entries = []
    for line in lines:
        start, end, word = line.strip().split()
        if word != 'sp':  # Only keep non-'sp' entries
            entries.append((int(start), int(end), word))
    
    # Sort by start time
    entries.sort(key=lambda x: x[0])
    
    # Fix timing sequence
    fixed_entries = []
    for i, (start, end, word) in enumerate(entries):
        if i > 0:
            # Ensure start time is after previous end time
            prev_end = fixed_entries[-1][1]
            if start < prev_end:
                start = prev_end
        fixed_entries.append((start, end, word))
    
    # Write the fixed alignment
    with open(align_path, 'w') as f:
        for start, end, word in fixed_entries:
            f.write(f"{start} {end} {word}\n")
    
    print(f"Fixed alignment file written to: {align_path}")
    print("\nNew alignment contents:")
    with open(align_path, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    video_name = input("Enter video name (default: aa011): ").strip() or "aa011"
    fix_alignment_file(video_name) 