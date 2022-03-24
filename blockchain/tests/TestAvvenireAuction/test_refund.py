import pytest
import brownie
import time

from brownie import AvvenireTest, AvvenireCitizens, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

SALE_START_TIME = 100
WHITELIST_DISCOUNT = 0.3
PUBLIC_SALE_START_TIME_FROM_EPOCH = 240


def drop_interval(number_of_drops):
    avvenire_contract = AvvenireTest[-1]
    drop_interval = avvenire_contract.AUCTION_DROP_INTERVAL()
    drop_time = int(drop_interval * number_of_drops)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(drop_time)
        chain.mine(1)
    else:
        time.sleep(drop_time)


@pytest.fixture(autouse=True)
def post_auction(fn_isolation):
    admin_account = get_account()
    dev_account = get_dev_account()
    deploy_contract(3, 2, 20, 15, 5, dev_account, 2)
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]

    # Don't need to pass in chain.time()...
    # Unsure why
    set_auction_start_time(SALE_START_TIME)

    drop_per_step_wei = avvenire_contract.AUCTION_DROP_PER_STEP()
    auction_start_price_wei = avvenire_contract.AUCTION_START_PRICE()

    # Go to auction start time
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 1)

    # Mint one before any drop intervals..
    avvenire_contract.auctionMint(
        1, {"from": accounts[0], "value": auction_start_price_wei}
    )

    # Mint 1 at every drop interval...
    for drops in range(1, 9):
        print(
            f"AvvenireTest Contract balance after minting: {avvenire_contract.balance()}"
        )
        print(
            f"AvvenireCitizens Contract balance after minting: {avvenire_citizens_contract.balance()}"
        )

        drop_interval(1)
        implied_price = auction_start_price_wei - (drop_per_step_wei * drops)

        avvenire_contract.auctionMint(
            1, {"from": accounts[drops], "value": implied_price}
        )


@pytest.fixture()
def public_auction_set():
    avvenire_contract = AvvenireTest[-1]
    admin_account = get_account()
    auction_end_price_wei = avvenire_contract.AUCTION_END_PRICE()
    public_price_wei = avvenire_contract.AUCTION_END_PRICE()
    whitelist_price_wei = (1 - WHITELIST_DISCOUNT) * public_price_wei

    public_sale_start_time = chain.time() + PUBLIC_SALE_START_TIME_FROM_EPOCH
    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price_wei, public_price_wei, public_sale_start_time
    )


def test_refund_before_public_price_set():
    avvenire_contract = AvvenireTest[-1]
    admin_account = get_account()

    with brownie.reverts():
        avvenire_contract.refund(accounts[1], {"from": admin_account})


def test_refund_me_before_public_price_set():
    avvenire_contract = AvvenireTest[-1]

    with brownie.reverts():
        avvenire_contract.refundMe({"from": accounts[1]})


def test_refund(public_auction_set):
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    auction_end_price_wei = avvenire_contract.AUCTION_END_PRICE()

    i = 0
    while avvenire_citizens_contract.numberMinted(accounts[i]) > 0:
        total_paid = avvenire_contract.totalPaid(accounts[i])
        balance_before_refund = accounts[i].balance()
        number_minted = avvenire_citizens_contract.numberMinted(accounts[i])
        actual_cost = number_minted * auction_end_price_wei

        # If total_paid is greater than what they should've paid, refund.  Else, expect exception
        if total_paid > actual_cost:
            avvenire_contract.refund(accounts[i], {"from": admin_account})
            balance_after_refund = accounts[i].balance()
            assert balance_after_refund - balance_before_refund == (
                total_paid - actual_cost
            )

            # Make sure you can't refund a 2nd time...
            with brownie.reverts():
                avvenire_contract.refund(accounts[i], {"from": admin_account})
        else:
            with brownie.reverts():
                avvenire_contract.refund(accounts[i], {"from": admin_account})

        i = i + 1


def test_refund_me(public_auction_set):
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    auction_end_price_wei = avvenire_contract.AUCTION_END_PRICE()

    i = 0
    while avvenire_citizens_contract.numberMinted(accounts[i]) > 0:
        total_paid = avvenire_contract.totalPaid(accounts[i])
        balance_before_refund = accounts[i].balance()
        number_minted = avvenire_citizens_contract.numberMinted(accounts[i])
        actual_cost = number_minted * auction_end_price_wei

        # If total_paid is greater than what they should've paid, refund.  Else, expect exception
        if total_paid > actual_cost:
            print(f"Avvenire contract balance: {avvenire_contract.balance()}")
            avvenire_contract.refundMe({"from": accounts[i]})
            balance_after_refund = accounts[i].balance()
            assert balance_after_refund - balance_before_refund == (
                total_paid - actual_cost
            )

            # Make sure you can't refund a 2nd time...
            with brownie.reverts():
                avvenire_contract.refundMe({"from": accounts[i]})
        else:
            with brownie.reverts():
                avvenire_contract.refundMe({"from": accounts[i]})

        i = i + 1
