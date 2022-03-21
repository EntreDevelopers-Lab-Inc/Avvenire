import pytest
import brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, accounts
from web3 import Web3

from tools.ChainHandler import CitizenMarketBroker, TraitManager

from scripts.helpful_scripts import get_account
from scripts.mint import mint_citizens_and_initialize, mint_citizens
from scripts.auction import setup_auction


# always have an auction, and initialize the citizens
@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    mint_citizens_and_initialize(3, accounts[2])


# test to bind a false trait id
def test_false_trait():
    # keep track of the contract
    market_contract = AvvenireCitizenMarket[-1]

    # use account 2 for the test user
    account = accounts[2]

    # request from the market to remove all the traits of a citizen
    trait_changes = [
        [0, False, 2, 1],
        [10, True, 2, 2],  # change to body that doesn't exist
        [0, False, 2, 3],
        [0, False, 2, 4],
        [0, False, 2, 5],
        [0, False, 2, 6],
        [0, False, 2, 7],
        [0, False, 2, 8],
        [0, False, 2, 9],
        [0, False, 2, 10],
        [0, False, 2, 11],
    ]

    # test combination of fake trait
    with brownie.reverts():
        market_contract.combine(0, trait_changes, {'from': account})


# bind a real trait to the wrong sex
def test_wrong_combination():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]

    # use account 2 for the test user
    account = accounts[2]

    # take off the male hair
    # request from the market to remove all the traits of a citizen
    male_trait_changes = [
        [0, False, 2, 1],
        [0, False, 2, 2],
        [0, False, 2, 3],
        [0, False, 2, 4],
        [0, False, 2, 5],
        [0, False, 2, 6],
        [0, False, 2, 7],
        [0, False, 2, 8],
        [0, False, 2, 9],
        [0, True, 2, 10],  # put on default hair
        [0, False, 2, 11],
    ]

    # put on default hair
    market_contract.combine(0, male_trait_changes, {'from': account})

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    trait_manager.update_trait()  # this is updating the effect

    # put the male hair on a female
    female_trait_changes = [
        [0, False, 3, 1],
        [0, False, 3, 2],
        [0, False, 3, 3],
        [0, False, 3, 4],
        [0, False, 3, 5],
        [0, False, 3, 6],
        [0, False, 3, 7],
        [0, False, 3, 8],
        [0, False, 3, 9],
        [new_trait_id, True, 2, 10],  # put on male hair
        [0, False, 2, 11],
    ]
    with brownie.reverts():
        market_contract.combine(2, female_trait_changes, {'from': account})
