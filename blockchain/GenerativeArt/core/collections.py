from core import FileHandler
from core import constants
import random
import shutil
import json
import sys
import os


class InfoHandler:
    def __init__(self, data_filepath, metadata_filepath):
        self.data_filepath = data_filepath
        self.metadata_filepath = metadata_filepath

    # copy each file to the export directory
    # change their names to prevent merge conflicts
    # we can assume that the directories exist, as they were created by the group merger
    # this can be asynchronous, as nothing depends on it
    def export_pair(self, index, export_directory):
        # get the files out of the filepaths
        _, data_file = os.path.split(self.data_filepath)
        _, metadata_file = os.path.split(self.metadata_filepath)

        # get the extension for the data file
        _, extension = os.path.splitext(data_file)

        # create the export filepaths (use the indexes, as we do not want export conflicts or overwrites)
        export_data_filepath = f"{export_directory}/{constants.FILE_FOLDER}/{index}{extension}"
        export_metadata_filepath = f"{export_directory}/{constants.METADATA_FOLDER}/{index}"

        # move each file
        shutil.copy(self.data_filepath, export_data_filepath)
        shutil.copy(self.metadata_filepath, export_metadata_filepath)

        return export_data_filepath, export_metadata_filepath


# create a class to merge groups of information
class GroupMerger(FileHandler):
    def __init__(self, export_directory, directories):
        self.directories = directories
        self.export_directory = export_directory

        # get all the files from each directory --> put them in info handlers
        self.info_handlers = []
        for directory in directories:
            # get the directory extension
            extension = self.get_directory_extension(directory)

            # if there is no extension, quit and signal such
            if not extension:
                print(f"No extensions could be found in {directory}")
                sys.exit()

            # get the file pairs
            self.info_handlers.extend(self.get_file_pairs(
                directory, extension))

        # make sure the export directory Exists
        self.check_export_directory()

    # function to get the file pairs
    def get_file_pairs(self, directory, extension):
        # store the pairs
        pairs = []

        # get the files
        files = os.listdir(f"{directory}/{constants.METADATA_FOLDER}")

        # check if the pairs exist for everything in metadata
        for file in files:
            pair = self.get_file_pair(directory, file, extension)

            # if there is a pair
            if pair:
                pairs.append(pair)
            else:
                print(f"No file found corresponding to metadata file: {file}")
        return pairs

    # function to check if a file pair exists
    def get_file_pair(self, directory, file, extension):
        data_file = f"{directory}/{constants.FILE_FOLDER}/{file}{extension}"
        metadata_file = f"{directory}/{constants.METADATA_FOLDER}/{file}"

        if not os.path.isfile(data_file):
            return None
        if not os.path.isfile(metadata_file):
            return None
        else:
            return InfoHandler(data_file, metadata_file)

    # function to export all
    # this SHOULD be multithreaded, but I haven't had the time to put it together yet, so it remains single-threaded
    def export_all(self):
        # shuffle the info handlers
        random.shuffle(self.info_handlers)

        # iterate over all the info handlers --> export pair
        for i in range(len(self.info_handlers)):
            # get the info handler --> have it export with the index to the export directory
            new_data_file, new_metadata_file = self.info_handlers[i].export_pair(
                i, self.export_directory)

            # change the name in the metadata
            self.rename(new_metadata_file)

    # create a way to rename the citizens in order (just going to point to the wrong index after creation)
    def rename(self, filepath):
        # read the data
        with open(filepath, 'r') as infile:
            data = json.loads(infile.read())

        # get the filename, which will correspond to the new name
        _, new_name = os.path.split(filepath)

        # change the name
        prefix = data['name'].split('#')[0]
        data['name'] = f"{prefix}#{new_name}"

        # rewrite the file
        with open(filepath, 'w') as outfile:
            outfile.write(json.dumps(data, indent=4))
