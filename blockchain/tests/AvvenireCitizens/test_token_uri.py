import pytest
import brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, accounts
from web3 import Web3

from tools.ChainHandler import CitizenMarketBroker

from scripts.helpful_scripts import get_account
from scripts.script_definitions import drop_interval
from scripts.auction import setup_auction, perform_auction, end_auction, BASE_URI, LOAD_URI
from scripts.mint import mint_citizens_and_end, mint_citizens_and_initialize


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


# try to get a token uri by interacting with the main contract directly
def test_direct_false_token_change():
    # get the admin account and the contract
    avvenire_citizens_contract = AvvenireCitizens[-1]

    # mint some nfts to account 2
    account = accounts[2]

    # mint some citizens to this account
    mint_citizens_and_end(1, account)

    # user tries to change token directly (hitting modifier)
    with brownie.reverts():
        avvenire_citizens_contract.requestChange(0, {"from": account})

    # try and get the token uri, is it still the base uri?
    token_uri = avvenire_citizens_contract.tokenURI(0)
    assert token_uri == f"{BASE_URI}0"


# get a normal character URI (mint a bunch of them and request if they exist)
def test_base_URI():
    # get the admin account and the contract
    avvenire_citizens_contract = AvvenireCitizens[-1]

    # mint some nfts to account 2
    tokens = 2
    account = accounts[2]
    mint_citizens_and_end(tokens, account)

    for i in range(tokens):
        print(avvenire_citizens_contract.tokenURI(i))
        assert avvenire_citizens_contract.tokenURI(i) == f"{BASE_URI}{i}"


# request a change --> see if it returns the load uri
# mint an NFT --> take the hair off, make sure that it returns a load URI
def test_load_uri():
    # get the contracts
    avvenire_market_contract = AvvenireCitizenMarket[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]

    # mint an nft
    account = accounts[2]

    mint_citizens_and_initialize(2, account)

    # request from the market to remove all the traits of a citizen
    trait_changes = [
        [0, False, 2, 1],  # default background
        [0, True, 2, 2],
        [0, False, 2, 3],  # default tattoo
        [0, True, 2, 4],
        [0, True, 2, 5],
        [0, False, 2, 6],  # no mask
        [0, False, 2, 7],  # no necklaces
        [0, True, 2, 8],
        [0, False, 2, 9],  # no earrings
        [0, True, 2, 10],
        [0, False, 2, 11]  # default effects
    ]

    # request the combination from the market
    print(
        f"Cost to make changes: {avvenire_citizens_contract.getChangeCost()}")
    avvenire_market_contract.combine(
        0, trait_changes, {"from": account, "value": Web3.toWei(0.05, "ether")})

    # check to make sure that the token uri is the loading uri
    assert avvenire_citizens_contract.tokenURI(0) == LOAD_URI
    assert avvenire_citizens_contract.tokenURI(1) == f"{BASE_URI}1"

    # make sure that the contracts did not receive any money (rest got refunded)
    assert avvenire_citizens_contract.balance() == 0
    assert avvenire_market_contract.balance() == 0


# request a change --> have the admin update it
# mint an NFT --> take the hair off, make sure that it returns a load URI
def test_character_uri_after_change():
    # get the contracts
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_market_contract = AvvenireCitizenMarket[-1]

    # mint an nft
    account = accounts[2]
    broker = mint_citizens_and_initialize(2, account)

    # request from the market to remove all the traits of a citizen --> should be stored on the backend --> will be able to set it later
    trait_changes = [
        [0, False, 2, 1],  # default background
        [0, True, 2, 2],
        [0, False, 2, 3],  # default tattoos
        [0, True, 2, 4],
        [0, True, 2, 5],
        [0, False, 2, 6],  # default masks
        [0, False, 2, 7],  # default necklaces
        [0, True, 2, 8],
        [0, False, 2, 9],  # default earrings
        [0, True, 2, 10],
        [0, False, 2, 11]  # default effects
    ]

    # request the combination from the market
    avvenire_market_contract.combine(
        0, trait_changes, {"from": account, "value": Web3.toWei(0.05, "ether")})
    drop_interval(1)

    # this should make all the citizens traits default
    chain_citizen = avvenire_citizens_contract.tokenIdToCitizen(0)
    chain_traits = chain_citizen[4]
    for trait in chain_traits:
        assert trait[3] is False  # make sure it doesn't exist

    # make the changes as an admin
    broker_citizen = broker.update_citizen()

    # get the new citizen from the chain and see if it matches
    chain_citizen = avvenire_citizens_contract.tokenIdToCitizen(0)
    print(chain_citizen)

    # make sure the citizens are the same
    assert broker_citizen == chain_citizen
