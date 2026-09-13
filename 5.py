import os
import librosa

def get_audio_duration(file_path):
    try:
        # Load the audio file with librosa
        audio_data, sample_rate = librosa.load(file_path, sr=None)

        # Calculate the duration of the audio in seconds
        duration_seconds = librosa.get_duration(y=audio_data, sr=sample_rate)

        # Convert the duration from seconds to hours, minutes, and remaining seconds
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)

        return hours, minutes, seconds
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def get_audio_durations_in_directory(directory_path):
    audio_durations = {}  # Dictionary to store durations of each audio file
    # Iterate over all files in the specified directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if file_path.endswith('.flac'):  # assuming audio files are in FLAC format
            # Get duration of each audio file
            duration = get_audio_duration(file_path)
            if duration is not None:
                hours, minutes, seconds = duration
                # Store only the filename (without extension) in the dictionary
                audio_durations[os.path.splitext(filename)[0]] = f"{hours}:{minutes:02}:{seconds:02}"

    return audio_durations

# Specify the directory containing your audio files
directory_path = r'insert_directory_path_here'

# Get durations of FLAC audio files in the specified directory
audio_durations = get_audio_durations_in_directory(directory_path)

# Print the durations at the end
print("Audio Durations:")
for filename, duration in audio_durations.items():
    print(f"{filename}: {duration}")