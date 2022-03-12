from core import constants
from core import FileHandler
from PIL import Image
import pandas as pd
import random
import json
import os


# a class for one piece of art (good for storing data, as you can pass an entire trait into it)
class Art:
    def __init__(self, trait_dict):
        # keep all the trait dicts in a list (starting with the one passed)
        self.traits = [trait_dict]

        # open the full path
        self.image = Image.open(trait_dict['full_path'])
        print(f"Opened {trait_dict}")

    # paste a new trait dict onto the existing traits
    def paste(self, new_trait_dict):
        # append the trait dict to the list
        self.traits.append(new_trait_dict)

        # paste the new trait on the base
        new_image = Image.open(new_trait_dict['full_path'])
        self.image.paste(new_image, (0, 0), new_image)

    # export the data
    def export(self, art_name, folder, filename, art_extension, extra_traits=[]):
        # make a filepath
        filepath = f"{folder}/{constants.FILE_FOLDER}/{filename}.{art_extension}"

        # save the image
        self.image.save(filepath)

        # get the metadata
        art_metadata = self.metadata

        # set the art name of the metadata
        art_metadata['name'] = art_name

        # extend the traits to include the extra traits
        art_metadata['attributes'] = extra_traits + art_metadata['attributes']

        # export the metadata
        with open(f"{folder}/{constants.METADATA_FOLDER}/{filename}", 'w') as outfile:
            outfile.write(json.dumps(art_metadata, indent=4))

    # function to create trait metadata
    def create_trait_metadata(self, trait):
        trait_metadata = {
            'trait_type': trait['trait_type'],
            'value': trait['trait_name']
        }

        return trait_metadata

    # function to create trait files
    def create_trait_filedata(self, trait):
        trait_filedata = {
            'trait_type': trait['trait_type'],
            'file': f"{trait['trait_type']}/{trait['file']}"
        }

        return trait_filedata

    # export all the trait's information (in opensea format)
    @property
    def metadata(self):
        metadata_dict = {
            "name": "",
            "image": "",
            # create from the trait data
            "attributes": [self.create_trait_metadata(trait) for trait in self.traits],
            # backwards link it for reproducability, also would be cool to link these to IPFS
            "trait_files": [self.create_trait_filedata(trait) for trait in self.traits]
        }

        return metadata_dict


# class for handling a bunch of traits
class TraitGroupHandler:
    def __init__(self, directory, trait_group):
        # save the directory name
        self.directory = f"{directory}/{trait_group['folder']}"

        # use the directory to make a trait type (title case)
        self.trait_type = os.path.basename(trait_group['folder']).title()

        # open the trait csv
        df = pd.read_csv(f"{self.directory}/{trait_group['csv']}")

        # add a column called full_path mapping the file and directory
        df['full_path'] = [
            f"{self.directory}/{row['file']}" for index, row in df.iterrows()]

        # add the trait type for all the traits
        df['trait_type'] = [
            self.trait_type for index, row in df.iterrows()]

        # store the default trait
        self.default_trait = df[df['file'] == trait_group['default']].head(
            1).to_dict(orient='records')[0]

        # remove the default from the traits
        df = df[df['file'] != trait_group['default']]

        # store the default probability
        self.default_probability = trait_group['default_probability']

        # store the traits for later access
        self.traits = df.to_dict(orient='records')

    # make a way to get a random trait
    def random_trait(self):
        if random.random() < self.default_probability:
            # get the default if it is under the probability
            trait_choice = self.default_trait
        else:
            # random otherwise
            trait_choice = random.choice(self.traits)

        return trait_choice

    # get the length
    def __len__(self):
        return len(self.traits)


# class to handle merging jpegs into art
class FileMerger(FileHandler):
    def __init__(self, directory, export_directory, config_file='config.json'):
        # save the directories
        self.directory = directory
        self.export_directory = export_directory

        # check to make sure that the export directory exists
        self.check_export_directory()

        # load the config
        with open(f"{directory}/{config_file}", 'r') as infile:
            self.config = json.loads(infile.read())

        # make trait groups
        self.trait_groups = {trait_group['folder']: TraitGroupHandler(
            self.directory, trait_group) for trait_group in self.config['trait_groups']}

        # get the number of combinations for later use
        self.combinations = self.get_combinations()

        # make a set to track pieces of art that have been created (ensures uniqueness)
        self.art_created = set()

    # merge all of the files on top of each other --> creates one piece of art
    def merge(self):
        # get the order from the config's trait folders (in order already)
        order = [group['folder'] for group in self.config['trait_groups']]

        traits_to_merge = []

        # iterate over the order
        for folder in order:
            trait_group = self.trait_groups[folder]

            # get a random trait
            traits_to_merge.append(trait_group.random_trait())

        return traits_to_merge

    # safe merge attempts to create an order for every combination in the merger
    # str: art_name, str: filename (which should have NO extension, for parallel json and art files), list: order (folders to merge from in order)
    def safe_merge(self, art_name, filename):
        # set unique to false to ensure that the art being created is unique
        unique = False

        # iterate for all combinations
        for i in range(self.combinations):
            # use a list to put together all the files to merge
            traits_to_merge = self.merge()

            # check if some art with this combination has been created yet --> flatten the files into one string --> check the art created set
            new_combo = self.flatten_filenames(
                [trait['full_path'] for trait in traits_to_merge])

            if not (new_combo in self.art_created):
                # the new combination is unique!
                unique = True

                # save the art, so we don't create anything like it
                self.art_created.add(new_combo)

                # break the loop
                break

        # if unique is false, return none
        if not unique:
            return None

        # export the art
        self.export_art(art_name, filename, traits_to_merge)

    # export art function
    def export_art(self, art_name, filename, traits_to_merge):
        # make the base art with the first trait
        art = Art(traits_to_merge[0])

        # iterate over the traits to merge and export the generative art
        for trait in traits_to_merge[1:]:
            # paste the next trait on top of the existing art
            art.paste(trait)
            print(f"pasted {trait}")

        # export the art
        extension = self.config['export_extension']
        art.export(art_name, self.export_directory, filename,
                   extension, extra_traits=self.config['extra_traits'])

    # a way to get unique names from a list of files
    def flatten_filenames(self, filenames):
        # sort the filenames and then join them (need to account for a case when a user merges in different orders)
        return ' '.join(sorted(filenames))

    # make a property to calculate the number of combinationations
    def get_combinations(self):
        combination_count = 1

        # iterate over the group and multiply the new combinations
        for group in self.trait_groups:
            combination_count *= len(group)

        return combination_count
