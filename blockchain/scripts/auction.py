from brownie import AvvenireTest, AvvenireCitizens, chain, network, accounts
from web3 import Web3

from constants import BASE_URI, LOAD_URI
from scripts.script_definitions import (
    deploy_contract,
    set_auction_start_time,
    drop_interval,
    end_auction,
)
from scripts.helpful_scripts import (
    get_account,
    get_dev_account,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)

import time

SALE_START_TIME = 10
PUBLIC_SALE_START_TIME = 120
PUBLIC_SALE_KEY = 12345
DEV_PAYMENT = Web3.toWei(0.02, "ether")


def setup_auction():
    admin_account = get_account()
    dev_account = get_dev_account()
    deploy_contract(3, 2, 20, 15, 5, dev_account, 2)
    avvenire_citizens_contract = AvvenireCitizens[-1]

    avvenire_citizens_contract.setBaseURI(BASE_URI, {"from": admin_account})
    avvenire_citizens_contract.setLoadURI(LOAD_URI, {"from": admin_account})

    # Initializations
    set_auction_start_time(SALE_START_TIME)

    # Move to the auction start time...
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)


def perform_auction():
    admin_account = get_account()
    avvenire_contract = AvvenireTest[-1]

    # Initializations
    avvenire_contract.teamMint({"from": admin_account})
    cost = Web3.toWei(1, "ether")

    # Move to the auction start time...
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    # Mint an NFT at every interval...
    for count in range(1, 9):
        avvenire_contract.auctionMint(1, {"from": accounts[count], "value": cost})
        drop_interval(1)

    # 9 auction mints and 5 team mint = 14 minted total for 5.4 ETH

    # 6 left in collection
    public_price_wei = Web3.toWei(0.2, "ether")
    whitelist_discount = 0.3
    whitelist_price_wei = public_price_wei * whitelist_discount

    # Set up public auction
    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price_wei, public_price_wei, PUBLIC_SALE_START_TIME
    )

    # Setting public sale key...
    avvenire_contract.setPublicSaleKey(PUBLIC_SALE_KEY)

    # Mint 6 @ public price
    for count in range(1, 6):
        avvenire_contract.publicSaleMint(
            1, PUBLIC_SALE_KEY, {"from": accounts[count], "value": public_price_wei}
        )


# function to end the character mint
def end_auction_and_enable_changes():
    # get the admin and contract
    admin_account = get_account()
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_auction_contract = AvvenireTest[-1]

    current_auction_price = avvenire_auction_contract.getAuctionPrice()
    end_auction(current_auction_price, 0)

    # set mutability mode to true and end the character mint
    avvenire_citizens_contract.setMutabilityMode(True, {"from": admin_account})
    avvenire_citizens_contract.setCitizenMintActive(False, {"from": admin_account})
