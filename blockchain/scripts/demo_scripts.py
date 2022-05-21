import brownie, pytest

from brownie import AvvenireCitizenMarket, AvvenireTraits, AvvenireCitizens, network
from web3 import Web3
from pytest import approx

from scripts.script_definitions import *
from scripts.helpful_scripts import *
from scripts.auction import *
from scripts.mint import *

GAS_LIMIT = 29000000
REQUEST_COST = Web3.toWei(0.01, "ether")

from web3 import Web3

from tools.ChainHandler import CitizenMarketBroker, TraitManager

# always have an auction, and initialize the citizens
def mint_citizens_end_auction():
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    account = get_dev_account()
    mint_citizens_and_initialize(3, account)
    end_auction_and_enable_changes()

def take_off_traits():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    traits_contract = AvvenireTraits[-1]
    data_contract = AvvenireCitizensData[-1]

    # use account 2 for the test user
    account = get_dev_account()
    admin_account = get_account()
    
    total_supply = citizens_contract.getTotalSupply()
    citizens_contract.setOwnersExplicit(total_supply, {"from": admin_account} )
    
    # take off the male body
    # request from the market to remove the hair of a citizen
    male_trait_changes = [
        [0, False, 1, 1],
        [0, False, 1, 2], 
        [0, False, 1, 3],
        [0, True, 1, 4], # put on default eyes
        [0, True, 1, 5], # put on default mouth
        [0, False, 1, 6], 
        [0, False, 1, 7], 
        [0, True, 1, 8], # put on default clothin
        [0, False, 1, 9], 
        [0, False, 1, 10], 
        [0, False, 1, 11],
    ]
    
    # *** 
    # Trait indexes
    # ***
    trait_indexes = [3, 4, 7]
        
    # ***
    # Combining...
    # ***
    tx = market_contract.combine(0, male_trait_changes, {"from": account})
    tx.wait(2)


    # ***
    # Check that the new traits have the proper information
    # ***

    #Traits indexed @ 1
    end_trait_id = traits_contract.getTotalSupply() 
    
    for x in range(len(trait_indexes)):
        # update the uri
        trait_manager = TraitManager(data_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect

    # Update the citizen
    broker = CitizenMarketBroker(data_contract, 0)
    citizen = broker.update_citizen()

def put_on_new_citizen():
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    traits_contract = AvvenireTraits[-1]
    data_contract = AvvenireCitizensData[-1]
    
    account = get_dev_account()
    admin_account = get_account()
    
    # *** 
    # Trait indexes
    # ***
    trait_indexes = [3, 4, 7]
    
    other_male_trait_changes = [
        [0, False, 1, 1],
        [0, True, 1, 2],  
        [0, False, 1, 3],
        [end_trait_id - 2, True, 1, 4], # put on existing eyes
        [end_trait_id - 1, True, 1, 5], # put on existing mouth
        [0, False, 1, 6], 
        [0, False, 1, 7], 
        [end_trait_id, True, 1, 8], # clothing
        [0, False, 1, 9],  
        [0, True, 1, 10], 
        [0, False, 1, 11],
    ]
    

    tx = market_contract.combine(1, other_male_trait_changes, {"from": account})
    tx.wait(2)
    
    # ***
    # Make sure that the new traits attatched to Citizen 1 are correct 
    # *** 
    start_trait_id = end_trait_id - 4
    
    # update the male
    broker = CitizenMarketBroker(data_contract, 1)
    citizen = broker.update_citizen()
    
    for x, index in enumerate(trait_indexes):    
        trait_manager = TraitManager(data_contract, start_trait_id + x)
        new_trait = trait_manager.update_trait()  # this is updating the effect
    
    #*** 
    # Update minted traits
    # ***
    
    #traits indexed @ 1
    end_trait_id = traits_contract.getTotalSupply() 
    for x in range(len(trait_indexes)):
        # update the uri
        trait_manager = TraitManager(data_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect
