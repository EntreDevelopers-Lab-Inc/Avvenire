import pytest
import brownie

from brownie import AvvenireAuction, AvvenireCitizens
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

# Public sale starts 4 minutes after auction ends
SALE_START_TIME = 100
PUBLIC_SALE_START_TIME = 240
PUBLIC_SALE_PRICE_ETH = 0.5
WHITELIST_DISCOUNT = 0.3


@pytest.fixture()
def auction_set():
    admin_account = get_account()
    dev_account = get_dev_account()
    deploy_contract(2, 20, 15, 5)
    avvenire_contract = AvvenireAuction[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_citizens_contract.setBaseURI(
        "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/",
        {"from": admin_account},
    )

    # Don't need to pass in chain.time()...
    # Unsure why
    avvenire_contract.setAuctionSaleStartTime(SALE_START_TIME, {"from": admin_account})


@pytest.fixture()
def no_auction():
    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4], accounts[5]]
    admin_account = get_account()
    dev_account = get_dev_account()

    # uint256 maxPerAddressDuringAuction_,
    # uint256 maxPerAddressDuringWhiteList_,
    # uint256 collectionSize_,
    # uint256 amountForAuctionAndTeam_,
    # uint256 amountForTeam_,
    # address devAddress_,
    # uint256 paymentToDevs_
    deploy_contract(2, 20, 15, 5)

    avvenire_contract = AvvenireAuction[-1]
    public_price_wei = Web3.toWei(PUBLIC_SALE_PRICE_ETH, "ether")
    whitelist_price_wei = (1 - WHITELIST_DISCOUNT) * public_price_wei
    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price_wei, public_price_wei, PUBLIC_SALE_START_TIME
    )

    # Seed whitelist...
    avvenire_contract.seedWhitelist(whitelist, {"from": admin_account})


def test_whitelist_mint_1(no_auction):
    avvenire_contract = AvvenireAuction[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    mint_quantity = 2
    # Total cost of mint + .1 ETH for gas
    total_cost = Web3.toWei(
        PUBLIC_SALE_PRICE_ETH * (1 - WHITELIST_DISCOUNT) * mint_quantity, "ether"
    )
    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4], accounts[5]]
    for account in whitelist:
        account_balance_before = account.balance()
        avvenire_contract.whiteListMint(
            mint_quantity, {"from": account, "value": total_cost}
        )

        # Asserts that account minted 2
        assert avvenire_citizens_contract.numberMinted(account) == 2
        assert avvenire_citizens_contract.balanceOf(account) == 2

        # Asserts the account's expected ETH balance
        assert account.balance() == (account_balance_before - total_cost)

        # Asserts that the allowlist[account] == 0
        assert avvenire_contract.allowlist(account) == 0

        # Asserts the account can't whitelist mint again
        with brownie.reverts():
            avvenire_contract.whiteListMint(1, {"from": account, "value": total_cost})


def test_remove_whitelist(no_auction):
    avvenire_contract = AvvenireAuction[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4], accounts[5]]

    for account in whitelist:
        avvenire_contract.removeFromWhitelist(account, {"from": admin_account})

        # Asserts that the allowlist[account] == 0
        assert avvenire_contract.allowlist(account) == 0

        # Makes sure thatremoveFromWhiteList reverts if called on account where allowlist(account) == 0
        with brownie.reverts():
            avvenire_contract.removeFromWhitelist(account, {"from": admin_account})

        # Makes sure the account can't whitelist mint again
        total_cost = Web3.toWei(
            PUBLIC_SALE_PRICE_ETH * (1 - WHITELIST_DISCOUNT), "ether"
        )
        with brownie.reverts():
            avvenire_contract.whiteListMint(1, {"from": account, "value": total_cost})


def test_whitelist_mint_2(no_auction):
    avvenire_contract = AvvenireAuction[-1]
    mint_quantity = 2
    total_cost = Web3.toWei(
        PUBLIC_SALE_PRICE_ETH * (1 - WHITELIST_DISCOUNT) * mint_quantity, "ether"
    )
    account = accounts[1]

    # Mint 1
    avvenire_contract.whiteListMint(1, {"from": account, "value": total_cost})

    # Try to mint another 2
    with brownie.reverts():
        avvenire_contract.whiteListMint(2, {"from": account, "value": total_cost})


def test_whitelist_mint_past_collection_size(auction_set):
    avvenire_contract = AvvenireAuction[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    auction_sale_price_wei = Web3.toWei(1, "ether")
    mint_quantity = 3
    mint_cost = auction_sale_price_wei * mint_quantity
    chain.sleep(SALE_START_TIME + 1)
    chain.mine()

    # Mint all 15 NFTs in the auction
    for count in range(1, 6):
        avvenire_contract.auctionMint(
            mint_quantity,
            {"from": accounts[count], "value": mint_cost},
        )
        assert avvenire_citizens_contract.numberMinted(accounts[count]) == 3

    assert avvenire_citizens_contract.totalSupply() == 15

    # End auction, seed whitelist and mint the remaining 5
    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4], accounts[5]]
    public_price_wei = Web3.toWei(PUBLIC_SALE_PRICE_ETH, "ether")
    whitelist_price_wei = (1 - WHITELIST_DISCOUNT) * public_price_wei
    whitelist_mint_cost = Web3.toWei(
        PUBLIC_SALE_PRICE_ETH * (1 - WHITELIST_DISCOUNT), "ether"
    )

    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price_wei, public_price_wei, PUBLIC_SALE_START_TIME
    )
    avvenire_contract.seedWhitelist(whitelist, {"from": admin_account})
    for account in whitelist:
        avvenire_contract.whiteListMint(
            1,
            {"from": account, "value": whitelist_mint_cost},
        )
        assert avvenire_citizens_contract.numberMinted(account) == 4

    # Try to mint 1 past collection size
    with brownie.reverts():
        avvenire_contract.whiteListMint(
            1, {"from": accounts[1], "value": whitelist_mint_cost}
        )
