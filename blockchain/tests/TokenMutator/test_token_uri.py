import pytest
import brownie

from brownie import AvvenireTest, AvvenireCitizens, accounts
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
    avvenire_citizens_contract = AvvenireCitizens[-1]

    # check the wrong token uri
    with brownie.reverts():
        # token 20 should have an issue, as only 0-19 are minted
        assert avvenire_citizens_contract.tokenURI(20)


# try to get a token uri after a change has been requested
def test_direct_false_token_change():
    # get the admin account and the contract
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]

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
    with brownie.reverts():
        avvenire_citizens_contract.requestChange(0, {"from": account})
        drop_interval(1)

    # try and get the token uri, is it still the base uri?
    token_uri = avvenire_citizens_contract.tokenURI(0)
    assert token_uri == f"{BASE_URI}0"

# get a normal character URI (mint a bunch of them and request if they exist)


def test_character_URI():
    # get the admin account and the contract
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]

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
        print(avvenire_citizens_contract.tokenURI(i))
        assert avvenire_citizens_contract.tokenURI(i) == f"{BASE_URI}{i}"


# continue with trait swapping, need all traits first
