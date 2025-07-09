import streamlit as st
import os

st.title('Test Streamlit App')

# Get current directory
current_dir = os.getcwd()
st.write(f"Current directory: {current_dir}")

# List files in current directory
st.write("Files in current directory:")
files = os.listdir(current_dir)
st.write(files)

# Test video display
st.title('Test Video Display')

# Try different possible paths
possible_paths = [
    os.path.join('data', 's1', 'aa011.mpg'),
    os.path.join(current_dir, 'data', 's1', 'aa011.mpg'),
    os.path.join('..', 'data', 's1', 'aa011.mpg'),
    os.path.join(current_dir, '..', 'data', 's1', 'aa011.mpg')
]

st.write("Checking possible video paths:")
for path in possible_paths:
    exists = os.path.exists(path)
    st.write(f"Path: {path}")
    st.write(f"Exists: {exists}")
    if exists:
        st.write(f"File size: {os.path.getsize(path)} bytes")
        try:
            st.video(path)
            st.success(f"Successfully loaded video from: {path}")
        except Exception as e:
            st.error(f"Error displaying video: {str(e)}")
    else:
        st.error(f"Video not found at: {path}") 