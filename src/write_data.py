import keyboard
import traceback
import os

from eeg_streamer import EEGStreamer


def escape_function():
    return keyboard.is_pressed("esc")


def main():
    sampling_rate = 1
    streaming_dir = "data"
    streaming_file = "results.json"

    streamer = EEGStreamer(sampling_rate=sampling_rate)

    try:
        streamer.start_streaming()
        print("Press 'esc' to stop streaming...")

        while not escape_function():

            # get data periodically (pandas dataframe)
            new_data = streamer.read_data()

            # convert to json format
            if new_data is not None and not new_data.empty:
                json_data = new_data.to_json(orient='records', lines=True)
                json_data = json_data.strip("[]")

            # Create the data directory if it doesn't exist
            os.makedirs(streaming_dir, exist_ok=True)

            # Path to the file in the data directory
            file_path = os.path.join(streaming_dir, streaming_file)

            # Save the data to the file
            with open(file_path, 'w') as f:
                f.write(json_data)

    except KeyboardInterrupt:
        print("\nKeyboard interrupted.")
        print("Program terminated by user.\n")

    except Exception as e:
        # Print out any other exceptions that might occur
        print(f"An error occurred: {e}\n")
        # Print the full stack trace using traceback
        traceback.print_exc()
        print("\n")

    finally:
        streamer.stop_streaming()
        return


main()
