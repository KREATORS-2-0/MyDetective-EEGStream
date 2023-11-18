import time
import numpy as np
import pandas as pd

import serial.tools.list_ports
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class EEGStreamer:
    columns = ['EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3', 'EXG Channel 4', 'Timestamp']

    def __init__(self, manual_input_com_port='COM3', sampling_rate=0.001):  # 1 milliseconds
        self.params = BrainFlowInputParams()

        # Search for COM port
        self.com_port = self.find_com_port()
        if not self.com_port:
            self.com_port = manual_input_com_port
            print('Ganglion board not found.')
            print(f'Trying to use {manual_input_com_port}.\n')
        else:
            print('Successfully connected to the board.\n')

        self.sampling_rate = sampling_rate
        self.params.serial_port = self.com_port
        self.board_id = BoardIds.GANGLION_BOARD.value
        self.board = BoardShim(self.board_id, self.params)

    def find_com_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            # Check if the VID:PID in the HWID matches that of the Ganglion board
            if 'VID:PID=2458:0001' in port.hwid:
                print(f"Found board at {port.device}")
                return port.device
        return None  # No Ganglion board found

    def start_streaming(self):
        BoardShim.enable_dev_board_logger()
        self.board.prepare_session()
        self.board.start_stream(45000)
        print('Streaming data from the Ganglion board...')


    def read_data(self):
        try:
            time.sleep(self.sampling_rate)
            data = self.board.get_board_data()
            
            if data.size == 0:
                return None  # No new data was found
            
            eeg_channels = BoardShim.get_eeg_channels(self.board_id)
            time_channel = BoardShim.get_timestamp_channel(self.board_id)

            eeg_data = data[eeg_channels]  # 2d-array, var goes right
            time_data = data[time_channel]  # 1d-array, var goes down

            # print("Shape of eeg_data:", eeg_data.shape)
            # print("Shape of time_data:", time_data.shape)

            # 1d-array to 2d-array, var goes right
            time_data = np.reshape(time_data, (1, len(time_data)))

            # print("Shape of time_data:", time_data.shape)

            # print("Shape of eeg_data.T:", eeg_data.T.shape)
            # print("Shape of time_data.T:", time_data.T.shape)

            # raise error if data rate does not match
            if len(eeg_data.T) != len(time_data.T):
                raise Exception("EEG_data and time_data are not synced.")

            # combine data and turn into pandas dataframe
            new_data = np.concatenate((eeg_data.T, time_data.T), axis=1)
            new_df = pd.DataFrame(new_data, columns=self.columns)

            # print(new_df)
            return new_df

        except Exception as e:
            print('EEG data reading error: ', e)
            return None

    def stop_streaming(self):
        if self.board.is_prepared():
            print('Stopping the stream and releasing session...')
            self.board.stop_stream()
            self.board.release_session()