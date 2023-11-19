import pandas as pd
import traceback
import os
import keyboard

import lie_detection
from biosensor_streamer import BiosensorStreamer


class LieAnalyzer():
    def __init__(self):
        self.eeg_data = pd.DataFrame(columns=BiosensorStreamer.get_labels())
        self.streamer = BiosensorStreamer()
        self.analysis_result = ""

    def start_streaming(self):
        try:
            self.streamer.start_streaming()
            print("Press 'esc' to stop streaming...")

        except Exception as e:
            # Print out any other exceptions that might occur
            print(f"An error occurred: {e}\n")
            # Print the full stack trace using traceback
            traceback.print_exc()
            print("\n")

    def stop_streaming(self):
        self.streamer.stop_streaming()

    def append_data(self, print_data=False):
        while True:
            partial_eeg_data = self.streamer.read_data()
            if print_data:
                self.streamer.display_data(partial_eeg_data)
            self.eeg_data = pd.concat([self.eeg_data, partial_eeg_data], axis=0, ignore_index=True)

            if keyboard.is_pressed("esc"):
                self.write_as_csv_data(self.eeg_data, "data", "eeg_data.csv")
                break
        return

    def write_as_csv_data(self, dataframe, filedir, filename):
        if dataframe is None or dataframe.empty:
            return False
        # Create the data directory if it doesn't exist
        os.makedirs(filedir, exist_ok=True)
        # Path to the file in the data directory
        filepath = os.path.join(filedir, filename)
        # Write the data to the file
        dataframe.to_csv(filepath, index=False)
        return True


    def analyze(self):
        # write eeg_data into CSV file
        self.write_as_csv_data(self.eeg_data, "data", "temp_eeg.csv")
        # update analysis_result
        self.analysis_result = lie_detection.model("../data/temp_eeg.csv")
        # reset the eeg_data
        self.eeg_data = pd.DataFrame(columns=BiosensorStreamer.get_labels())
        return True