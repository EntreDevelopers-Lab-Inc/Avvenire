import pytest
import brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, accounts
from web3 import Web3
from scripts.helpful_scripts import get_account

from scripts.script_definitions import drop_interval
from scripts.auction import *


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()


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
        assert avvenire_market_contract.requestChange(0, {"from": account})


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
        assert avvenire_market_contract.requestChange(1, {"from": account})


# REQUEST CHANGE WILL ALWAYS THROW AN ERROR IF THE ACCOUNT IS NOT AN ALLOWED ACCOUNT
# **** THEREFORE NEED TO TEST REQUIRE STATEMENTS FROM THE MARKET CONTRACT ****

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
        assert avvenire_market_contract.requestChange(0, {"from": accounts[2]})


def test_request_after_existing_request():
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_market_contract = AvvenireCitizenMarket[-1]

    cost = Web3.toWei(1, "ether")
    avvenire_contract.auctionMint(1, {"from": accounts[1], "value": cost})
    end_auction_and_enable_changes()

    # Confirm that the owner of NFT #0 is Account[1]
    assert avvenire_citizens_contract.ownerOf(0) == accounts[1]
    avvenire_market_contract.requestChange(0, {"from": accounts[1]})

    # Should throw error... Existing change request outstanding
    with brownie.reverts():
        assert avvenire_market_contract.requestChange(0, {"from": accounts[1]})


# test the rest from an accessory contract