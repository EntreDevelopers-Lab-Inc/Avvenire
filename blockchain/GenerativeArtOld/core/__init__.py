from core import constants
import shutil
import os


# filehandler to handle some base functions
class FileHandler:
    # make the export directory
    def check_export_directory(self):
        # clear old export directory
        shutil.rmtree(self.export_directory)

        # get the directories
        file_directory = f"{self.export_directory}/{constants.FILE_FOLDER}"
        metadata_directory = f"{self.export_directory}/{constants.METADATA_FOLDER}"

        # make one for files and one for metadata
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)
            print(f"Created {file_directory} for file export")

        if not os.path.exists(metadata_directory):
            os.makedirs(metadata_directory)
            print(f"Created {metadata_directory} for metadata export")

    # make a function that gets the extension of the first file in a directory
    def get_directory_extension(self, directory):
        # get the folder
        folder = f"{directory}/{constants.FILE_FOLDER}"

        # get the files in the folder
        files = os.listdir(folder)

        # iterate over all the files
        for file in files:
            filepath = f"{folder}/{file}"
            # if the file is a real file, return it
            if os.path.isfile(filepath):
                _, extension = os.path.splitext(file)
                return extension

        # if it gets here, flag the output and mention that there are no files
        print(f"No files found in {directory}")
        return None
