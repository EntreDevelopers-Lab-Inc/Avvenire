import pytest, time, brownie

from pytest import approx
from brownie import AvvenireAuction, AvvenireCitizens, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *
from scripts.auction import (
    SALE_START_TIME,
    PUBLIC_SALE_START_TIME,
    PUBLIC_SALE_KEY,
    DEV_PAYMENT,
)


@pytest.fixture(autouse=True)
def perform_auction(fn_isolation):
    dev_address = get_dev_account()
    print(dev_address)
    deploy_contract(2, 20, 15, 5)
    avvenire_contract = AvvenireAuction[-1]
    admin_account = get_account()

    # Don't need to pass in chain.time()...
    # Unsure why
    set_auction_start_time(SALE_START_TIME)

    avvenire_contract.teamMint({"from": admin_account})

    # Move to the auction start time...
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    # Mint an NFT at every interval...
    for count in range(1, 9):
        cost = avvenire_contract.getAuctionPrice()
        avvenire_contract.auctionMint(1, {"from": accounts[count], "value": cost})
        drop_interval(1)
    # 9 auction mints and 5 team mint = 14 minted total for 5.4 ETH


def test_pay_devs():
    avvenire_auction_contract = AvvenireAuction[-1]
    admin_account = get_account()
    avvenire_auction_contract.payDevs({"from": admin_account})


def test_try_pay_devs_twice():
    avvenire_auction_contract = AvvenireAuction[-1]
    admin_account = get_account()
    avvenire_auction_contract.payDevs({"from": admin_account})
    with brownie.reverts():
        avvenire_auction_contract.payDevs({"from": admin_account})


def test_withdraw_before_devs_paid():
    avvenire_auction_contract = AvvenireAuction[-1]
    admin_account = get_account()
    with brownie.reverts():
        avvenire_auction_contract.withdrawMoney({"from": admin_account})


def test_withdraw():
    # Initializations
    avvenire_auction_contract = AvvenireAuction[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    dev_account = get_dev_account()

    contract_balance = avvenire_auction_contract.balance()
    # Account balances before withdraw
    admin_before_withdraw_balance = admin_account.balance()
    dev_before_withdraw_balance = dev_account.balance()

    # Withdrawing...
    avvenire_auction_contract.payDevs({"from": admin_account})
    assert dev_before_withdraw_balance + DEV_PAYMENT == dev_account.balance()

    # Reset contract balance...
    contract_balance = avvenire_auction_contract.balance()

    avvenire_auction_contract.withdrawMoney({"from": admin_account})

    dev_estimation_wei = (
        dev_before_withdraw_balance + DEV_PAYMENT + (contract_balance / 20)
    )
    dev_estimation_eth = Web3.fromWei(dev_estimation_wei, "ether")
    dev_actual = Web3.fromWei(dev_account.balance(), "ether")
    # Assertions
    assert round(dev_actual, 4) == round(dev_estimation_eth, 4)

    admin_estimation = Web3.fromWei(
        admin_before_withdraw_balance + (contract_balance * 19 / 20),
        "ether",
    )
    admin_actual = Web3.fromWei(admin_account.balance(), "ether")
    assert round(admin_estimation, 4) == round(admin_actual, 4)

    assert avvenire_auction_contract.balance() == 0
