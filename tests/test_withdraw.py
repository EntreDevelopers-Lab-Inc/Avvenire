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
