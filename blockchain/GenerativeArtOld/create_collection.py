from core.art import FileMerger
import sys
import os


def main(amount_to_create, config_filepath, new_collection_filepath):
    # get the config file and path
    source_path, config_file = os.path.split(config_filepath)

    # format the source path to actually work with windows
    source_path = source_path.replace('\\', '/')

    # create a FileMerger
    file_merger = FileMerger(source_path, new_collection_filepath, config_file)

    # check that we can actually create this many items
    if amount_to_create > file_merger.combinations:
        print(
            f"You cannot create {amount_to_create}, as there are only {file_merger.combinations} possible combinations with this data")
        sys.exit()

    for i in range(amount_to_create):
        file_merger.safe_merge(f"Avvenire Test Citizen #{i}", str(i))


if __name__ == '__main__':
    # run main with sys inputs
    main(int(sys.argv[1]), sys.argv[2], sys.argv[3])
