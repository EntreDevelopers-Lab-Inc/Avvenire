# make a market broker that interacts with the avvenire citizens market
class CitizenMarketBroker:
    def __init__(self, contract, citizenId):
        # store the contract
        self.contract = contract

    # get the citizen
    def get_citizen(self):
        # need to connect to other contract to get the citizen
        citizen = self.contract.avvenireCitizens.tokenIdToCitizen(
            self.citizenId)
        return citizen

    # get the traits of the citizen

    def get_traits(self):
        citizen = self.get_citizen()
        traits = citizen.traits

        return traits

    # function to update a citizen
    def update_citizen(self, citizen_data):
        citizen = self.get_citizen()

        # check to make sure that the citizen has a change requested
        if not self.contract.tokenChangeRequests(self.citizenId).changeRequested:
            print(f"No change was requested for citizen {self.citizenId}")

        # create the citizen using generative art

        # upload the citizen to ipfs

        # get the ipfs uri

        # create the citizen's data

        # set the citizen data with the contract using the admin account

        pass

    # function to update a trait
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


'''
NOTES
- this is mainly to make changes on the backend, so it may need to interact using web3
    - for even more security, it may be smart to hire a server security expert
        - we could also just run these from a computer and person --> get logged changes and make them
'''
