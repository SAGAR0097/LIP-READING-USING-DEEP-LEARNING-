import tensorflow as tf
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from app directory
from app.utils import load_data, num_to_char, char_to_num
from app.modelutil import load_model
import numpy as np

def debug_video_processing(video_path):
    print(f"\nDebugging video processing for: {video_path}")
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return
    
    # Check if alignment file exists
    alignment_path = os.path.join('data', 'alignments', 's1', 'aa011.align')
    if not os.path.exists(alignment_path):
        print(f"Error: Alignment file not found at {alignment_path}")
        return
    
    print("\nLoading data...")
    try:
        # Convert path to tensor
        path_tensor = tf.convert_to_tensor(video_path)
        
        # Load video and alignments
        video, annotations = load_data(path_tensor)
        
        print("\nVideo data shape:", video.shape)
        print("Annotations shape:", annotations.shape)
        
        # Try to decode annotations
        try:
            decoded_annotations = tf.strings.reduce_join(num_to_char(annotations)).numpy().decode('utf-8')
            print("\nDecoded annotations:", decoded_annotations)
            
            # Print raw annotation indices
            print("\nRaw annotation indices:", annotations.numpy())
            
            # Print character mapping for annotations
            print("\nCharacter mapping for annotations:")
            for idx in annotations.numpy():
                if idx != 0:  # Skip padding
                    char = num_to_char(tf.constant([idx])).numpy()[0].decode('utf-8')
                    print(f"Index {idx} -> '{char}'")
        except Exception as e:
            print("Error decoding annotations:", str(e))
        
        # Try model prediction
        print("\nLoading model...")
        model = load_model()
        
        # Prepare video for prediction
        video_for_prediction = tf.expand_dims(video, axis=0)
        print("Input shape for prediction:", video_for_prediction.shape)
        
        # Get prediction
        print("\nMaking prediction...")
        yhat = model.predict(video_for_prediction, verbose=0)
        print("Prediction shape:", yhat.shape)
        
        # Print prediction probabilities for first 3 frames
        print("\nPrediction probabilities for first 3 frames:")
        for frame_idx in range(3):
            print(f"\nFrame {frame_idx + 1}:")
            frame_probs = yhat[0, frame_idx, :]
            top_indices = tf.math.top_k(frame_probs, k=5).indices.numpy()
            for idx in top_indices:
                char = num_to_char(tf.constant([idx])).numpy()[0].decode('utf-8')
                prob = frame_probs[idx].numpy()
                print(f"Character: {char}, Probability: {prob:.4f}")
        
        # Decode prediction with CTC
        print("\nCTC Decoding process:")
        input_length = tf.ones(yhat.shape[0]) * yhat.shape[1]
        
        # Get raw CTC output
        ctc_output = tf.keras.backend.ctc_decode(yhat, input_length, greedy=True)
        decoder = ctc_output[0][0].numpy()
        log_probs = ctc_output[1].numpy()
        
        print("CTC log probabilities:", log_probs)
        
        # Convert numbers to characters
        converted_prediction = tf.strings.reduce_join(num_to_char(decoder)).numpy().decode('utf-8')
        print("\nPredicted text:", converted_prediction)
        
        # Print raw prediction values for debugging
        print("\nRaw prediction values (first 20):", decoder[0][:20])
        print("Unique values in prediction:", np.unique(decoder[0]))
        
        # Print the actual text from alignment file
        print("\nActual text from alignment file:")
        with open(alignment_path, 'r') as f:
            lines = f.readlines()
        actual_text = ' '.join([line.split()[2] for line in lines if line.split()[2] != 'sil'])
        print(actual_text)
        
        # Compare prediction with actual text
        print("\nComparison:")
        print("Actual text:", actual_text)
        print("Predicted text:", converted_prediction)
        print("Decoded annotations:", decoded_annotations)
        
        # Print character-by-character comparison
        print("\nCharacter-by-character comparison:")
        actual_chars = list(actual_text.replace(" ", ""))
        pred_chars = list(converted_prediction.replace(" ", ""))
        
        print("Actual characters:", actual_chars)
        print("Predicted characters:", pred_chars)
        
        # Print vocabulary for reference
        print("\nModel vocabulary:")
        vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]
        print("".join(vocab))
        
    except Exception as e:
        print("Error during processing:", str(e))

if __name__ == "__main__":
    # Use absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try both .mp4 and .mpeg extensions
    video_path_mp4 = os.path.join(base_dir, 'data', 's1', 'aa011.mp4')
    video_path_mpeg = os.path.join(base_dir, 'data', 's1', 'aa011.mpeg')
    
    # Check which file exists
    if os.path.exists(video_path_mp4):
        video_path = video_path_mp4
    elif os.path.exists(video_path_mpeg):
        video_path = video_path_mpeg
    else:
        print(f"Error: Video file not found at either {video_path_mp4} or {video_path_mpeg}")
        exit(1)
        
    print(f"Video path: {video_path}")
    print(f"Video exists: {os.path.exists(video_path)}")
    debug_video_processing(video_path) 