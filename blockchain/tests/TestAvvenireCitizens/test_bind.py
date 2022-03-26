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
from scripts.script_definitions import drop_interval

from tools.ChainHandler import CitizenMarketBroker, TraitManager

from scripts.helpful_scripts import get_account, get_dev_account
from scripts.mint import mint_citizens_and_initialize, mint_citizens
from scripts.auction import end_auction_and_enable_changes, setup_auction

REQUEST_COST = Web3.toWei(0.01, "ether")


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
    # Accounts[2] owns 0, 1, 2
    
    mint_citizens_and_initialize(2, accounts[3])
    # Accounts[3] owns 3, 4
    
    end_auction_and_enable_changes()

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
    print(citizens_contract.getCitizen(0))
    drop_interval(1)
    print(f"Total Supply = {citizens_contract.getTotalSupply()}")
    
    market_contract.combine(0, male_trait_changes, {"from": account})

    # make sure that the trait came off of the citizen
    assert citizens_contract.getCitizen(0)[4][1][2] is False
    assert citizens_contract.getCitizen(0)[4][1][3] is False

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the new trait has the proper information
    assert citizens_contract.getTrait(new_trait_id) == (
        new_trait_id, '', True, True, 1, 2, 0)

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect

    assert new_trait == citizens_contract.getTrait(new_trait_id)
    
    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

    # ensure that the male on chain is what you set him to
    assert citizen == citizens_contract.getCitizen(0)

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
    # put on the new body
    assert citizens_contract.getCitizen(0)[3] == 1
    assert citizens_contract.getCitizen(1)[3] == 1
    print(citizens_contract.getCitizen(1))
    
    market_contract.combine(1, male_trait_changes, {"from": account})

    # make sure that the trait is on the citizen
    assert citizens_contract.getCitizen(1)[4][1][0] == new_trait_id
    assert citizens_contract.getCitizen(1)[4][1][2] is False
    assert citizens_contract.getCitizen(1)[4][1][3] is True
    
    # update the information with a new citizen broker
    broker = CitizenMarketBroker(citizens_contract, 0)
    new_citizen = broker.update_citizen()

    # check that the ipfs data made it
    assert new_citizen == citizens_contract.getCitizen(0)

def test_attaching_unowned_existing_trait():
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]

    # use account 2 for the test user
    trait_owner = accounts[2]
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
    market_contract.combine(0, male_trait_changes, {"from": trait_owner})

    # make sure that the trait came off of the citizen
    assert citizens_contract.getCitizen(0)[4][1][2] is False
    assert citizens_contract.getCitizen(0)[4][1][3] is False

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the new trait has the proper information
    assert citizens_contract.getTrait(new_trait_id) == (
        new_trait_id, '', True, True, 1, 2, 0)

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect

    # The newly minted trait on IPFS should match the on-chain trait 
    assert new_trait == citizens_contract.getTrait(new_trait_id)
    
    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

    # The citizen on IPFS should match the on-chain data 
    assert citizen == citizens_contract.getCitizen(0)

    # now, put the body on citizen 1
    male_trait_changes = [
        [0, False, 1, 1],
        [new_trait_id, True, 1, 2],  # put on new citizen
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
    # Attempt to put the new trait on citizen #3 which accounts[3] owns
    # It should revert considering accounts[3] does not own the trait
    with brownie.reverts():
        market_contract.combine(3, male_trait_changes, {"from": other_account})
    
    # Assert that no changes have been made 
    assert citizens_contract.getCitizen(3)[4][1][0] == 0
    assert citizens_contract.getCitizen(3)[4][1][2] is False
    assert citizens_contract.getCitizen(3)[4][1][3] is True

def test_binding_wrong_trait_type():
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
    assert citizens_contract.getTrait(new_trait_id) == (
        new_trait_id, '', True, True, 1, 2, 0)

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect

    assert new_trait == citizens_contract.getTrait(new_trait_id)
    
    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

    # ensure that the male on chain is what you set him to
    assert citizen == citizens_contract.tokenIdToCitizen(0)

    # now, put the body on citizen 1
    male_trait_changes = [
        [0, False, 1, 1],
        [0, False, 1, 2],  
        [0, False, 1, 3],
        [new_trait_id, True, 1, 4], # Try to put body on eyes
        [0, False, 1, 5],
        [0, False, 1, 6],
        [0, False, 1, 7],
        [0, False, 1, 8],
        [0, False, 1, 9],
        [0, False, 1, 10],
        [0, False, 1, 11],
    ]         
    # put on the new body
    with brownie.reverts():
        market_contract.combine(0, male_trait_changes, {"from": account})

def test_trait_changes_no_cost():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]

    # use account 2 for the test user
    account = accounts[2]

    supply_before_combine = citizens_contract.getTotalSupply()
    
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
        [0, True, 1, 8], # default clothing
        [0, False, 1, 9], 
        [0, True, 1, 10], # default hair 
        [0, False, 1, 11],
    ]
    # *** 
    # Trait indexes
    # ***
    trait_indexes = [1, 3, 4, 7, 9]
    
    # Make sure all traits exist before combine
    for index in trait_indexes:
        assert citizens_contract.tokenIdToCitizen(0)[4][index][3] is True
    
    # ***
    # Combining...
    # ***
    market_contract.combine(0, male_trait_changes, {"from": account})

    # Make sure that the traits came off of the citizen and the default is on
    for index in trait_indexes:
        assert citizens_contract.tokenIdToCitizen(0)[4][index][0] == 0
        assert citizens_contract.tokenIdToCitizen(0)[4][index][2] is False
        assert citizens_contract.tokenIdToCitizen(0)[4][index][3] is False
    
    # Make sure that 5 tokens were minted
    assert citizens_contract.getTotalSupply() - supply_before_combine == 5
    end_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the new trait has the proper information

    for x in range(5):
        assert citizens_contract.getTrait(end_trait_id - x) == (
            end_trait_id - x, 
            "", 
            True, 
            True, 
            1, 
            # Need to start @ 4...
            trait_indexes[4-x] + 1,  # Adjusted for the fact that TraitTypes start at 1 in contract
            0, 
            )
        # update the hair's uri
        trait_manager = TraitManager(citizens_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect

        assert new_trait == citizens_contract.getTrait(end_trait_id - x)

    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

    # ensure that the male on chain is what you set him to
    assert citizen == citizens_contract.tokenIdToCitizen(0)
    
    # Rebind to new citizen 
    other_male_trait_changes = [
        [0, False, 1, 1],
        [(end_trait_id - 1), True, 1, 2],  # put on default body
        [0, False, 1, 3],
        [(end_trait_id - 2), True, 1, 4], # put on default eyes
        [(end_trait_id - 3), True, 1, 5], # put on default mouth
        [0, False, 1, 6], 
        [0, False, 1, 7], 
        [(end_trait_id - 4), True, 1, 8], # default clothing
        [0, False, 1, 9], 
        [(end_trait_id - 5), True, 1, 10], # default hair 
        [0, False, 1, 11],
    ]
    supply_before_combine = citizens_contract.getTotalSupply()
    print(f"Citizen # 1: {citizens_contract.tokenIdToCitizen(1)}")
    print(f"Citizen # 1 sex: {citizens_contract.tokenIdToCitizen(1)[3]}")
    market_contract.combine(1, other_male_trait_changes, {"from": account})
    
    # Assert that 5 traits were minted
    assert citizens_contract.getTotalSupply() - supply_before_combine == 5
    
    for count, trait_index in enumerate(trait_indexes, 1):
        assert citizens_contract.tokenIdToCitizen(1)[4][trait_index][0] == end_trait_id - count
        assert citizens_contract.tokenIdToCitizen(1)[4][trait_index][2] is False
        assert citizens_contract.tokenIdToCitizen(1)[4][trait_index][3] is True


def test_changes_with_cost_and_multiple_mints():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    number_of_mints = 3
    dev_account = get_dev_account()
    admin_account = get_account()
    
    mutability_cost = Web3.toWei(0.01, "ether")
    citizens_contract.setMutabilityCost(mutability_cost, {"from": admin_account})
    citizens_contract.setDevRoyalty(50, {"from": dev_account})
    supply_before_combine = citizens_contract.getTotalSupply()

    # use account 2 for the test user
    account = accounts[2]

    
    # *** 
    # Get total cost
    # *** 
    change_cost = citizens_contract.getChangeCost()
    
    # Total cost should be the (# of mints + 1) * change_cost
    # 1 accounts for the additional request_change
    total_cost = change_cost * (number_of_mints + 1)
    
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
        [0, False, 1, 8],
        [0, False, 1, 9],
        [0, False, 1, 10],
        [0, False, 1, 11],
    ]

    # Make sure all traits exist before combine
    
    # Body
    assert citizens_contract.tokenIdToCitizen(0)[4][1][3] is True
    # Eyes...
    assert citizens_contract.tokenIdToCitizen(0)[4][3][3] is True
    # Mouth... 
    assert citizens_contract.tokenIdToCitizen(0)[4][4][3] is True
    
    # ***
    # Combining...
    # ***
    market_contract.combine(0, male_trait_changes, {"from": account})

    # Make sure that the traits came off of the citizen and the default is on
    
    # Body...
    assert citizens_contract.tokenIdToCitizen(0)[4][1][0] == 0
    assert citizens_contract.tokenIdToCitizen(0)[4][1][2] is False
    assert citizens_contract.tokenIdToCitizen(0)[4][1][3] is False
    
    # Eyes...
    assert citizens_contract.tokenIdToCitizen(0)[4][3][0] == 0
    assert citizens_contract.tokenIdToCitizen(0)[4][3][2] is False
    assert citizens_contract.tokenIdToCitizen(0)[4][3][3] is False
    
    # Mouth... 
    assert citizens_contract.tokenIdToCitizen(0)[4][4][0] == 0
    assert citizens_contract.tokenIdToCitizen(0)[4][4][2] is False
    assert citizens_contract.tokenIdToCitizen(0)[4][4][3] is False
    
    # Make sure that 3 tokens were minted
    assert citizens_contract.getTotalSupply() - supply_before_combine == 3
    end_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the new trait has the proper information
    
    for x in range(3):
        assert citizens_contract.tokenIdToTrait(end_trait_id - x) == (
            end_trait_id - x,
            "",
            True,
            True,
            1,
            2,
            0,
        )
        # update the hair's uri
        trait_manager = TraitManager(citizens_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect

        assert new_trait == citizens_contract.tokenIdToTrait(end_trait_id - x)

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

