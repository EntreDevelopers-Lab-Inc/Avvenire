import brownie

from brownie import AvvenireTest, AvvenireCitizenMarket
from web3 import Web3
from pytest import approx

from scripts.script_definitions import *
from scripts.helpful_scripts import *
from scripts.auction import *
from scripts.mint import *

DEV_PAYMENT = Web3.toWei(0.5, "ether")
GAS_LIMIT = 29000000
REQUEST_COST = Web3.toWei(0.01, "ether")

from web3 import Web3

from tools.ChainHandler import CitizenMarketBroker, TraitManager

# always have an auction, and initialize the citizens
def citizens_minted():
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    account = get_dev_account()
    mint_citizens_and_initialize(3, account)
    end_auction_and_enable_changes()

def combine_first_citizen():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]

    # use account 2 for the test user
    account = get_dev_account()
    
    # take off the male body
    # request from the market to remove the hair of a citizen
    male_trait_changes = [
        [0, False, 1, 1],
        [0, True, 1, 2],  # put on default body 
        [0, False, 1, 3],
        [0, True, 1, 4], # put on default eyes
        [0, True, 1, 5], # put on default mouth
        [0, False, 1, 6], 
        [0, False, 1, 7], 
        [0, True, 1, 8], # put on default clothin
        [0, False, 1, 9], 
        [0, True, 1, 10], # put on default hair 
        [0, False, 1, 11],
    ]
    
    # *** 
    # Trait indexes
    # ***
    trait_indexes = [1, 3, 4, 7, 9]

    # ***
    # Combining...
    # ***
    supply_before_combine = citizens_contract.getTotalSupply()
    tx = market_contract.combine(0, male_trait_changes, {"from": account})
    tx.wait(3)

    end_trait_id = citizens_contract.getTotalSupply() - 1
    for x in range(len(trait_indexes)):
        trait_manager = TraitManager(citizens_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect
        time.sleep(10)

    # Update the citizen
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

def combine_second_citizen():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]

    # use account 2 for the test user
    account = get_dev_account()
    
    end_trait_id = citizens_contract.getTotalSupply() - 1
    other_male_trait_changes = [
        [0, False, 1, 1],
        [end_trait_id - 4, True, 1, 2],  # body 
        [0, False, 1, 3],
        [end_trait_id - 3, True, 1, 4], # put on existing eyes
        [end_trait_id - 2, True, 1, 5], # put on existing mouth
        [0, False, 1, 6], 
        [0, False, 1, 7], 
        [end_trait_id - 1, True, 1, 8], # clothing
        [0, False, 1, 9],  # 
        [end_trait_id, True, 1, 10], # hair
        [0, False, 1, 11],
    ]
    
    supply_before_combine = citizens_contract.getTotalSupply()
    tx = market_contract.combine(1, other_male_trait_changes, {"from": account})
    tx.wait(3)

def update_citizen_one():
    citizens_contract = AvvenireCitizens[-1]
    # update the male
    broker = CitizenMarketBroker(citizens_contract, 1)
    citizen = broker.update_citizen()

def update_second_citizen_traits():
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]
    
    trait_indexes = [1, 3, 4, 7, 9]
    end_trait_id = citizens_contract.getTotalSupply() - 1
    start_trait_id = end_trait_id - 4
    
    
    for x, index in enumerate(trait_indexes):
       trait_manager = TraitManager(citizens_contract, start_trait_id + x)
       new_trait = trait_manager.update_trait()  # this is updating the effect

def main():
    citizens_contract = AvvenireCitizens[-1]
    print(citizens_contract.getCitizen(1))
    trait = citizens_contract.getTrait(11)
    
    print(f"ownership of 7: {citizens_contract.ownerOf(7)}")