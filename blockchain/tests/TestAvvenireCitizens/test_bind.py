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


def test_bind_existing_token():
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
        new_trait_id, '', True, True, 1, 2, 0)

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect

    assert new_trait == citizens_contract.tokenIdToTrait(new_trait_id)
    print (new_trait)
    
    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

    # ensure that the male on chain is what you set him to
    assert citizen == citizens_contract.tokenIdToCitizen(0)

    # now, put the body on citizen 1
    male_trait_changes = [
        [0, False, 1, 1],
        [new_trait_id, True, 1, 2],  # put on SAME body
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

    print(
        f"citizen before combination: {citizens_contract.tokenIdToCitizen(0)}")
    print(f"new_trait type = {new_trait[5]}" )
    trait_from_mapping = citizens_contract.tokenIdToTrait(new_trait_id)
    trait_type_from_mapping = trait_from_mapping[5]
    print(f"mapping trait type = {trait_from_mapping[5]} ")
    
    assert trait_from_mapping[5] == new_trait[5]
    
          
    # put on the new body
    market_contract.combine(0, male_trait_changes, {"from": account})

    # make sure that the trait is on the citizen
    assert citizens_contract.tokenIdToCitizen(0)[4][2][2] is False
    assert citizens_contract.tokenIdToCitizen(0)[4][2][3] is True
    assert citizens_contract.tokenIdToCitizen(0)[4][2][0] == new_trait_id

    # update the information with a new citizen broker
    broker = CitizenMarketBroker(citizens_contract, 1)
    new_citizen = broker.update_citizen()

    # check that the ipfs data made it
    assert new_citizen == citizens_contract.tokenIdToCitizen(0)


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

    # check that the new trait has the proper information
    assert citizens_contract.tokenIdToTrait(new_trait_id) == (
        new_trait_id, '', True, True, 1, 10, 0)

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect

    # check that the new trait was updated
    assert new_trait == citizens_contract.tokenIdToTrait(new_trait_id)

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

