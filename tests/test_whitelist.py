import pytest, brownie

from brownie import AvvenireTest
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

# Public sale starts 4 minutes after auction ends
PUBLIC_SALE_START_TIME = 240
PUBLIC_SALE_PRICE_ETH = 0.5
WHITELIST_DISCOUNT = 0.3


@pytest.fixture(autouse=True)
def no_auction(fn_isolation):
    admin_account = get_account()
    dev_account = get_dev_account()

    # uint256 maxPerAddressDuringAuction_,
    # uint256 maxPerAddressDuringWhiteList_,
    # uint256 collectionSize_,
    # uint256 amountForAuctionAndTeam_,
    # uint256 amountForTeam_,
    # address devAddress_,
    # uint256 paymentToDevs_
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

    # Seed whitelist...
    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4]]
    avvenire_contract.seedWhitelist(whitelist, {"from": admin_account})


def test_whitelist_mint():
    avvenire_contract = AvvenireTest[-1]
    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4]]
    mint_quantity = 2
    # Total cost of mint + .1 ETH for gas
    total_mint_cost = Web3.toWei(
        PUBLIC_SALE_PRICE_ETH * (1 - WHITELIST_DISCOUNT) * mint_quantity, "ether"
    )
    gas_cost = Web3.toWei(0.1, "ether")
    total_cost = total_mint_cost + gas_cost

    for account in whitelist:
        account_balance_before = account.balance()
        tx = avvenire_contract.whiteListMint(
            mint_quantity, {"from": account, "value": total_cost}
        )

        # Asserts that account minted 2
        assert avvenire_contract.numberMinted(account) == 2

        # Asserts the account's expected ETH balance
        assert account.balance() == (account_balance_before - total_mint_cost)

        # Asserts that the allowlist[account] == 0
        assert avvenire_contract.allowlist(account) == 0

        # Asserts the account can't whitelist mint again
        with brownie.reverts():
            avvenire_contract.whiteListMint(1, {"from": account, "value": total_cost})


def test_remove_whitelist():
    avvenire_contract = AvvenireTest[-1]
    admin_account = get_account()
    whitelist = [accounts[1], accounts[2], accounts[3], accounts[4]]
    for account in whitelist:
        avvenire_contract.removeFromWhitelist(account, {"from": admin_account})

        # Asserts that the allowlist[account] == 0
        assert avvenire_contract.allowlist(account) == 0

        total_cost = Web3.toWei(
            PUBLIC_SALE_PRICE_ETH * (1 - WHITELIST_DISCOUNT) + 0.1, "ether"
        )

        # Asserts the account can't whitelist mint again
        with brownie.reverts():
            avvenire_contract.whiteListMint(1, {"from": account, "value": total_cost})
