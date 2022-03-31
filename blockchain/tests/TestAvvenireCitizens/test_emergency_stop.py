import pytest, brownie, time

from brownie import (
    AvvenireTest,
    AvvenireCitizens,
    AvvenireCitizenMarket,
    AvvenireCitizensData,
    accounts,
    exceptions,
)
from web3 import Web3
from scripts.script_definitions import drop_interval
from pytest import approx 

from tools.ChainHandler import CitizenMarketBroker, TraitManager

from scripts.helpful_scripts import get_account, get_dev_account
from scripts.mint import mint_citizens_and_initialize, mint_citizens
from scripts.auction import end_auction_and_enable_changes, setup_auction

REQUEST_COST = Web3.toWei(0.01, "ether")

@pytest.fixture()
def auction_complete():
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    mint_citizens_and_initialize(3, accounts[2])
    # Accounts[2] owns 0, 1, 2
    
    mint_citizens_and_initialize(2, accounts[3])
    # Accounts[3] owns 3, 4
    
    end_auction_and_enable_changes()

def test_safemint_emergency():
    setup_auction()
    
    admin_account = get_account()
    account = accounts[3]
    citizens_contract = AvvenireCitizens[-1]
    avvenire_auction_contract = AvvenireTest[-1]
    cost = avvenire_auction_contract.getAuctionPrice() * 2
    
    # set emergency stop to true
    citizens_contract.setEmergencyStop(True, {"from": admin_account})
    
    with brownie.reverts():
        avvenire_auction_contract.auctionMint(2, {"from": account, "value": cost})

    
def test_bind_emergency(auction_complete):
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    account = accounts[2]

    male_trait_changes = [
        [0, False, 1, 1],
        [0, True, 1, 2],  # put on default body
        [0, False, 1, 3],
        [0, False, 1, 4],
        [0, False, 1, 5],
        [0, False, 1, 6],
        [0, False, 1, 7],
        [0, False, 1, 8],
        [0, False, 1, 9],
        [0, False, 1, 10],
        [0, False, 1, 11],
    ]

    # set emergency stop to true
    citizens_contract.setEmergencyStop(True, {"from": admin_account})
    
    # Shouldn't be able to combine as bind has the stoppedInEmergency modifier...
    with brownie.reverts():
        market_contract.combine(0, male_trait_changes, {"from": account})
        
def test_set_citizen_and_trait_emergency(auction_complete):
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]

    # use account 2 for the test user
    account = accounts[2]
    admin_account = get_account()

    # take off the male body
    # request from the market to remove the hair of a citizen
    male_trait_changes = [
        [0, False, 1, 1],
        [0, True, 1, 2],  # put on default body
        [0, False, 1, 3],
        [0, False, 1, 4],
        [0, False, 1, 5],
        [0, False, 1, 6],
        [0, False, 1, 7],
        [0, False, 1, 8],
        [0, False, 1, 9],
        [0, False, 1, 10],
        [0, False, 1, 11],
    ]

    # put on default body
    market_contract.combine(0, male_trait_changes, {"from": account})
    
    # Set emergency stop to true...
    citizens_contract.setEmergencyStop(True, {"from": admin_account})

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    
    with brownie.reverts():
        new_trait = trait_manager.update_trait()  # this is updating the effect
        
    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    
    with brownie.reverts():
        citizen = broker.update_citizen()

