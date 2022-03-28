import pytest, brownie, time

from brownie import (
    AvvenireCitizens,
    AvvenireCitizenMarket,
    AvvenireCitizensData,
    testAvvenireBurn,
    accounts,
    exceptions,
)
from scripts.script_definitions import drop_interval, owner_of

from tools.ChainHandler import CitizenMarketBroker, TraitManager

from scripts.helpful_scripts import get_account, get_dev_account
from scripts.mint import mint_citizens_and_initialize, mint_citizens
from scripts.auction import end_auction_and_enable_changes, setup_auction

# always have an auction, and initialize the citizens
@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    mint_citizens_and_initialize(3, accounts[2])
    # Accounts[2] owns 0, 1, 2
    
    mint_citizens_and_initialize(2, accounts[3])
    # Accounts[3] owns 3, 4
    
    end_auction_and_enable_changes()

def test_transfer_trade_before_change_false():
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]

    # use account 2 for the test user
    account = accounts[2]
    other_account = accounts[3]

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
    drop_interval(1)
    print(data_contract.getCitizen(0))
    market_contract.combine(0, male_trait_changes, {"from": account})

    # make sure that the trait came off of the citizen
    assert data_contract.getCitizen(0)[4][1][2] is False
    assert data_contract.getCitizen(0)[4][1][3] is False
    
    # ***
    # Since trade before change is fals, should not be able to transfer citizen
    # ***
    with brownie.reverts():
        citizens_contract.transferFrom(account, other_account, 0, {"from": account})

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1
    
    # ***
    # Since trade before change is fals, should not be able to transfer trait
    # ***
    with brownie.reverts():
        citizens_contract.transferFrom(account, other_account, new_trait_id, {"from": account})

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect
    
    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()
    
    # ***
    # Changes in place... Now should be able to ransfer 
    # ***
    
    citizens_contract.transferFrom(account, other_account, 0, {"from": account})
    assert citizens_contract.ownerOf(0) == other_account
    
    citizens_contract.transferFrom(account, other_account, new_trait_id, {"from": account})
    assert citizens_contract.ownerOf(new_trait_id) == other_account 

def test_burn():
    admin_account = get_account()
    burn_test_contract = testAvvenireBurn.deploy(AvvenireCitizens[-1].address, {"from": admin_account})
    citizens_contract = AvvenireCitizens[-1]
    citizens_contract.setAllowedPermission(testAvvenireBurn[-1].address, True, {"from": admin_account})
    
    account = accounts[2]
    
    burn_test_contract.burn(0, {"from": account})
    
    assert citizens_contract.ownerOf(0) != account 
    
    
    