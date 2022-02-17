import pytest, brownie, time

from brownie import AvvenireTest, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

# Public sale starts 2 minutes after auction ends
PUBLIC_SALE_START_TIME = 120
PUBLIC_SALE_PRICE_ETH = 0.5
WHITELIST_DISCOUNT = 0.3


@pytest.fixture(autouse=True)
def no_auction(fn_isolation):
    admin_account = get_account()
    dev_account = get_dev_account()
    deploy_contract(3, 2, 20, 15, 5, dev_account, 2)
    avvenire_contract = AvvenireTest[-1]
    avvenire_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": admin_account},
    )
    public_price_wei = Web3.toWei(PUBLIC_SALE_PRICE_ETH, "ether")
    whitelist_price_wei = (1 - WHITELIST_DISCOUNT) * public_price_wei
    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price_wei, public_price_wei, PUBLIC_SALE_START_TIME
    )

    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4]]
    avvenire_contract.seedWhitelist(whitelist, {"from": admin_account})


def test_whitelist_mint():
    pass
