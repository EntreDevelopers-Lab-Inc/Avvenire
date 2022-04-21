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
        
def test_set_trait_emergency(auction_complete):
    citizens_contract = AvvenireCitizens[-1]

    admin_account = get_account()
    random_trait = (0, '', False, False, 0, 1, 0)
    
    # set emergency stop to true
    citizens_contract.setEmergencyStop(True, {"from": admin_account})
    
    with brownie.reverts(): 
        citizens_contract.setTraitData(random_trait, False, {"from": admin_account})

def test_set_citizen_emergency(auction_complete):
    citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]

    admin_account = get_account()
    random_citizen = list(data_contract.getCitizen(1))
    
    # Change random_citizen's tokenId to 0
    random_citizen[0] = 0
    
    # set emergency stop to true
    citizens_contract.setEmergencyStop(True, {"from": admin_account})
    
    with brownie.reverts(): 
        citizens_contract.setCitizenData(random_citizen, False, {"from": admin_account})