import pytest, time, brownie

from pytest import approx 
from brownie import AvvenireTest, AvvenireCitizens, chain, network
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
    deploy_contract(3, 2, 20, 15, 5, dev_address, DEV_PAYMENT)
    avvenire_contract = AvvenireTest[-1]
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

def test_withdraw():
    # Initializations
    avvenire_auction_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    dev_account = get_dev_account()

    contract_balance = avvenire_auction_contract.balance()
    # Account balances before withdraw
    admin_before_withdraw_balance = admin_account.balance()
    dev_before_withdraw_balance = dev_account.balance()

    # Withdrawing...
    avvenire_auction_contract.withdrawMoney({"from": admin_account})
    contract_balance_eth = Web3.fromWei(contract_balance, "ether")
    
    print (f"contract_balance: {contract_balance_eth}")
    print (f"contract_balance/20: {contract_balance_eth/20}")

    # Assertions
    assert Web3.fromWei(dev_account.balance(), "ether") == approx(
        Web3.fromWei(dev_before_withdraw_balance + 
                     DEV_PAYMENT + 
                     (contract_balance/20),
                     "ether"))
    assert (
        Web3.fromWei(admin_account.balance(), "ether")
        == approx(Web3.fromWei(
            admin_before_withdraw_balance + 
            (contract_balance * 19/20) - DEV_PAYMENT), 
                  "ether")
    )
    assert avvenire_auction_contract.balance() == 0


def test_multiple_dev_withdraws():
    # Initializations
    avvenire_auction_contract = AvvenireTest[-1]
    admin_account = get_account()
    dev_account = get_dev_account()

    # Withdrawing...
    avvenire_auction_contract.withdrawMoney({"from": admin_account})
    assert avvenire_auction_contract.balance() == 0

    # Devs should now be paid and can't be paid again...
    public_price_wei = Web3.toWei(0.2, "ether")
    whitelist_discount = 0.3
    whitelist_price_wei = public_price_wei * whitelist_discount

    # Set up public auction
    avvenire_auction_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price_wei, public_price_wei, PUBLIC_SALE_START_TIME
    )

    # Setting public sale key...
    avvenire_auction_contract.setPublicSaleKey(PUBLIC_SALE_KEY)

    # Mint 5 @ public price
    for count in range(1, 5):
        avvenire_auction_contract.publicSaleMint(
            1, PUBLIC_SALE_KEY, {"from": accounts[count], "value": public_price_wei}
        )

    contract_balance = avvenire_auction_contract.balance()
    dev_account_balance = dev_account.balance()
    admin_account_balance = admin_account.balance()

    # Testing 2nd withdraw
    avvenire_auction_contract.withdrawMoney({"from": admin_account})

    # Admin account should increase by the full contract_balance...
    assert Web3.fromWei(admin_account.balance(), "ether") == approx(
        Web3.fromWei(admin_account_balance + contract_balance * 0.95)
        , "ether")

    # Dev account balance should be the same
    assert Web3.fromWei(dev_account.balance(), "ether") == approx(
        Web3.fromWei(
        dev_account_balance + (contract_balance/20), 
        "ether"))

    # Contract balance should be 0
    assert avvenire_auction_contract.balance() == 0
