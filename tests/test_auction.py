from re import A
import pytest, brownie, time

from brownie import AvvenireTest, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

SALE_START_TIME = 100


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    deploy_contract()
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": account},
    )

    # Don't need to pass in chain.time()...
    # Unsure why
    set_auction_start_time(SALE_START_TIME)


def test_mint_before_start():
    # avvenire_contract = AvvenireTest[-1]
    # account = get_dev_account()
    with brownie.reverts():
        # Should throw a VirtualMachineError
        auction_mint(2)


def test_all_prices():

    # Initial price special case...
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    assert Web3.fromWei(get_auction_price(), "ether") == 1

    for drops in range(1, 8):
        drop_time = int(60 * 7.5)
        if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            chain.sleep(drop_time)
            chain.mine(1)
        else:
            time.sleep(60 * 7.5)
        implied_price = round(1 - (0.1 * drops), 1)
        assert float(Web3.fromWei(get_auction_price(), "ether")) == implied_price


def test_auction_mint():
    avvenire_contract = AvvenireTest[-1]
    account = get_dev_account()

    # Set Dutch Auction price to 0.5
    drops = 5
    drop_start = chain.time() + SALE_START_TIME + int(drops * 60 * 7.5)

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # chain.sleep(second_drop_start)
        chain.mine(1, drop_start)
    else:
        time.sleep(drop_start + 5)

    balance_before_mint = account.balance()
    avvenire_contract.auctionMint(
        2, {"from": account, "value": Web3.toWei(1.1, "ether")}
    )
    balance_after_mint = account.balance()

    balance_difference = balance_before_mint - balance_after_mint
    print(f"Balance Difference: {balance_difference}")

    assert Web3.fromWei(balance_difference, "ether") == 1
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        assert avvenire_contract.balanceOf(account) == 2
    assert (
        avvenire_contract.tokenURI(1)
        == "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/1"
    )
