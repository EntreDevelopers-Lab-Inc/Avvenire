import pytest
import time

from brownie import AvvenireTest, AvvenireCitizens, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *
from scripts.auction import SALE_START_TIME, PUBLIC_SALE_START_TIME, PUBLIC_SALE_KEY, DEV_PAYMENT


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    dev_address = get_dev_account()
    print(dev_address)
    deploy_contract(3, 2, 20, 15, 5, dev_address, DEV_PAYMENT)
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    account = get_account()
    avvenire_citizens_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": account},
    )

    # Don't need to pass in chain.time()...
    # Unsure why
    set_auction_start_time(SALE_START_TIME)


# May need to refactor...
# Unit test is way too bloated


def test_withdraw(auction_set):
    # Initializations
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    dev_account = get_dev_account()
    avvenire_contract.teamMint({"from": admin_account})
    total_balance = 0
    cost = Web3.toWei(1, "ether")

    # Move to the auction start time...
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    # Mint an NFT at every interval...
    for count in range(1, 9):
        avvenire_contract.auctionMint(
            1, {"from": accounts[count], "value": cost})
        drop_interval(1)
        total_balance = total_balance + cost
        cost = cost - Web3.toWei(0.1, "ether")
        assert float(Web3.fromWei(cost, "ether")
                     ) == round((1 - count * 0.1), 1)
        assert total_balance == avvenire_contract.balance()
        assert avvenire_citizens_contract.numberMinted(accounts[count]) == 1

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
            1, PUBLIC_SALE_KEY, {
                "from": accounts[count], "value": public_price_wei}
        )
        total_balance = total_balance + public_price_wei
        assert avvenire_citizens_contract.numberMinted(accounts[count]) == 2
        assert total_balance == avvenire_contract.balance()

    # Account balances before withdraw
    admin_before_withdraw_balance = admin_account.balance()
    dev_before_withdraw_balance = dev_account.balance()

    # Withdrawing...
    avvenire_contract.withdrawMoney({"from": admin_account})

    # Assertions
    assert dev_account.balance() == dev_before_withdraw_balance + DEV_PAYMENT
    assert (
        admin_account.balance()
        == admin_before_withdraw_balance + total_balance - DEV_PAYMENT
    )
