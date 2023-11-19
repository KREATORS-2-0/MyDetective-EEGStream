import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
# from pynput import keyboard
import keyboard
import sys

triggered = False

def read_data(csv_file):
    # Process the data by reading the file
    df = pd.read_csv(csv_file)
    return df

def filter(df):
    # remove noise by applying Fourier Transform and inverse it
    low_freq_threshold = 5
    high_freq_threshold = 50
    sampling_rate = 256

    for i in range(1, 5):
        column_name = f"EXG Channel {i}"

        freq_data = np.fft.fft(df[column_name])
        frequencies = np.fft.fftfreq(df[column_name].size, d=1/sampling_rate)
        
        mask = (frequencies > low_freq_threshold) & (frequencies < high_freq_threshold)
        freq_data[~mask] = 0
    
        filtered_data = np.fft.ifft(freq_data)

        df[column_name] = filtered_data.real

    return df 

def data_segmentation(df):
    # segmenting data and extract features
    response_indices = df.index[df['Response'] == 'yes'].tolist()    
    window_size = 256

    features = []
    labels = []

    for idx in response_indices:
        start_idx = max(idx - window_size, 0)
        end_idx = min(idx + window_size, len(df))

        # Segmenting data
        window_data = df.iloc[start_idx:end_idx, 0:4]  # Assuming EEG data is in the first 4 columns

        # Extract features from the window
        window_features = window_data.values.flatten()

        # If the window is smaller than the desired window size (at the edges of the dataset),
        # pad the feature vector with zeros
        if len(window_features) < 80:
            # Calculate how many zeros we need to add
            padding_size = 80 - len(window_features)
            # Create a padding array with zeros
            padding = np.zeros(padding_size)
            # Append the padding to the feature vector
            window_features = np.concatenate([window_features, padding])

        # Append the feature vector and the corresponding label to your lists
        features.append(window_features)
        labels.append(df.iloc[idx]['TrueFalse'])

    # Convert the lists to arrays for machine learning
    features = np.array(features)
    labels = np.array(labels)

    return features, labels

def training(csv_file):
    print("training..")
    raw_df = read_data(csv_file)
    df = filter(raw_df)
    features, labels = data_segmentation(df)
    # Splitting data into training and testing data sets
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save the fitted scaler to a file
    dump(scaler, '/Users/jamielee/Desktop/NatHacks/scaler.joblib')

    # Initialize the machine learning model
    model = RandomForestClassifier(random_state=42)

    # Train the model
    model.fit(X_train_scaled, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test_scaled)
    dump(model, '/Users/jamielee/Desktop/NatHacks/model.joblib')

    # Evaluate the model's performance
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")

def model(csv_file):
    df = read_data(csv_file)

    # Define your frequency thresholds
    low_freq_threshold = 5  # example value, set your own threshold
    high_freq_threshold = 50  # example value, set your own threshold
    sampling_rate = 256

    # Applying FT
    for i in range(1, 5):
        column_name = f"EXG Channel {i}"

        freq_data = np.fft.fft(df[column_name])

        # Get frequencies for all elements in freq_data
        frequencies = np.fft.fftfreq(df[column_name].size, d=1/sampling_rate)

        # Apply filter in frequency domain
        mask = (frequencies > low_freq_threshold) & (frequencies < high_freq_threshold)
        freq_data[~mask] = 0

        # Apply the inverse Fourier transform
        filtered_data = np.fft.ifft(freq_data)

        # Replace the original data with the filtered data in the same column
        df[column_name] = filtered_data.real

    data = df.iloc[:, 0:4]

    features = data.values.flatten()
    desired_length = 2048 # expected number of features

    if len(features) < desired_length:
        features = np.pad(features, (0, desired_length - len(features)), 'constant')
    elif len(features) > desired_length:
        features = features[:desired_length]

    features = features.reshape(1, -1)

    scaler = load('/Users/jamielee/Desktop/NatHacks/scaler.joblib')
    features_scaled = scaler.transform(features)

    model = load('/Users/jamielee/Desktop/NatHacks/model.joblib')
    prediction = model.predict(features_scaled)

    prediction_label = "Truth" if prediction[0] == 1 else "Lie"
    print(prediction_label)
    return prediction_label

def on_press(key):
    global triggered
    try:
        if key.char == 's':
            print("\nKey pressed. Starting the model")
            triggered = True
            return False
        
    except AttributeError:
        pass

# use this function to run the model
def run(csv_file):
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    # training('labeled_data.csv')
    
    if triggered:
        # if keyboard "s" is pressed, run the model
        model(csv_file)