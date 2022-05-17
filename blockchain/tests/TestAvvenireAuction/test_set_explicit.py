import pytest
import time
import brownie

from brownie import AvvenireAuction, AvvenireCitizens, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

SALE_START_TIME = 100
PUBLIC_SALE_START_TIME = 120
PUBLIC_SALE_KEY = 12345
DEV_PAYMENT = Web3.toWei(2, "ether")


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    dev_address = get_dev_account()
    print(dev_address)
    deploy_contract(2, 20, 15, 5)
    avvenire_contract = AvvenireAuction[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    account = get_account()
    avvenire_citizens_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": account},
    )

    # Don't need to pass in chain.time()...
    # Unsure why
    set_auction_start_time(SALE_START_TIME)

def test_explicit_no_supply():
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    total_supply = avvenire_citizens_contract.totalSupply()
    with brownie.reverts():
        avvenire_citizens_contract.setOwnersExplicit(
            total_supply, {"from:": admin_account}
        )

def test_set_explicit():
    avvenire_contract = AvvenireAuction[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    avvenire_contract.teamMint({"from": admin_account})

    # Initial price special case...
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    for count in range(1, 9):
        cost = avvenire_contract.getAuctionPrice()
        avvenire_contract.auctionMint(1, {"from": accounts[count], "value": cost})
        drop_interval(1)

    # 9 auction mints and 5 team mint = 14 minted total 

    total_supply = avvenire_citizens_contract.totalSupply()
    avvenire_citizens_contract.setOwnersExplicit(total_supply, {"from:": admin_account})
