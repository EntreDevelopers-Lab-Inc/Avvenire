import pytest
import brownie

from brownie import (
    AvvenireTest,
    AvvenireCitizens,
    AvvenireCitizenMarket,
    accounts,
    exceptions,
)
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
        [0, False, 1, 1],
        [10, True, 1, 2],  # change to body that doesn't exist
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

    # test combination of fake trait
    # with brownie.reverts():
    with pytest.raises(exceptions.VirtualMachineError):
        market_contract.combine(0, trait_changes, {"from": account})


# bind a real trait to the wrong sex
def test_wrong_sex():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]

    # use account 2 for the test user
    account = accounts[2]

    # take off the male hair
    # request from the market to remove all the traits of a citizen
    male_trait_changes = [
        [0, False, 1, 1],
        [0, False, 1, 2],
        [0, False, 1, 3],
        [0, False, 1, 4],
        [0, False, 1, 5],
        [0, False, 1, 6],
        [0, False, 1, 7],
        [0, False, 1, 8],
        [0, False, 1, 9],
        [0, True, 1, 10],  # put on default hair
        [0, False, 1, 11],
    ]

    # put on default hair
    market_contract.combine(0, male_trait_changes, {"from": account})

    # make sure that the trait came off of the citizen
    assert citizens_contract.tokenIdToCitizen(0)[4][9][3] is False

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # get the trait data
    new_trait = citizens_contract.tokenIdToTrait(new_trait_id)
    assert new_trait == (new_trait_id, '', True, True, 1, 10, 0)

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    trait_manager.update_trait()  # this is updating the effect

    print(citizens_contract.tokenIdToTrait(new_trait_id))

    # put the male hair on a female
    female_trait_changes = [
        [0, False, 2, 1],
        [0, False, 2, 2],
        [0, False, 2, 3],
        [0, False, 2, 4],
        [0, False, 2, 5],
        [0, False, 2, 6],
        [0, False, 2, 7],
        [0, False, 2, 8],
        [0, False, 2, 9],
        [new_trait_id, True, 2, 10],  # put on male hair
        [0, False, 2, 11],
    ]
    with brownie.reverts():
        market_contract.combine(2, female_trait_changes, {"from": account})


# test adding a new background


# test changing body


# test adding a tattoo


# test changing eyes


# test changing mouth


# test changing mask


# test changing necklace


# test changing clothing


# test changing hair


# test changing effect
