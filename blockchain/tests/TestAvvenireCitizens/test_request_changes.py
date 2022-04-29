from doctest import REPORT_UDIFF
from http.client import REQUEST_ENTITY_TOO_LARGE
import pytest
import brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireTraits, AvvenireCitizenMarket, AvvenireCitizensData, accounts
from web3 import Web3
from scripts.helpful_scripts import get_account

from scripts.script_definitions import drop_interval
from scripts.auction import *
from scripts.trading import setup_fees

REQUEST_COST = Web3.toWei(0.25, "ether")


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()


# Single mint from accounts[2]
@pytest.fixture
def single_mint():
    avvenire_auction_contract = AvvenireTest[-1]
    test_account = accounts[2]

    mint_cost = Web3.toWei(1, "ether")
    avvenire_auction_contract.auctionMint(1, {"from": test_account, "value": mint_cost})
    end_auction_and_enable_changes()


# Sets request cost to 0.25 ether
@pytest.fixture
def set_mut_cost():
    admin_account = get_account()
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_citizens_contract.setMutabilityCost(REQUEST_COST, {"from": admin_account})


# try to change a token before it is mutable
def test_token_change_before_mutable():
    avvenire_auction_contract = AvvenireTest[-1]
    avvenire_market_contract = AvvenireCitizenMarket[-1]

    # mint some nfts to account 2
    account = accounts[2]

    # make sure that the gas is less than 5% of the auction
    cost = Web3.toWei(1, "ether")
    avvenire_auction_contract.auctionMint(1, {"from": account, "value": cost})

    # request a change (will later be from an accessory contract) --> should fail, as not mutable
    with brownie.reverts():
        assert avvenire_market_contract.initializeCitizen(0, {"from": account})


# test the change of a non-existed token
def test_non_existent_token_change():
    avvenire_contract = AvvenireTest[-1]
    avvenire_market_contract = AvvenireCitizenMarket[-1]

    # mint some nfts to account 2
    account = accounts[2]

    # make sure that the gas is less than 5% of the auction
    cost = Web3.toWei(1, "ether")
    avvenire_contract.auctionMint(1, {"from": account, "value": cost})

    # end the auction
    end_auction_and_enable_changes()
    drop_interval(1)

    # request a change (will later be from an accessory contract) --> should fail, as not no token exists
    with brownie.reverts():
        assert avvenire_market_contract.initializeCitizen(1, {"from": account})

# Tests request by a non-owner
def test_request_by_nonowner():
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_market_contract = AvvenireCitizenMarket[-1]

    cost = Web3.toWei(1, "ether")
    avvenire_contract.auctionMint(1, {"from": accounts[1], "value": cost})
    avvenire_contract.auctionMint(1, {"from": accounts[2], "value": cost})
    end_auction_and_enable_changes()

    # Confirm that the owner of NFT #0 is Account[1]
    assert avvenire_citizens_contract.ownerOf(0) == accounts[1]
    assert avvenire_citizens_contract.ownerOf(1) == accounts[2]

    with brownie.reverts():
        # Try to change 0 from accounts[2] when the owner is accounts[1]
        assert avvenire_market_contract.initializeCitizen(0, {"from": accounts[2]})


def test_request_after_existing_request(single_mint):
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_market_contract = AvvenireCitizenMarket[-1]
    data_contract = AvvenireCitizensData[-1]
    traits_contract = AvvenireTraits[-1]
    
    mint_account = accounts[2]
    admin_account = get_account()

    # Confirm that the owner of NFT #0 is Account[1]
    assert avvenire_citizens_contract.ownerOf(0) == mint_account

    # Request
    avvenire_market_contract.initializeCitizen(0, {"from": mint_account})
    assert data_contract.getCitizenChangeRequest(0) == True

    # Should throw error... Existing change request outstanding
    with brownie.reverts():
        assert avvenire_market_contract.initializeCitizen(0, {"from": mint_account})
    

    traits_contract.safeMint(admin_account, 1)
    
    new_trait_id = traits_contract.getTotalSupply()
    
    traits_contract.requestChange(new_trait_id, {"from": admin_account}); 
    
    with brownie.reverts():
        traits_contract.requestChange(new_trait_id, {"from": admin_account}); 

    
def test_request_change_with_cost(single_mint, set_mut_cost):
    avvenire_market_contract = AvvenireCitizenMarket[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]
    
    mint_account = accounts[2]

    balance_before_change = mint_account.balance()

    # Try to request change with right amount...
    avvenire_market_contract.initializeCitizen(
        0, {"from": mint_account, "value": REQUEST_COST}
    )

    assert balance_before_change - mint_account.balance() == REQUEST_COST
    assert data_contract.getTokenChangeRequest(0) == True
    assert avvenire_citizens_contract.balance() == REQUEST_COST


def test_request_change_with_underpayment(single_mint, set_mut_cost):
    avvenire_market_contract = AvvenireCitizenMarket[-1]
    data_contract = AvvenireCitizensData[-1]
    mint_account = accounts[2]

    underpayment = REQUEST_COST / 2
    balance_before_change = mint_account.balance()

    # Try to request change with underpayment...
    with brownie.reverts():
        avvenire_market_contract.initializeCitizen(
            0, {"from": mint_account, "value": underpayment}
        )

    assert balance_before_change == mint_account.balance()
    assert data_contract.getTokenChangeRequest(0) == False



def test_request_change_with_overpayment(single_mint, set_mut_cost):
    avvenire_market_contract = AvvenireCitizenMarket[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]
    mint_account = accounts[2]

    balance_before_change = mint_account.balance()
    overpayment = REQUEST_COST * 2

    # Try to request change with right amount...
    avvenire_market_contract.initializeCitizen(
        0, {"from": mint_account, "value": overpayment}
    )

    assert balance_before_change - mint_account.balance() == REQUEST_COST
    assert data_contract.getTokenChangeRequest(0) == True
    assert avvenire_citizens_contract.balance() == REQUEST_COST


def test_request_change_with_dev_royalty(single_mint, set_mut_cost):
    avvenire_market_contract = AvvenireCitizenMarket[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]
    
    mint_account = accounts[2]

    dev_account = get_dev_account()
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_citizens_contract.setDevRoyalty(50, {"from": dev_account})

    change_cost = avvenire_citizens_contract.getChangeCost()
    balance_before_change = mint_account.balance()

    # Try to request change with change cost...
    avvenire_market_contract.initializeCitizen(
        0, {"from": mint_account, "value": change_cost}
    )

    assert balance_before_change - mint_account.balance() == change_cost
    assert data_contract.getTokenChangeRequest(0) == True
    assert avvenire_citizens_contract.balance() == change_cost


# # test paying the royalty
# def test_pay_royalty():
#     # get the contracts
#     citizen_contract = AvvenireCitizens[-1]
#     market_contract = AvvenireCitizenMarket[-1]
#     auction_contract = AvvenireTest[-1]

#     # start the auction and set the fees
#     cost = Web3.toWei(1, "ether")
#     auction_contract.auctionMint(1, {"from": accounts[1], "value": cost})
#     end_auction_and_enable_changes()
#     setup_fees()

#     # get the fees
#     fees = citizen_contract.getChangeCost()

#     # initialize the citizen with the fees
#     market_contract.initializeCitizen(0, {"from": accounts[1], "value": fees})


# test NOT paying the royalty
# def test_not_pay_royalty():
#     # get the contracts
#     market_contract = AvvenireCitizenMarket[-1]
#     auction_contract = AvvenireTest[-1]

#     # start the auction and set the fees
#     cost = Web3.toWei(1, "ether")
#     auction_contract.auctionMint(1, {"from": accounts[1], "value": cost})
#     end_auction_and_enable_changes()
#     setup_fees()

#     # initialize the citizen with the fees
#     with brownie.reverts():
#         market_contract.initializeCitizen(0, {"from": accounts[1]})
