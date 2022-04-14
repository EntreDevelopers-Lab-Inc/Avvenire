import pytest
import brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, accounts
from web3 import Web3
from scripts.helpful_scripts import get_account

from scripts.auction import *


@pytest.fixture(autouse=True)
def auction_set(module_isolation):
    setup_auction()
    # perform_auction()


@pytest.fixture
def single_mint():
    avvenire_auction_contract = AvvenireTest[-1]
    test_account = accounts[2]

    mint_cost = Web3.toWei(1, "ether")
    avvenire_auction_contract.auctionMint(1, {"from": test_account, "value": mint_cost})
    end_auction_and_enable_changes()


# ******* MOST IMPORTANT SETTERS of the avvenire citizens contract ********
def test_set_trait_data(single_mint):
    avvenire_auction_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()

   

    # Admin account should be "Allowed Contract"

    


# *** MISC SETTERS ****

@pytest.mark.parametrize("bool_", [True, False])
def test_set_mutability_mode(bool_):
    admin_account = get_account()
    avvenire_citizens_contract = AvvenireCitizens[-1]

    avvenire_citizens_contract.setMutabilityMode(bool_, {"from": admin_account})
    assert avvenire_citizens_contract.getMutabilityMode() == bool_


def test_ownership_of():
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_auction_contract = AvvenireTest[-1]
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
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()

    cost = Web3.toWei(1, "ether")

    avvenire_citizens_contract.setMutabilityCost(cost, {"from": admin_account})

    (x, mutability_cost, y) = avvenire_citizens_contract.mutabilityConfig()
    assert mutability_cost == cost


@pytest.mark.parametrize("bool_", [True, False])
def test_trade_before_change(bool_):
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    avvenire_citizens_contract.setTokenTradeBeforeChange(bool_, {"from": admin_account})
    (x, y, trade_before_change) = avvenire_citizens_contract.mutabilityConfig()
    assert trade_before_change == bool_


@pytest.mark.parametrize("bool_", [True, False])
def test_set_allowed_permission(bool_):
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    avvenire_citizens_contract.setTokenTradeBeforeChange(bool_, {"from": admin_account})


# *** Tests below need to have variables set to public to test ***
# ALL PASSED on implementation of 03/13/22

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