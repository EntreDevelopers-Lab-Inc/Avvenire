import requests
import json
import os

# import modules selectively to see if you are in test or production mode
try:
    from blockchain.scripts.helpful_scripts import get_server_account
    from blockchain.constants import BASE_URI, EXTENSION
    from blockchain.GenerativeArt.core.art import Art
    from blockchain.tools.ipfs import upload_to_ipfs

except ImportError:
    from scripts.helpful_scripts import get_server_account
    from constants import BASE_URI, EXTENSION
    from GenerativeArt.core.art import Art
    from tools.ipfs import upload_to_ipfs

# create a trait order
TRAIT_ORDER = ['Background', 'Body', 'Tattoo', 'Eyes', 'Mouth',
               'Mask', 'Necklace', 'Clothing', 'Earrings', 'Hair', 'Effect']

# create the sex order
SEX_ORDER = ['Male', 'Female']

# set the default
DEFAULT_FILE = f"DEFAULT.{EXTENSION}"

# set the folder with the art
ART_FOLDER = f"{os.getcwd()}GenerativeArt"


# make a class that can create citizens by comparing ipfs to on-chain data
class CitizenCreator:
    def __init__(self, ipfs_data, chain_data, sex):
        # save each group of traits
        self.ipfs_data = ipfs_data

        # save the overall on-chain data
        self.chain_data = chain_data

        # convert the on-chain data into files
        self.chain_traits = self.extract_data_for_traits(chain_data)

        # store the sex, so you can use the right file
        self.sex = sex

        # will need the metadata for later
        self.metadata = self.get_metadata()

    # create a function that converts traits to files
    # only going to get a list of data off the chain --> need to convert it somehow
    def extract_data_for_traits(self, chain_data):
        # create a list for the files
        data = []

        # iterate over all the traits
        for i in range(len(TRAIT_ORDER)):
            # create a file from the integer --> some trait & first item in trait struct list --> get the tokenId
            trait_file = self.extract_data_for_trait(chain_data[i])

            # cannot have incomplete build
            if not trait_file:
                return None

            # add the trait file to the list of files
            data.append(trait_file)

        # return the files
        return data

    # a function for getting a file from an ipfs trait uri
    def extract_data_for_trait(self, trait):
        # if there is a uri, get the info from there
        if trait[1]:
            # get the trait data from ipfs
            try:
                data = requests.get(trait[1]).json()
            except requests.exceptions.JSONDecodeError:
                print(f"No trait data found at {trait[1]}")
                return None

            return data
        # if there is not a uri, it can't exist (only traits with no change requested can be merged)
        elif trait[3]:
            # if it exists, just return a dictionary of unknown, as it will not be used
            return {'name': 'unknown', 'file': 'unknown', 'attributes': {'trait_type': 'unknown', 'value': 'unknown'}}
        # if no uri, and it doesn't exist, set it to the default
        else:
            # get what type of trait it is
            trait_type = TRAIT_ORDER[trait[5] - 1]

            # imply the file default information based on the trait type and sex
            return create_trait(trait_type, f"{trait_type}/{DEFAULT_FILE}", trait_type)

    # create a way to get the metadata
    def get_metadata(self):
        # make sure that we have chain traits
        if not self.chain_traits:
            return None

        # create a file list
        files = []

        # create an attribute list (start with the sex data)
        attributes = [{'trait_type': 'Sex', 'value': self.sex}]

        # iterate over all of the files in both trait lists
        for i in range(len(TRAIT_ORDER)):
            # get the ipfs file
            ipfs_file = self.ipfs_data['trait_files'][i]['file']
            ipfs_attribute = self.ipfs_data['attributes'][i]

            # get the chain file
            chain_file = self.chain_traits[i]['file']
            chain_attribute = self.chain_traits['name']

            # figure out if the new trait exists
            new_trait_exists = self.chain_data[i][3]

            # if the ipfs trait and the chain trait are the same, just use that file
            if ipfs_file == chain_file:
                # set the file and attribute
                new_file = ipfs_file
                new_attribute = ipfs_attribute
            # if the ipfs file is a default and the new one exists, use the chain trait
            elif (ipfs_file == DEFAULT_FILE) and (new_trait_exists):
                # set the file and attribute
                new_file = chain_file
                new_attribute = chain_attribute
            # if the ipfs file is NOT a default, and the new one does not exist, the trait has been removed, add the chain trait
            elif (ipfs_file != DEFAULT_FILE) and (not new_trait_exists):
                # set the new trait to the default, which is the the current chain trait
                # set the file and attribute
                new_file = chain_file
                new_attribute = chain_attribute
            # if the ipfs trait is not the same as the chain trait, the traits have been swapped
            else:
                # set the file and attribute
                new_file = chain_file
                new_attribute = chain_attribute

            # add the new file to files
            files.append({'trait_type': TRAIT_ORDER[i], 'file': new_file})

            # add the new attribute to the attributes
            attributes.append(new_attribute)

            # make a metadata dict for the new citizen
            metadata_dict = {
                'name': self.ipfs_data['name'],
                'image': '',  # this will be set AFTER the image is uploaded
                'attributes': attributes,
                'trait_files': files
            }

        return metadata_dict

    # function to upload to ipfs (both citizen and metadata --> return metadata uri)
    def upload_to_ipfs(self):
        # get the files
        files = [f"{self.sex}/{file}" for file in self.composition_files]

        # create a piece of art, initializing with the first file
        art = Art({'full_path': os.path.join(ART_FOLDER, files[0])})

        # iterate over the files
        for file in files[1:]:
            # paste each file onto the original piece of art
            art.paste({'full_path': os.path.join(ART_FOLDER, file)})

        # upload the image to ipfs
        image_link = upload_to_ipfs(art.image)

        # need a image link to keep going
        if not image_link:
            return None

        # now that you have the pinata link, finish the metadata
        self.metadata['image'] = image_link

        # upload the metadata to ipfs
        metadata_link = upload_to_ipfs(
            bytes(json.dumps(self.metadata, indent=4)))

        # need metadata link to continue
        if not metadata_link:
            return None

        return metadata_link

    # get only the files for composition
    @property
    def composition_files(self):
        # iterate over all the files and add them to a list
        files = [file['file'] for file in self.metadata['trait_files']]

        return files


# make a market broker that interacts with the avvenire citizens market
class CitizenMarketBroker:
    def __init__(self, contract, citizen_id):
        # store the contract
        self.contract = contract

    # get the citizen
    def get_citizen(self):
        # need to connect to other contract to get the citizen
        citizen = self.contract.avvenireCitizens.tokenIdToCitizen(
            self.citizen_id)
        return citizen

    # get the traits of the citizen
    def get_traits(self):
        citizen = self.get_citizen()
        traits = citizen.traits

        return traits

    # function to set a citizen's sex
    def set_sex(self):
        # get the citizen
        citizen = self.get_citizen()

        # get the ipfs data
        ipfs_data = self.get_ipfs_data(citizen)

        # IF the citizen's sex is not set already, set it
        if citizen[3] == 0:
            # set the sex
            citizen[3] = SEX_ORDER.index(
                ipfs_data['attributes'][0]['value']) + 1

            # set the citizen's data
            self.contract.setCitizenData(
                citizen, {'from': get_server_account()})

    # function to update a citizen
    def update_citizen(self):
        citizen = self.get_citizen()

        # check to make sure that the citizen has a change requested
        if not self.contract.tokenChangeRequests(self.citizen_id).changeRequested:
            print(f"No change was requested for citizen {self.citizen_id}")

        # get all the existing traits from ipfs (these will be integers)
        ipfs_data = self.get_ipfs_data(citizen)

        # if there are not ipfs traits, say that we failed to update the citizen
        if not ipfs_data:
            print(
                f"Failed to update citizen due to lack of ipfs data: {self.citizen_id}")
            return

        # get the citizen's sex
        sex = ipfs_data['attributes'][0]['value']

        # create a citizen creator with the two bunches of traits
        citizen_creator = CitizenCreator(ipfs_data, citizen[4], sex)

        # upload the citizen to ipfs
        uri = citizen_creator.upload_to_ipfs()

        # change the citizen uri
        citizen[1] = uri

        # set the citizen data with the contract using the admin account
        self.contract.setCitizenData(citizen, {'from': get_server_account()})

        pass

    # get some blank trait changes
    def get_blank_trait_change(self):
        # matching a blank trait change from the Avvenire Citizen Market contract
        return [0, False, 0, 0]

    def get_ipfs_data(self, citizen):
        # check if there is a uri
        uri = citizen[1]

        # a uri with nothing set to it signifies a freshly minted citizen (where there have been no changes yet)
        if not uri:
            uri = f"{BASE_URI}{self.citizen_id}"

        # get the citizen data from ipfs using the uri
        try:
            data = requests.get(uri).json()
        except requests.exceptions.JSONDecodeError:
            print(f"No character data found at {uri}")
            return None

        return data


# a class for managing on-chain traits
class TraitManager:
    def __init__(self, contract, trait_id):
        # save the contract
        self.contract = contract

    # function to update a trait (needs to be relocated to a trait manager --> will become a part of creating a citizen)
    # on the API, citizen creations will be stored with the exact traits created and dropped --> will have this data
    def update_trait(self):
        # get the trait
        trait = self.contract.tokenIdToTrait(trait_id)

        # get the trait data from ipfs by linking it to the origin citizen
        resp = requests.get(f"{BASE_URI}/{trait[6]}")

        # check if we got anything
        if resp.status_code > 299:
            print(f"Unable to get the data for trait: {trait}")
            return

        # get the citizen data
        citizen_data = resp.json()

        # get dictionaries for the attributes and files
        attribute_dict = {attribute['trait_type']: attribute['value']
                          for attribute in citizen_data['attributes']}
        file_dict = {trait_files['trait_type']: trait_files['file']
                     for trait_files in citizen_data['trait_files']}

        # get the trait data depending on the trait type
        trait_type = TRAIT_ORDER[trait[5] - 1]
        file = file_dict[trait_type]
        attribute = attribute_dict[trait_type]

        # create the metadata
        metadata = create_trait(
            attribute, file, trait_type)

        # get the image (just create some art with only one file)
        art = Art({'full_path': os.path.join(ART_FOLDER, file)})

        # upload the image to ifpfs
        art_link = upload_to_ipfs(art.image)

        # set the image associated with the trait
        metadata['image'] = art_link

        # upload the metadata to ipfs
        metadata_link = upload_to_ipfs

        # change the trait's uri (rest can stay the same)
        trait[1] = metadata_link

        # set the trait's data using the admin account
        self.contract.setTraitsData(trait, {'from': get_server_account()})

        pass


# function for standardizing trait data
def create_trait(name, file, trait_type):
    return {'name': name, 'file': file, 'attributes': {'trait_type': trait_type, 'value': name}}


'''
NOTES
- this is mainly to make changes on the backend, so it may need to interact using web3
    - for even more security, it may be smart to hire a server security expert
        - we could also just run these from a computer and person --> get logged changes and make them
'''
