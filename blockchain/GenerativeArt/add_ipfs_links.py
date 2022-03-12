import json
import sys
import os


def get_filepath(folder, file):
    return f"{folder}/{file}"


# create a main function that adds ipfs links to jsons (light formatting)
def main(folder, base_uri, extension):
    # clean the folder
    folder = os.path.abspath(folder)
    print(folder)

    # get all the items with the folder
    files = [f for f in os.listdir(
        folder) if os.path.isfile(get_filepath(folder, f))]
    print(f"Overwriting {len(files)} files")

    # iterate over all the json files
    for file in files:
        # get the filepath
        filepath = get_filepath(folder, file)

        # open each json file and read the data
        with open(filepath, 'r') as infile:
            data = json.loads(infile.read())

        # get the file id
        file_id = file.split('.')[0]

        # add the image link
        data['image'] = f"{base_uri}/{file_id}.{extension}"

        # save the json file
        with open(filepath, 'w') as outfile:
            outfile.write(json.dumps(data, indent=4))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
