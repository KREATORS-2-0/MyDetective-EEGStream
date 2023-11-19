'''
Not needed when streaming data, but useful when obtaining training data for labelling
'''


import os


class FileIO:
    default_dir = ""
    default_filename = ""
    file_type = ""

    def __init__(self, default_default_dir=os.path.join("..", "data"), default_filename="default_name.csv"):
        self.default_dir = default_default_dir
        self.default_filename = default_filename
        self.file_type = self.get_substring_after_last_period(default_filename)

    '''
    def save_data(self, dataframe, filename=None):
        if filename is None:
            filename = self.default_filename

        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, self.default_dir)
        file_path = os.path.join(data_path, filename)

        if os.path.exists(file_path):
            print(f"\nA file named {filename} already exists in the data directory.\n")
            print("Select an option:")
            print("\t1. Append data to the existing file. Type (a/append).")
            print("\t2. Save data in a new file. Type (n/new/new_file).")
            print("\t3. Overwrite the existing file. Type (o/overwrite).")
            print("\t4. Delete current data frame. Type(d/delete).")
            print("\n")
            option = input("\nEnter your option: ")
            print("\n")

            if option.lower() in ['a', 'append']:
                try:
                    dataframe.to_csv(file_path, mode='a', header=False, index=False)
                    print(f"Data appended at: {os.path.abspath(file_path)}")
                except Exception as e:
                    print(f"Data append error occurred: {e}")
                    return
            elif option.lower() in ['n', 'new', 'new_file']:
                new_filename = input("Enter the new filename: ")
                new_data_path = os.path.join(data_path, new_filename)
                try:
                    dataframe.to_csv(new_data_path, index=False)
                    print(f"Data saved at: {os.path.abspath(new_data_path)}")
                except Exception as e:
                    print(f"Data save error occurred: {e}")
                    return
            elif option.lower() in ['o', 'overwrite']:
                try:
                    dataframe.to_csv(file_path, index=False)
                    print(f"Data overwritten at: {os.path.abspath(file_path)}")
                except Exception as e:
                    print(f"Data overwrite error occurred: {e}")
                    return
            elif option.lower() in ['d', 'delete']:
                print("Data not saved.")
                return
            else:
                print("Invalid option. Data not saved.")
                return self.save_data(dataframe, filename)
        else:
            # Save the data in a new file if the file does not exist
            try:
                dataframe.to_csv(file_path, index=False)
                print(f"Data saved at: {os.path.abspath(file_path)}")
            except Exception as e:
                print(f"Data save error occurred: {e}")
                return
    '''


    def write_data(self, dataframe, filedir=None, filename=None):
        if filedir == None:
            filedir = self.default_dir
        if filename == None:
            filename = self.default_filename

        if self.file_type.lower() == "csv":
            self.write_csv_data(dataframe, filedir, filename)
        elif self.file_type.lower() == "json":
            self.write_json_data(dataframe, filedir, filename)
        else:
            return False


    def write_csv_data(self, dataframe, filedir, filename):
        if dataframe is None or dataframe.empty:
            return False

        # Create the data directory if it doesn't exist
        os.makedirs(filedir, exist_ok=True)
        # Path to the file in the data directory
        filepath = os.path.join(filedir, filename)
        # Write the data to the file
        dataframe.to_csv(filepath, index=False)
        return True


    def write_json_data(self, dataframe, filedir, filename):
        if dataframe is None or dataframe.empty:
            return False
    
        # convert to json format
        json_data = dataframe.to_json(orient='records', lines=True)
        json_data = json_data.strip("[]")

        # Create the data directory if it doesn't exist
        os.makedirs(filedir, exist_ok=True)
        # Path to the file in the data directory
        filepath = os.path.join(filedir, filename)
        # Write the data to the file
        with open(filepath, 'w') as f:
            f.write(json_data)
        return True


    @staticmethod
    def get_substring_after_last_period(input_string):
        # Find the index of the last period
        last_period_index = input_string.rfind('.')

        # Check if a period was found
        if last_period_index != -1:
            # Extract the substring after the last period
            substring = input_string[last_period_index + 1:]

            return substring
        else:
            # If no period is found, return the original string
            return input_string
