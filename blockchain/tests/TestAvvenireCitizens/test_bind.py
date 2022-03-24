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

from scripts.helpful_scripts import get_account, get_dev_account
from scripts.mint import mint_citizens_and_initialize, mint_citizens
from scripts.auction import setup_auction

REQUEST_COST = Web3.toWei(0.25, "ether")


@pytest.fixture
def set_mut_cost():
    admin_account = get_account()
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_citizens_contract.setMutabilityCost(REQUEST_COST, {"from": admin_account})


@pytest.fixture
def set_dev_royalty():
    dev_account = get_dev_account()
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_citizens_contract.setDevRoyalty(50, {"from": dev_account})


# always have an auction, and initialize the citizens
@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    mint_citizens_and_initialize(3, accounts[2])


def test_single_trait_change_no_cost():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]

    # use account 2 for the test user
    account = accounts[2]

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

    # make sure that the trait came off of the citizen
    assert citizens_contract.tokenIdToCitizen(0)[4][2][2] is False
    assert citizens_contract.tokenIdToCitizen(0)[4][2][3] is False

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the new trait has the proper information
    assert citizens_contract.tokenIdToTrait(new_trait_id) == (
        new_trait_id,
        "",
        True,
        True,
        1,
        2,
        0,
    )

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect

    assert new_trait == citizens_contract.tokenIdToTrait(new_trait_id)

    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

    # ensure that the male on chain is what you set him to
    assert citizen == citizens_contract.tokenIdToCitizen(0)


def test_single_trait_change_with_cost():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    change_cost = citizens_contract.getChangeCost()

    # use account 2 for the test user
    account = accounts[2]

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

    # Mints 1 token and requests_change...
    # Should cost 2 * getChangeCost()...
    total_cost = 2 * change_cost

    # Combine...
    market_contract.combine(
        0, male_trait_changes, {"from": account, "value": total_cost}
    )

    # make sure that the trait came off of the citizen
    assert citizens_contract.tokenIdToCitizen(0)[4][2][2] is False
    assert citizens_contract.tokenIdToCitizen(0)[4][2][3] is False

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the new trait has the proper information
    # should be a male base_trait that exists and is free...
    # No URI should be set yet
    assert citizens_contract.tokenIdToTrait(new_trait_id) == (
        new_trait_id,
        "",
        True,
        True,
        1,
        2,
        0,
    )
