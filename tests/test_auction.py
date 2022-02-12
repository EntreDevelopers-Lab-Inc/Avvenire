import pytest, brownie, time

from brownie import AvvenireTest, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

SALE_START_TIME = 30


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    deploy_contract()
    set_base_uri("https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/")

    # Auction starts in 30 seconds...
    set_auction_start_time(SALE_START_TIME)


def test_mint_before_start(auction_set):
    # avvenire_contract = AvvenireTest[-1]
    # account = get_dev_account()
    with brownie.reverts():
        # Should throw a VirtualMachineError
        auction_mint(5)


def test_first_drop(auction_set):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME + 5)
    else:
        time.sleep(SALE_START_TIME + 5)
    assert Web3.fromWei(get_auction_price(SALE_START_TIME), "ether") == 1
