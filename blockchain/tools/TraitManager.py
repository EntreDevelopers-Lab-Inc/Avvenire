import requests

# constants file is either in test mode or the full path
try:
    from blockchain.constants import BASE_URI
except ImportError:
    from constants import BASE_URI


# create a trait order
TRAIT_ORDER = ['Background', 'Body', 'Tattoo', 'Eyes', 'Mouth',
               'Mask', 'Necklace', 'Clothing', 'Earrings', 'Hair', 'Effect']

# create the sex order
SEX_ORDER = ['Male', 'Female']

# create a file extension
EXTENSION = 'PNG'

# set the default
DEFAULT_FILE = f"DEFAULT.{EXTENSION}"


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
            return {'name': 'Default', 'file': f"{trait_type}/{DEFAULT_FILE}", 'attributes': {'trait_type': trait_type, 'value': 'Default'}}

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

        # iterate over the files
            # make the full path of the file, as this will indicate where to find the file for pasting

            # paste each file onto the original piece of art

        # create a hash using bytecode and upload it to the local pinata api: https://medium.com/python-pandemonium/getting-started-with-python-and-ipfs-94d14fdffd10

        # upload the image hash to pinata: https://docs.pinata.cloud/api-pinning/pin-by-hash

        # now that you have the pinata link, finish the metadata

        # upload the metadata to local ipfs

        # upload the file hash to pinata

        # return the pinata metadata --> will only need to set the image uri of the character's data after this

        pass

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

    # function to update a citizen
    def update_citizen(self, citizen_data):
        citizen = self.get_citizen()
        print(citizen)

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

        # create the NEW citizen using generative art (using citizen creator)

        # upload the citizen to ipfs

        # get the ipfs uri

        # create the citizen's data

        # set the citizen data with the contract using the admin account

        pass

    # function to update a trait (needs to be relocated to a trait manager --> will become a part of creating a citizen)
    # on the API, citizen creations will be stored with the exact traits created and dropped --> will have this data
    def update_trait(self, trait_id):
        # get the trait

        # upload the trait to ipfs

        # create the trait's data

        # set the trait's data using the admin account

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


'''
NOTES
- this is mainly to make changes on the backend, so it may need to interact using web3
    - for even more security, it may be smart to hire a server security expert
        - we could also just run these from a computer and person --> get logged changes and make them
'''
