import requests

# constants file is either in test mode or the full path
try:
    from blockchain.constants import BASE_URI
except ImportError:
    from constants import BASE_URI


# create a trait order
TRAIT_ORDER = ['Background', 'Body', 'Tattoo', 'Eyes', 'Mouth', 'Mask', 'Necklace', 'Clothing', 'Earrings', 'Hair', 'Effect']

# create a file extension
EXTENSION = 'PNG'

# set the default
DEFAULT_FILE = f"DEFAULT.{EXTENSION}"


# make a class that can create citizens by comparing ipfs to on-chain data
class CitizenCreator:
    def __init__(self, ipfs_traits, chain_traits, trait_changes):
        # save each group of traits
        self.ipfs_traits = ipfs_traits
        self.chain_traits = self.int_to_files(chain_traits)

        # this is a list of trait changes (true and false)
        self.trait_changes = trait_changes

    # create a function that converts int traits to files
    # only going to get a list of data off the chain --> need to convert it somehow
    def int_to_files(self, traits):
        # create a list for the files
        files = []

        # iterate over all the traits
        for i in range(len(TRAIT_ORDER)):
            # create a file from the integer
            trait_file = f"{TRAIT_ORDER[i]}/{file_from_int(traits[i])}"

            # add the trait file tot he list of files
            files.append(trait_file)

        # return the files
        return files

    # create a property that gives you the mergable files
    @property
    def mergable_files(self):
        # create a file list
        files = []

        # iterate over all of the files in both trait lists
        for i in range(len(self.ipfs_traits)):
            # get the ipfs trait
            ipfs_trait = self.ipfs_traits[i]['file']

            # get the chain trait
            chain_trait = self.chain_traits[i]

            # if the ipfs trait and the chain trait are the same, just use that file
            if ipfs_trait == chain_trait:
                files.append(ipfs_trait)
            # if the ipfs file is a default and the new one is not, a trait has been added to the character
            elif (ipfs_trait == DEFAULT_FILE) and (chain_trait != DEFAULT_FILE):
                files.append(chain_trait)
            # if the ipfs file is NOT a default, and the new one is, the trait has been removed, add the chain trait
            elif (ipfs_trait != DEFAULT_FILE) and (chain_trait == DEFAULT_FILE):
                # what about the case where the chain trait is changed for the first time?
                # need to figure out if a trait has been changed (only want to check here for allowing maximum amount of decentralization)
                if self.trait_changes[i]:
                    # the trait has been changed, go with the on-chain version
                    files.append(chain_trait)
                else:
                    # the trait has NOT been changed, go with the ipfs version
                    files.append(ipfs_trait)
            # if the ipfs trait is not the same as the chain trait, the traits have been swapped
            else:
                files.append(chain_trait)

        return files

    # create a property that gets the actual trait values (using the config and its mapping between trait groups)
    # this would be faster as a database (for later)


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
        ipfs_traits = self.get_ipfs_traits(citizen)

        # if there are not ipfs traits, say that we failed to update the citizen
        if not ipfs_traits:
            print(
                f"Failed to update citizen due to lack of ipfs data: {self.citizen_id}")
            return

        # create a citizen creator with the two bunches of traits
        citizen_creator = CitizenCreator(ipfs_traits, citizen.traits)

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

    def get_ipfs_traits(self, citizen):
        # check if there is a uri
        uri = citizen.uri

        # a uri with nothing set to it signifies a freshly minted citizen (where there have been no changes yet)
        if not uri:
            uri = f"{BASE_URI}{self.citizen_id}"

        # get the citizen data from ipfs using the uri
        try:
            data = requests.get(uri).json()
        except requests.exceptions.JSONDecodeError:
            print(f"No character data found at {uri}")
            return None

        # get the trait files out of the json
        trait_files = data['trait_files']

        return trait_files


# a function for taking an integer and turning it into a compatible filepath
def file_from_int(integer):
    # if the integer is 0, return default
    if integer == 0:
        return DEFAULT_FILE
    # if the integer is < 10, return a buffered number
    elif integer < 10:
        return f"0{integer}.{EXTENSION}"
    # else. return the integer in a formatted way
    else:
        return f"{integer}.{EXTENSION}"


'''
NOTES
- this is mainly to make changes on the backend, so it may need to interact using web3
    - for even more security, it may be smart to hire a server security expert
        - we could also just run these from a computer and person --> get logged changes and make them
'''
