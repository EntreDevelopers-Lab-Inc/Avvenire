from core.collections import GroupMerger
import sys


def main(export_directory, directories):
    # create a group merger from the export directory and directories
    merger = GroupMerger(export_directory, directories)

    # export all
    merger.export_all()

    # rename all the exports


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
