from smtplib import SMTPServerDisconnected
import pytest, brownie, time

from brownie import AvvenireTest, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

SALE_START_TIME = 30


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    deploy_contract()
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": account},
    )

    # Auction starts in 30 seconds...
    set_auction_start_time(SALE_START_TIME)


def test_mint_before_start():
    # avvenire_contract = AvvenireTest[-1]
    # account = get_dev_account()
    with brownie.reverts():
        # Should throw a VirtualMachineError
        auction_mint(5)


def test_first_drop():

    avvenire_contract = AvvenireTest[-1]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME + 5)
    else:
        time.sleep(SALE_START_TIME + 5)

    # Need to create new block...
    chain.mine()

    assert Web3.fromWei(get_auction_price(SALE_START_TIME), "ether") == 1


def test_second_drop():

    second_drop_start = SALE_START_TIME + int(60 * 7.5) + chain.time()

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.mine(1, second_drop_start)
        chain.sleep(second_drop_start + 15)

    else:
        time.sleep(second_drop_start + 5)

    assert float(Web3.fromWei(get_auction_price(SALE_START_TIME), "ether")) == 0.9
