import pytest
import brownie
import time

from brownie import AvvenireTest, AvvenireCitizens, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

SALE_START_TIME = 100


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
def auction_set(fn_isolation):
    admin_account = get_account()
    dev_account = get_dev_account()
    deploy_contract(3, 2, 20, 15, 5, dev_account, 2)
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_citizens_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": admin_account},
    )

    # Don't need to pass in chain.time()...
    # Unsure why
    set_auction_start_time(SALE_START_TIME)


def test_mint_before_start():
    # avvenire_contract = AvvenireTest[-1]
    # account = get_dev_account()
    with brownie.reverts():
        # Should throw a VirtualMachineError
        auction_mint(1)


def test_below_mint_cost():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    account = get_dev_account()
    avvenire_contract = AvvenireTest[-1]
    value = avvenire_contract.AUCTION_START_PRICE() / 2
    
    with brownie.reverts():
        avvenire_contract.auctionMint(1, {"from": account, "value": value})


def test_mint_too_many():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 5)

    avvenire_contract = AvvenireTest[-1]
    cost = avvenire_contract.AUCTION_START_PRICE()
    account = accounts[1]

    # Mint 1
    avvenire_contract.auctionMint(1, {"from": account, "value": cost})

    three_mint_cost = cost * 3
    # Mint 3 more
    with brownie.reverts():
        avvenire_contract.auctionMint(3, {"from": account, "value": three_mint_cost})


def test_auction_mint():
    # Before drops intervals
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    drop_per_step_wei = avvenire_contract.AUCTION_DROP_PER_STEP()
    auction_start_price_wei = avvenire_contract.AUCTION_START_PRICE()

    # Go to auction start time
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 1)

    avvenire_contract.auctionMint(
        1, {"from": accounts[0], "value": auction_start_price_wei}
    )
    assert avvenire_citizens_contract.numberMinted(accounts[0]) == 1
    assert avvenire_citizens_contract.balanceOf(accounts[0]) == 1
    assert (
        avvenire_citizens_contract.tokenURI(0)
        == f"https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/0"
    )

    # During drop intervals
    for drops in range(1, 9):
        drop_interval(1)
        balance_before_mint = accounts[drops].balance()
        implied_price = auction_start_price_wei - (drop_per_step_wei * drops)

        avvenire_contract.auctionMint(
            1, {"from": accounts[drops], "value": implied_price}
        )

        balance_after_mint = accounts[drops].balance()

        assert avvenire_citizens_contract.numberMinted(accounts[drops]) == 1
        assert avvenire_citizens_contract.balanceOf(accounts[drops]) == 1
        assert (
            avvenire_citizens_contract.tokenURI(drops)
            == f"https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/{drops}"
        )
        assert implied_price == balance_before_mint - balance_after_mint


def test_all_prices():
    # Initial price special case...

    # Before drops intervals
    avvenire_contract = AvvenireTest[-1]
    assert avvenire_contract.getAuctionPrice() == avvenire_contract.AUCTION_START_PRICE()
    drop_per_step_wei = avvenire_contract.AUCTION_DROP_PER_STEP()
    auction_start_price_wei = avvenire_contract.AUCTION_START_PRICE()
    auction_end_price_wei = avvenire_contract.AUCTION_END_PRICE()

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(SALE_START_TIME)
        chain.mine(1)
    else:
        time.sleep(SALE_START_TIME + 1)

    # During drop intervals
    for drops in range(1, 9):
        drop_interval(1)
        implied_price = round(auction_start_price_wei - (drop_per_step_wei * drops), 1)
        assert avvenire_contract.getAuctionPrice() == implied_price

    # After all drops...
    drop_interval(1)
    assert avvenire_contract.getAuctionPrice() == auction_end_price_wei


def test_mint_after_auction_amount():
    avvenire_contract = AvvenireTest[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    auction_sale_price_wei = avvenire_contract.AUCTION_START_PRICE()
    mint_quantity = 3
    mint_cost = auction_sale_price_wei * mint_quantity
    chain.sleep(SALE_START_TIME + 1)
    chain.mine()

    # Mint all 20 NFTs in the collection
    for count in range(1, 6):
        avvenire_contract.auctionMint(
            mint_quantity,
            {"from": accounts[count], "value": mint_cost},
        )
        assert avvenire_citizens_contract.numberMinted(accounts[count]) == 3
        assert avvenire_citizens_contract.balanceOf(accounts[count]) == 3

    assert avvenire_citizens_contract.totalSupply() == 15

    with brownie.reverts():
        avvenire_contract.auctionMint(
            mint_quantity,
            {"from": accounts[0], "value": mint_cost},
        )


# # Only testable in local environment...
# def test_refund():
#     avvenire_contract = AvvenireTest[-1]
#     avvenire_citizens_contract = AvvenireCitizens[-1]
#     dev_account = get_dev_account()
#     admin_account = get_account()

#     if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
#         chain.sleep(SALE_START_TIME)
#         chain.mine(1)
#     else:
#         time.sleep(SALE_START_TIME + 5)

#     # Mint the teams portion...
#     avvenire_contract.teamMint()

#     # Mint three NFTs.  Cost is 1 ETH per NFT
#     avvenire_contract.auctionMint(
#         3, {"from": dev_account, "value": Web3.toWei(3.5, "ether")}
#     )

#     # Record before_refund
#     before_refund_balance_ether = Web3.fromWei(dev_account.balance(), "ether")
#     print(f"Balance before refund: {before_refund_balance_ether}")

#     # Drops auction price to 0.5 ETH
#     drop_interval(5)

#     # Mint the rest of the NFTs
#     i = 2
#     quantity_to_mint = 3
#     while (
#         avvenire_citizens_contract.totalSupply() + quantity_to_mint
#         <= avvenire_contract.amountForAuctionAndTeam()
#     ):
#         _account = accounts[i]
#         avvenire_contract.auctionMint(
#             quantity_to_mint, {"from": _account, "value": Web3.toWei(2, "ether")}
#         )
#         i = i + 1

#     # Make sure the price is 0.5
#     public_price = avvenire_contract.getAuctionPrice()

#     # Make sure behavior goes as expected
#     assert public_price == Web3.toWei(0.5, "ether")

#     # Set public price before refund
#     avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(0, public_price, 500)

#     # *** Refunding ***
#     avvenire_contract.refund(dev_account, {"from": admin_account})

#     after_refund_balance_ether = Web3.fromWei(dev_account.balance(), "ether")
#     print(f"Balance after refund {after_refund_balance_ether}")

#     refund_amount = after_refund_balance_ether - before_refund_balance_ether

#     print(f"Refund Amount: {refund_amount}")

#     # Account paid 3 ETH to mint 3 NFTS
#     # Public price is 0.5 ETH.  Should be refunded 1.5 ETH
#     assert refund_amount == 1.5
