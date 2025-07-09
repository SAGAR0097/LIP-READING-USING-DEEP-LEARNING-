# Import all of the dependencies\
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
    st.info('This application is  developed by the SAGAR SINGH,SHUBHAM KUSHWAHA,RITESH MISHRA UNDER THE SUPERVISION OF DR.RAVI PRAKASH VERAMA.')

st.title('LipNet Full Stack App') 

# Get the base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Generating a list of options or videos 
video_dir = os.path.join(base_dir, 'data', 's1')
options = os.listdir(video_dir)
selected_video = st.selectbox('Choose video', options)

# Generate two columns 
col1, col2 = st.columns(2)

if options: 
    try:
        # Rendering the video 
        with col1: 
            st.info('The video below displays and the format is mpeg')
            file_path = os.path.join(video_dir, selected_video)
            
            # Convert video to mp4 with proper settings
            os.system(f'ffmpeg -i {file_path} -vcodec libx264 -pix_fmt yuv420p -preset ultrafast test_video.mp4 -y')

            # Rendering inside of the app
            video = open('test_video.mp4', 'rb') 
            video_bytes = video.read() 
            st.video(video_bytes)

        with col2: 
            st.info('This is all the machine learning model sees when making a prediction')
            
            # Load and process video
            try:
                video, annotations = load_data(tf.convert_to_tensor(file_path))
                st.write(f"Video shape: {video.shape}")
                st.write(f"Annotations shape: {annotations.shape}")
                
                # Convert to numpy array and ensure correct format
                video_np = video.numpy()
                
                # Normalize to 0-255 range and convert to uint8
                video_np = ((video_np + 1) * 127.5).clip(0, 255).astype(np.uint8)
                
                # Ensure correct shape (frames, height, width)
                if video_np.shape[-1] == 1:
                    video_np = np.squeeze(video_np, axis=-1)
                    
                # Save as GIF with proper settings
                imageio.mimsave('animation.gif', video_np, fps=10, quality=100)
                st.image('animation.gif', width=400) 

                st.info('This is the output of the machine learning model as tokens')
                
                # Load model and make prediction
                try:
                    model = load_model()
                    
                    # Prepare video for prediction
                    video_for_prediction = tf.expand_dims(video, axis=0)
                    st.write(f"Input shape for prediction: {video_for_prediction.shape}")
                    
                    # Verify input shape
                    expected_shape = (None, 75, 46, 140, 1)
                    if video_for_prediction.shape[1:] != expected_shape[1:]:
                        st.error(f"Input shape mismatch! Expected {expected_shape[1:]}, got {video_for_prediction.shape[1:]}")
                        # Try to fix the shape
                        if video_for_prediction.shape[1] > 75:
                            video_for_prediction = video_for_prediction[:, :75, :, :, :]
                            st.write(f"Adjusted shape: {video_for_prediction.shape}")
                    
                    # Get model prediction
                    yhat = model.predict(video_for_prediction, verbose=0)
                    st.write(f"Prediction shape: {yhat.shape}")
                    
                    # Decode the prediction
                    input_length = tf.ones(yhat.shape[0]) * yhat.shape[1]
                    decoder = tf.keras.backend.ctc_decode(yhat, input_length, greedy=True)[0][0].numpy()
                    
                    # Convert numbers to characters
                    converted_prediction = tf.strings.reduce_join(num_to_char(decoder)).numpy().decode('utf-8')
                    
                    # Display the prediction
                    st.info('Parser text:')
                    st.text(converted_prediction)
                    
                    # Display raw tokens for debugging
                    st.info('Raw tokens:')
                    st.text(decoder)
                    
                    # Display text from video
                    st.info('Decoded Text from video:')
                    original_text = tf.strings.reduce_join(num_to_char(annotations)).numpy().decode('utf-8')
                    st.text(original_text)
                    
                except Exception as e:
                    st.error(f"Error during model prediction: {str(e)}")
                    st.error(f"Error type: {type(e)}")
                    import traceback
                    st.error(f"Traceback: {traceback.format_exc()}")
                    
            except Exception as e:
                st.error(f"Error during video processing: {str(e)}")
                
    except Exception as e:
        st.error(f"Error during video loading: {str(e)}")
