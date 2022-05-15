import pytest
import brownie

from brownie import AvvenireAuction, AvvenireCitizens, AvvenireCitizenMarket, AvvenireCitizensData, accounts
from web3 import Web3
from scripts.helpful_scripts import get_account

from scripts.auction import *


@pytest.fixture(autouse=True)
def auction_set(module_isolation):
    setup_auction()
    # perform_auction()


@pytest.fixture
def single_mint():
    avvenire_auction_contract = AvvenireAuction[-1]
    test_account = accounts[2]
    admin_account = get_account()

    mint_cost = Web3.toWei(1, "ether")
    avvenire_auction_contract.auctionMint(
        1, {"from": test_account, "value": mint_cost})
    avvenire_auction_contract.auctionMint(
        1, {"from": admin_account, "value": mint_cost})
    end_auction_and_enable_changes()


@pytest.fixture
def set_server():
    avvenire_citizens_data_contract = AvvenireCitizensData[-1]
    admin_account = get_account()
    avvenire_citizens_data_contract.setServer(
        accounts[2], {"from": admin_account})


# ******* MOST IMPORTANT SETTERS of the avvenire citizens contract ********
# *** MISC SETTERS (citizen stuff is really in binding tests) ****

@pytest.mark.parametrize("bool_", [True, False])
def test_set_mutability_mode(bool_):
    admin_account = get_account()
    avvenire_citizens_data_contract = AvvenireCitizensData[-1]

    avvenire_citizens_data_contract.setMutabilityMode(
        bool_, {"from": admin_account})
    assert avvenire_citizens_data_contract.getMutabilityMode() == bool_


def test_ownership_of():
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_auction_contract = AvvenireAuction[-1]
    admin_account = get_account()
    account = accounts[5]
    cost = Web3.toWei(1, "ether")

    # Mint an NFT at every interval...
    avvenire_auction_contract.auctionMint(1, {"from": account, "value": cost})

    (addr, start_time_stamp, burned) = avvenire_citizens_contract.getOwnershipData(
        0, {"from": admin_account}
    )
    assert addr == account
    assert burned == 0


def test_set_mutability_cost():
    avvenire_citizens_data_contract = AvvenireCitizensData[-1]
    admin_account = get_account()

    cost = Web3.toWei(1, "ether")

    avvenire_citizens_data_contract.setMutabilityCost(
        cost, {"from": admin_account})

    (x, mutability_cost, y) = avvenire_citizens_data_contract.mutabilityConfig()
    assert mutability_cost == cost


@pytest.mark.parametrize("bool_", [True, False])
def test_trade_before_change(bool_):
    avvenire_citizens_data_contract = AvvenireCitizensData[-1]
    admin_account = get_account()
    avvenire_citizens_data_contract.setTokenTradeBeforeChange(
        bool_, {"from": admin_account})
    (x, y, trade_before_change) = avvenire_citizens_data_contract.mutabilityConfig()
    assert trade_before_change == bool_


@pytest.mark.parametrize("bool_", [True, False])
def test_set_allowed_permission(bool_, single_mint):
    avvenire_citizens_data_contract = AvvenireCitizensData[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    avvenire_citizens_data_contract.setAllowedPermission(
        avvenire_citizens_contract, bool_, {"from": admin_account})

    # make sure tokens are mutable
    avvenire_citizens_data_contract.setMutabilityMode(
        True, {"from": admin_account})

    # test requesting a change with both an allowed an disallowed contract (depends on t/f) --> have admin account call the request change function
    if bool_:
        # test if the contract interaction works
        avvenire_citizens_contract.requestChange(
            1, {"from": admin_account})
    else:
        # ensure that the contract interaction fails
        with brownie.reverts():
            avvenire_citizens_contract.requestChange(
                1, {"from": admin_account})


# set server --> access correctly
def test_set_server(single_mint, set_server):
    # try to change the citizen URI of citizen 0
    avvenire_citizens_data_contract = AvvenireCitizensData[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]

    # set the correct uri
    correct_uri = "new uri"
    avvenire_citizens_data_contract.updateCitizenURI(
        0, correct_uri, {'from': accounts[2]})

    # make some assertions
    assert avvenire_citizens_contract.tokenURI(0) == correct_uri


# set server --> access incorrectly
def test_set_server_malicious(single_mint, set_server):
    # try to change the citizen URI of citizen 0
    avvenire_citizens_data_contract = AvvenireCitizensData[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]

    # set the correct uri
    correct_uri = avvenire_citizens_contract.tokenURI(0)

    # make sure the contract reverts
    with brownie.reverts():
        avvenire_citizens_data_contract.updateCitizenURI(
            0, "fake uri", {'from': accounts[1]})

    # make some assertions
    assert avvenire_citizens_contract.tokenURI(0) == correct_uri

# *** Tests below need to have variables set to public to test ***
# ALL PASSED on implementation of 05/04/2022

# def test_set_receiving_address():
#     avvenire_citizens_contract = AvvenireCitizens[-1]
#     admin_account = get_account()
#     receiving_address = accounts[3]
#     avvenire_citizens_contract.setReceivingAddress(
#         receiving_address, {"from": admin_account}
#     )

#     assert avvenire_citizens_contract.receivingAddress() == receiving_address


# def test_dev_config():
#     avvenire_citizens_contract = AvvenireCitizens[-1]
#     admin_account = get_account()
#     dev_address = get_dev_account()
#     dev_royalty = 10
#     avvenire_citizens_contract.changeDevAddress(dev_address, {"from": dev_address})
#     avvenire_citizens_contract.setDevRoyalty(dev_royalty, {"from": dev_address})

#     (config_address, config_royalty) = avvenire_citizens_contract.devConfig()
#     assert config_address == dev_address
#     assert config_royalty == dev_royalty
