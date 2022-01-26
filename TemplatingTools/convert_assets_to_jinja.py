from Jinjafy import FileConverter
import sys

ATTRIBUTES = [('link', 'href'), ('img', 'src'), ('script', 'src')]


def convert(filepath):
    # make a converter
    converter = FileConverter(filepath)

    # convert it
    for tag_name, attribute_name in ATTRIBUTES:
        converter.change_attributes(tag_name, attribute_name)


if __name__ == '__main__':
    filepath = sys.argv[1].strip().replace('\\', '')

    convert(filepath)
