import pytest, time

from brownie import AvvenireTest, chain, network
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
    deploy_contract(3, 2, 20, 15, 5, dev_address, DEV_PAYMENT)
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": account},
    )

    # Don't need to pass in chain.time()...
    # Unsure why
    set_auction_start_time(SALE_START_TIME)


def drop_interval(number_of_drops):
    drop_time = int(60 * 7.5 * number_of_drops)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(drop_time)
        chain.mine(1)
    else:
        time.sleep(drop_time)


def test_set_explicit():
    avvenire_contract = AvvenireTest[-1]
    admin_account = get_account()
    dev_account = get_dev_account()
    avvenire_contract.teamMint({"from": admin_account})
    total_balance = 0

    # Initial price special case...
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    cost = Web3.toWei(1, "ether")

    for count in range(1, 9):
        avvenire_contract.auctionMint(1, {"from": accounts[count], "value": cost})
        drop_interval(1)
        total_balance = total_balance + cost
        cost = cost - Web3.toWei(0.1, "ether")
        assert float(Web3.fromWei(cost, "ether")) == round((1 - count * 0.1), 1)
        assert total_balance == avvenire_contract.balance()
        assert avvenire_contract.numberMinted(accounts[count]) == 1

    # 9 auction mints and 5 team mint = 14 minted total for 5.4 ETH
    # 6 left in collection

    public_price_wei = Web3.toWei(0.2, "ether")
    whitelist_discount = 0.3
    whitelist_price_wei = public_price_wei * whitelist_discount

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
        total_balance = total_balance + public_price_wei
        assert avvenire_contract.numberMinted(accounts[count]) == 2
        assert total_balance == avvenire_contract.balance()

    total_supply = avvenire_contract.totalSupply()
    avvenire_contract.setOwnersExplicit(total_supply)
