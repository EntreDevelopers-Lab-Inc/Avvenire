import pytest
import brownie

from brownie import AvvenireTest, accounts
from web3 import Web3

from scripts.helpful_scripts import get_account
from scripts.script_definitions import drop_interval
from scripts.auction import setup_auction, perform_auction, end_auction, BASE_URI, LOAD_URI


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()


# try to get the uri for a non-existent token
def test_fake_token():
    # perform the auction
    perform_auction()

    # get the contract
    avvenire_contract = AvvenireTest[-1]

    # check the wrong token uri
    with brownie.reverts():
        # token 20 should have an issue, as only 0-19 are minted
        assert avvenire_contract.tokenURI(20)


# try to get a token uri after a change has been requested
def test_token_after_change_request():
    # get the admin account and the contract
    admin_account = get_account()
    avvenire_contract = AvvenireTest[-1]

    # mint some nfts to account 2
    account = accounts[2]
    # make sure that the gas is less than 5% of the auction
    cost = Web3.toWei(1, "ether")
    avvenire_contract.auctionMint(1, {"from": account, "value": cost})
    drop_interval(1)

    # end the auction
    end_auction()
    drop_interval(1)

    # change one of the tokens (must be done from admin account, but later from mutability contract)
    avvenire_contract.requestChange(0, {"from": admin_account})
    drop_interval(1)

    # try and get the token uri, is it the load uri?
    token_uri = avvenire_contract.tokenURI(0)
    assert token_uri == LOAD_URI


# get a normal character URI (mint a bunch of them and request if they exist)
def test_character_URI():
    # get the admin account and the contract
    avvenire_contract = AvvenireTest[-1]

    # mint some nfts to account 2
    tokens = 2
    account = accounts[2]
    cost = Web3.toWei(
        tokens, "ether")
    avvenire_contract.auctionMint(tokens, {"from": account, "value": cost})
    drop_interval(1)

    # end the auction
    end_auction()
    drop_interval(1)

    for i in range(tokens):
        print(avvenire_contract.tokenURI(i))
        assert avvenire_contract.tokenURI(i) == f"{BASE_URI}{i}"


# continue with trait swapping, need all traits first
