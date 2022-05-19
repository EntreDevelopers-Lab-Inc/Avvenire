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

    avvenire_contract.teamMint(5, {"from": admin_account})

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

def test_withdraw_functions():
    # Initializations
    avvenire_auction_contract = AvvenireAuction[-1]
    admin_account = get_account()

    contract_balance = avvenire_auction_contract.balance()
    admin_before_withdraw_balance = admin_account.balance()

    
    eth = Web3.toWei(1, "ether")
    
    with brownie.reverts(): 
        avvenire_auction_contract.withdrawQuantity(contract_balance + eth, {"from": admin_account})
    
    amount_to_withdraw = contract_balance / 20
    
    avvenire_auction_contract.withdrawQuantity(amount_to_withdraw, {"from": admin_account})
    
    assert avvenire_auction_contract.balance() == contract_balance - amount_to_withdraw
    assert admin_account.balance() == admin_before_withdraw_balance + amount_to_withdraw
    
    #Reset contract_balance variable...
    contract_balance = avvenire_auction_contract.balance()
    #Reset admin account balance
    admin_before_withdraw_balance = admin_account.balance()
    
    avvenire_auction_contract.withdrawAll({"from": admin_account})

    admin_estimation = Web3.fromWei(
        admin_before_withdraw_balance + contract_balance,
        "ether",
    )
    admin_actual = Web3.fromWei(admin_account.balance(), "ether")
    
    assert round(admin_estimation, 4) == round(admin_actual, 4)
    assert avvenire_auction_contract.balance() == 0
