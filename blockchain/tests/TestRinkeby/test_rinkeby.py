import brownie, pytest

from brownie import AvvenireTest, AvvenireCitizenMarket, AvvenireTraits, AvvenireCitizens
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
@pytest.fixture()
def citizens_minted():
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    account = get_dev_account()
    mint_citizens_and_initialize(3, account)
    end_auction_and_enable_changes()
    
def test_trait_changes_no_cost(citizens_minted):
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
    # Make sure all traits exist before combine
    # ***
    for index in trait_indexes:
        assert data_contract.getCitizen(0)[4][index][3] is True
    
    # ***
    # Combining...
    # ***
    trait_supply_before_combine = traits_contract.getTotalSupply()
    tx = market_contract.combine(0, male_trait_changes, {"from": account})
    tx.wait(3)

    # ***
    # Make sure that the traits came off of the citizen and the default is on
    # ***
    
    for index in trait_indexes:
        assert data_contract.getCitizen(0)[4][index][0] == 0
        assert data_contract.getCitizen(0)[4][index][1] == ''
        # Free
        assert data_contract.getCitizen(0)[4][index][2] is False
        # Exists
        assert data_contract.getCitizen(0)[4][index][3] is False
        # Sex 
        assert data_contract.getCitizen(0)[4][index][4] == 1
    
    # Make sure that 5 tokens were minted
    assert traits_contract.getTotalSupply() - trait_supply_before_combine == 5

    # ***
    # Check that the new traits have the proper information
    # ***

    #Traits indexed @ 1
    end_trait_id = traits_contract.getTotalSupply() 
    
    for x in range(len(trait_indexes)):
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
        # update the uri
        trait_manager = TraitManager(data_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect
        assert new_trait == data_contract.getTrait(end_trait_id - x)
        assert account == citizens_contract.ownerOf(end_trait_id - x)

    # Update the citizen
    broker = CitizenMarketBroker(data_contract, 0)
    citizen = broker.update_citizen()
    
    # ***
    # ensure that the updated citizen matches the on-chain information
    # ***
    assert citizen == data_contract.getCitizen(0)
    
    print (f"end_trait_id: {end_trait_id}")
    print (f"supply_before_combine: {citizens_contract.getTotalSupply()}")

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
    
    supply_before_combine = traits_contract.getTotalSupply()
    tx = market_contract.combine(1, other_male_trait_changes, {"from": account})
    tx.wait(3)
    
    # ***
    # Make sure that the new traits attatched to Citizen 1 are correct 
    # *** 
    start_trait_id = end_trait_id - 4
    
    # update the male
    broker = CitizenMarketBroker(data_contract, 1)
    citizen = broker.update_citizen()
    
    for x, index in enumerate(trait_indexes):
        assert data_contract.getCitizen(1)[4][index][0] == start_trait_id + x
        assert data_contract.getCitizen(1)[4][index][1] > ''
        # Free
        assert data_contract.getCitizen(1)[4][index][2] is False
        # Exists
        assert data_contract.getCitizen(1)[4][index][3] is True
        # Sex should be male
        assert data_contract.getCitizen(1)[4][index][4] == 1
    
        trait_manager = TraitManager(data_contract, start_trait_id + x)
        new_trait = trait_manager.update_trait()  # this is updating the effect
        assert new_trait == data_contract.getTrait(start_trait_id + x)
    
    #*** 
    # Update minted traits
    # ***
    
    #traits indexed @ 1
    end_trait_id = citizens_contract.getTotalSupply() 
    for x in range(len(trait_indexes)):
        assert citizens_contract.getTrait(end_trait_id - x) == (
            end_trait_id - x, 
            "", 
            True, 
            True, 
            1, 
            # Need to start @ 4...
            trait_indexes[4-x] + 1,  # Adjusted for the fact that TraitTypes start at 1 in contract
            1, 
            )
        # update the uri
        trait_manager = TraitManager(data_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect
        assert new_trait == data_contract.getTrait(end_trait_id - x)
        assert account == citizens_contract.ownerOf(end_trait_id - x)

    assert traits_contract.getTotalSupply() - supply_before_combine == 5
    
    # ***
    # ensure that the male on chain is what you set him to
    # ***   
    assert citizen == data_contract.getCitizen(1)   


def test_trait_changes_with_cost():
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]

    # use account 2 for the test user
    admin_account = get_account()
    dev_account = get_dev_account()
    
    citizens_contract.setMutabilityCost(REQUEST_COST, {"from": admin_account})

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
        [0, True, 1, 8], # put on default clothing
        [0, False, 1, 9], 
        [0, True, 1, 10], # put on default hair 
        [0, False, 1, 11],
    ]
    
    # *** 
    # Trait indexes
    # ***
    trait_indexes = [1, 3, 4, 7, 9]
    
    # ***
    # Make sure all traits exist before combine
    # ***
    for index in trait_indexes:
        assert data_contract.getCitizen(0)[4][index][3] is True
    
    # ***
    # Combining...
    # ***
    
    # 6 total changes = 5 total mints + 1 request to change the token
    total_changes = len(trait_indexes) + 1
    change_cost = citizens_contract.getChangeCost()
    total_cost = total_changes * change_cost
    account_balance_before_combine = dev_account.balance()
    
    # ***
    # Combining...
    # ***
    tx = market_contract.combine(0, male_trait_changes, {"from": dev_account, "value": total_cost})
    tx.wait(3)
    
    assert approx(Web3.fromWei(dev_account.balance() - account_balance_before_combine, "ether")) == Web3.fromWei(total_cost, "ether")

    # ***
    # Make sure that the traits came off of the citizen and the default is on
    # ***
    
    for index in trait_indexes:
        assert data_contract.getCitizen(0)[4][index][0] == 0
        assert data_contract.getCitizen(0)[4][index][1] == ''
        # Free
        assert data_contract.getCitizen(0)[4][index][2] is False
        # Exists
        assert data_contract.getCitizen(0)[4][index][3] is False
        # Sex 
        assert data_contract.getCitizen(0)[4][index][4] == 1
    
    # Make sure that 5 tokens were minted
    assert citizens_contract.getTotalSupply() - supply_before_combine == 5

    # ***
    # Check that the new traits have the proper information
    # ***

    #traits indexed @ 1
    end_trait_id = citizens_contract.getTotalSupply()
    
    for x in range(len(trait_indexes)):
        assert citizens_contract.getTrait(end_trait_id - x) == (
            end_trait_id - x, 
            "", 
            True, 
            True, 
            1, 
            # Need to start @ 4...
            trait_indexes[4-x] + 1,  # Adjusted for the fact that TraitTypes start at 1 in contract
            1, 
            )
        # update the uri
        trait_manager = TraitManager(data_contract, end_trait_id - x)
        new_trait = trait_manager.update_trait()  # this is updating the effect

        assert new_trait == data_contract.getTrait(end_trait_id - x)
        assert dev_account == citizens_contract.ownerOf(end_trait_id - x)

    # Update the citizen
    broker = CitizenMarketBroker(data_contract, 0)
    citizen = broker.update_citizen()
    
    # ***
    # ensure that the updated citizen matches the on-chain information
    # ***
    assert citizen == data_contract.getCitizen(0)