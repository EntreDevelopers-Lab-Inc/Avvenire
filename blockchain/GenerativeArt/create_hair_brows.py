from tools import FileMerger
import sys
import os


HAIR_FOLDER = 'HAIR'
BROWS_FOLDER = 'BROWS'


def main(config_filepath, new_collection_filepath):
    # get the config file and path
    source_path, config_file = os.path.split(config_filepath)

    # format the source path to actually work with windows
    source_path = source_path.replace('\\', '/')

    # create a FileMerger
    file_merger = FileMerger(source_path, new_collection_filepath, config_file)

    # there are 2 trait groups: hair, and brows, which need to be combined in order (01 --> 01, 02 --> 02, etc.)
    hair_group = file_merger.trait_groups[HAIR_FOLDER]
    brows_group = file_merger.trait_groups[BROWS_FOLDER]
    for i in range(len(hair_group)):
        # create the grouping
        grouping = [brows_group.traits[i], hair_group.traits[i]]

        # export the grouping
        file_merger.export_art(
            f"HairBrows #{i}", str(i), grouping)


if __name__ == '__main__':
    # run main with sys inputs
    main(sys.argv[1], sys.argv[2])
