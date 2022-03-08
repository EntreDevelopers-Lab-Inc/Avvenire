import pytest
import brownie

from brownie import AvvenireTest, accounts
from web3 import Web3

from scripts.script_definitions import drop_interval
from scripts.auction import setup_auction, end_auction


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()


# try to change a token before it is mutable
def test_token_change_before_mutable():
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

    # request a change (will later be from an accessory contract) --> should fail, as not mutable
    with brownie.reverts():
        assert avvenire_contract.requestChange(0)

# test the change of a non-existed token


def test_non_existent_token_change():
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

    # request a change (will later be from an accessory contract) --> should fail, as not no token exists
    with brownie.reverts():
        assert avvenire_contract.requestChange(1)

# test the rest from an accessory contract
