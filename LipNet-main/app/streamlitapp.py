# Import all of the dependencies
import numpy as np
import streamlit as st
import os 
import imageio 
import tensorflow as tf 
from utils import load_data, num_to_char
from modelutil import load_model

# Set the layout to the streamlit app as wide 
st.set_page_config(layout='wide')

# Setup the sidebar
with st.sidebar: 
    st.image('https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png')
    st.title('LipBuddy')
    st.info('This application is originally developed from the LipNet deep learning model.')

st.title('LipNet Full Stack App') 

# Ensure data directory exists
data_dir = os.path.join('..', 'data', 's1')
if not os.path.exists(data_dir):
    st.error(f"Data directory not found: {data_dir}")
    st.info("Please make sure the data directory exists with video files")
    st.stop()

# Generating a list of options or videos 
options = os.listdir(data_dir)
if not options:
    st.error("No video files found in the data directory")
    st.info(f"Please add video files to: {data_dir}")
    st.stop()

selected_video = st.selectbox('Choose video', options)

# Generate two columns 
col1, col2 = st.columns(2)

if options: 
    # Rendering the video 
    with col1: 
        st.info('The video below displays the converted video in mp4 format')
        file_path = os.path.join('..', 'data', 's1', selected_video)
        
        # Check if ffmpeg command exists
        if os.system('ffmpeg -version') == 0:
            # Convert video to mp4 with proper settings
            os.system(f'ffmpeg -i "{file_path}" -vcodec libx264 -pix_fmt yuv420p -preset ultrafast test_video.mp4 -y')

            try:
                # Rendering inside of the app
                video = open('test_video.mp4', 'rb') 
                video_bytes = video.read() 
                st.video(video_bytes)
                video.close()
            except Exception as e:
                st.error(f"Error displaying video: {str(e)}")
        else:
            st.error("ffmpeg not found. Please install ffmpeg to convert videos.")

    with col2: 
        st.info('This is all the machine learning model sees when making a prediction')
        try:
            video, annotations = load_data(tf.convert_to_tensor(file_path))
            
            # Convert to numpy array and ensure correct format
            video_np = video.numpy()
            
            # Normalize to 0-255 range and convert to uint8
            video_np = ((video_np + 1) * 127.5).clip(0, 255).astype(np.uint8)
            
            # Ensure correct shape (frames, height, width)
            if video_np.shape[-1] == 1:
                video_np = np.squeeze(video_np, axis=-1)
                
            # Save as GIF with proper settings
            imageio.mimsave('animation.gif', video_np, fps=10)
            st.image('animation.gif', width=400) 

            st.info('This is the output of the machine learning model as tokens')
            try:
                model = load_model()
                
                # Prepare video for prediction
                video_for_prediction = tf.expand_dims(video, axis=0)
                
                # Get model prediction
                yhat = model.predict(video_for_prediction)
                
                # Decode the prediction
                decoder = tf.keras.backend.ctc_decode(yhat, input_length=tf.constant([75]), greedy=True)[0][0]
                
                # Convert numbers to characters
                converted_prediction = tf.strings.reduce_join(num_to_char(decoder)).numpy().decode('utf-8')
                
                # Display the prediction
                st.info('Decoded text from video:')
                st.text(converted_prediction)
                
                # Display original annotations for comparison
                st.info('Original annotations:')
                original_text = tf.strings.reduce_join(num_to_char(annotations)).numpy().decode('utf-8')
                st.text(original_text)
                
            except Exception as e:
                st.error(f"Error in model prediction: {str(e)}")
                
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
