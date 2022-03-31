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
    from constants import BASE_URI, EXTENSION, WAIT_BLOCKS
    from GenerativeArt.core.art import Art
    from tools.ipfs import upload_to_ipfs

# create a trait order
TRAIT_ORDER = [
    "Background",
    "Body",
    "Tattoo",
    "Eyes",
    "Mouth",
    "Mask",
    "Necklace",
    "Clothing",
    "Earrings",
    "Hair",
    "Effect",
]

# create the sex order
SEX_ORDER = ["Male", "Female"]

# set the default
DEFAULT_FILE = f"DEFAULT.{EXTENSION}"

# get the working directory
WORKING_DIR = os.getcwd()

# if tests is in the working directory, remove blockchain and tests from it
if "tests" in WORKING_DIR:
    WORKING_DIR = WORKING_DIR.split("tests")[0]

# set the folder with the art (remove tests from path if it is there)
ART_FOLDER = os.path.join(WORKING_DIR, "GenerativeArt")


# make a class that can create citizens by comparing ipfs to on-chain data
class CitizenCreator:
    def __init__(self, ipfs_data, chain_data):
        # save each group of traits
        self.ipfs_data = ipfs_data
        self.ipfs_files = {
            trait["trait_type"]: trait["file"]
            for trait in self.ipfs_data["trait_files"]
        }
        self.ipfs_traits = {
            trait["trait_type"]: trait["value"]
            for trait in self.ipfs_data["attributes"]
        }

        # store the sex, so you can use the right file
        self.sex = self.ipfs_data["attributes"][0]["value"]

        # save the overall on-chain data
        self.chain_data = chain_data

        # convert the on-chain data into files
        self.chain_traits = self.extract_data_for_traits(chain_data)

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
        # get what type of trait it is
        trait_type = TRAIT_ORDER[trait[5] - 1]

        # if there is a uri, get the info from there
        if trait[1]:
            # get the trait data from ipfs
            try:
                data = requests.get(trait[1]).json()
            except requests.exceptions.JSONDecodeError:
                print(f"No trait data found at {trait[1]}")
                return None

            return data
        # if there is not a uri, but it exists, get the data from ipfs
        elif trait[3]:
            return create_trait(
                self.ipfs_traits[trait_type], self.ipfs_files[trait_type], trait_type, self.sex
            )
        # if no uri, and it doesn't exist, set it to the default
        else:
            # imply the file default information based on the trait type and sex
            # first argument (name) will never be used, as no name will be set
            return create_trait(
                f"Default {trait_type}", f"{trait_type}/{DEFAULT_FILE}", trait_type, self.sex
            )

    # create a way to get the metadata
    def get_metadata(self):
        # make sure that we have chain traits
        if not self.chain_traits:
            return None

        # create a file list
        files = []

        # create an attribute list (start with the sex data)
        attributes = [{"trait_type": "Sex", "value": self.sex}]

        # iterate over all of the files in both trait lists
        for i in range(len(TRAIT_ORDER)):
            # get the chain file
            chain_file = self.chain_traits[i]["file"]
            chain_attribute = self.chain_traits[i]["name"]

            # add the new file to files
            files.append({"trait_type": TRAIT_ORDER[i], "file": chain_file})

            # add the new attribute to the attributes
            attributes.append(
                {'trait_type': TRAIT_ORDER[i], 'value': chain_attribute})

            # make a metadata dict for the new citizen
            metadata_dict = {
                "name": self.ipfs_data["name"],
                "image": "",  # this will be set AFTER the image is uploaded
                "attributes": attributes,
                "trait_files": files,
            }

        return metadata_dict

    # function to upload to ipfs (both citizen and metadata --> return metadata uri)
    def upload_to_ipfs(self):
        # create the composition files from the metadata that will be pushed on chain
        composition_files = [
            os.path.join(*entry["file"].split("/"))
            for entry in self.metadata["trait_files"]
        ]

        # get the files
        files = [os.path.join(self.sex, file) for file in composition_files]

        print(composition_files)

        # create a piece of art, initializing with the first file
        art = Art({"full_path": os.path.join(ART_FOLDER, files[0])})

        # iterate over the files
        for file in files[1:]:
            # paste each file onto the original piece of art
            art.paste({"full_path": os.path.join(ART_FOLDER, file)})

        # upload the image to ipfs
        image_link = upload_to_ipfs(art.image)

        # need a image link to keep going
        if not image_link:
            return None

        # now that you have the pinata link, finish the metadata
        self.metadata["image"] = image_link

        # upload the metadata to ipfs
        metadata_link = upload_to_ipfs(
            bytes(json.dumps(self.metadata, indent=4), encoding="utf-8"), extension=None
        )

        # need metadata link to continue
        if not metadata_link:
            print(f"no metadata link found")
            return None

        return metadata_link

    # get only the files for composition
    @property
    def composition_files(self):
        # iterate over all the files and add them to a list
        files = [file["file"] for file in self.metadata["trait_files"]]

        return files


# make a market broker that interacts with the avvenire citizens market
class CitizenMarketBroker:
    def __init__(self, contract, citizen_id):
        # store the contract
        self.contract = contract

        # store the citizen id
        self.citizen_id = citizen_id

    # get the citizen
    def get_citizen(self):
        # need to connect to other contract to get the citizen
        citizen = list(self.contract.getCitizen(self.citizen_id))
        
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

        # cannot do anything without ipfs data
        if not ipfs_data:
            print(f"Did not receive ipfs data when calling {citizen[1]}")
            return

        # IF the citizen's sex is not set already, set it
        if citizen[3] == 0:
            sex_id = int(SEX_ORDER.index(
                ipfs_data["attributes"][0]["value"])) + 1

            # set the sex
            citizen[3] = sex_id
        else:
            print(f"Already initialized: {citizen}")

        # set the citizen's data --> no need to update further, as the citizen's data is already stored
        tx = self.contract.setCitizenData(
            citizen, False, {"from": get_server_account()})
        tx.wait(3)

    # function to update a citizen
    def update_citizen(self):
        citizen = self.get_citizen()

        # check to make sure that the citizen has a change requested
        if not self.contract.tokenChangeRequests(self.citizen_id):
            print(f"No change was requested for citizen {self.citizen_id}")

        # get all the existing traits from ipfs (these will be integers)
        ipfs_data = self.get_ipfs_data(citizen)

        # if there are not ipfs traits, say that we failed to update the citizen
        if not ipfs_data:
            print(
                f"Failed to update citizen due to lack of ipfs data: {self.citizen_id}"
            )
            return

        # create a citizen creator with the two bunches of traits
        citizen_creator = CitizenCreator(ipfs_data, citizen[4])

        # upload the citizen to ipfs
        uri = citizen_creator.upload_to_ipfs()

        # if there is no uri, it never got uploaded, which is bad
        if not uri:
            return tuple()

        # change the citizen uri
        citizen[1] = uri

        # set the citizen data with the contract using the admin account --> no need for more changes, set those to false
        tx = self.contract.setCitizenData(
            citizen, False, {"from": get_server_account()})
        
        tx.wait(3)
            

        # return reconverted version of citizen for better understanding
        return tuple(citizen)

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

        # saev the trait id
        self.trait_id = trait_id

    # function to update a trait (needs to be relocated to a trait manager --> will become a part of creating a citizen)
    # on the API, citizen creations will be stored with the exact traits created and dropped --> will have this data
    def update_trait(self):
        # get the trait
        trait = list(self.contract.getTrait(self.trait_id))

        # get the trait data from ipfs by linking it to the origin citizen
        resp = requests.get(f"{BASE_URI}{trait[6]}")

        # check if we got anything
        if resp.status_code > 299:
            print(f"Unable to get the data for trait: {trait}")
            return

        # get the citizen data
        citizen_data = resp.json()

        # get dictionaries for the attributes and files
        attribute_dict = {
            attribute["trait_type"]: attribute["value"]
            for attribute in citizen_data["attributes"]
        }
        file_dict = {
            trait_files["trait_type"]: trait_files["file"]
            for trait_files in citizen_data["trait_files"]
        }

        # get the trait sex (which will already be set automatically by the market contract)
        sex = SEX_ORDER[trait[4] - 1]

        # get the trait data depending on the trait type
        trait_type = TRAIT_ORDER[trait[5] - 1]
        file = file_dict[trait_type]
        attribute = attribute_dict[trait_type]

        # create the metadata
        metadata = create_trait(attribute, file, trait_type, sex)

        # get the image (just create some art with only one file)
        art = Art({"full_path": os.path.join(ART_FOLDER, sex, file)})

        # upload the image to ifpfs
        art_link = upload_to_ipfs(art.image)

        # set the image associated with the trait
        metadata["image"] = art_link

        # upload the metadata to ipfs
        metadata_bytes = json.dumps(metadata, indent=4).encode('utf-8')
        metadata_link = upload_to_ipfs(metadata_bytes, extension=None)

        # change the trait's uri (rest can stay the same)
        trait[1] = metadata_link

        # set the sex to ENSURE that it is in-line with ipfs
        trait[4] = SEX_ORDER.index(citizen_data['attributes'][0]['value']) + 1

        # set the trait's data using the admin account (set change update to false, as the trait has been updated)
        tx = self.contract.setTraitData(
            trait, False, {"from": get_server_account()})
        tx.wait(3)

        return tuple(trait)


# function for standardizing trait data
def create_trait(name, file, trait_type, sex):
    return {
        "name": name,
        "file": file,
        "attributes": [{'Sex': sex}, {"trait_type": trait_type, "value": name}],
    }


"""
NOTES
- this is mainly to make changes on the backend, so it may need to interact using web3
    - for even more security, it may be smart to hire a server security expert
        - we could also just run these from a computer and person --> get logged changes and make them
"""
