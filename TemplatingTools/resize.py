from PIL import Image
import sys
import os

# set the image height/width in kilobytes
MAX_SIZE = 400

# set the file extensions
EXTENSIONS = ['.png', '.jpg', '.jpeg']


# resize an image
def resize(filepath):
    img = Image.open(filepath)
    img.thumbnail((MAX_SIZE, MAX_SIZE))
    img.save(filepath)


# main function
def main(filepaths):
    # if there is one filepath, check if it is a directory
    if (len(filepaths) == 1) and (os.path.isdir(filepaths[0])):
        # save the directory
        directory = filepaths[0]

        # make the files the images in the directory
        filepaths = []

        # check if the extension is in the filepath
        for file in os.listdir(directory):
            for extension in EXTENSIONS:
                if extension in file.lower():
                    filepaths.append(f"{directory}/{file}")

        print(f"Found files: {filepaths}")

    # resize each file
    for filepath in filepaths:
        resize(filepath)


if __name__ == '__main__':
    main(sys.argv[1:])
