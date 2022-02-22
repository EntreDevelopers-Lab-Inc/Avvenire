import pytest, brownie, time

from brownie import AvvenireTest, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

PUBLIC_SALE_PRICE_ETH = 0.5
PUBLIC_SALE_START_TIME_FROM_EPOCH = 240
PUBLIC_SALE_KEY = 12345


@pytest.fixture(autouse=True)
def public_mint(fn_isolation):
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

    public_sale_start_time = chain.time() + PUBLIC_SALE_START_TIME_FROM_EPOCH
    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price_wei, public_price_wei, public_sale_start_time
    )
    avvenire_contract.setPublicSaleKey(PUBLIC_SALE_KEY)


def test_public_mint():
    avvenire_contract = AvvenireTest[-1]
    mint_accounts = [accounts[2], accounts[3], accounts[4], accounts[5]]
    public_sale_price_wei = Web3.toWei(PUBLIC_SALE_PRICE_ETH, "ether")
    mint_quantity = 2
    mint_cost = public_sale_price_wei * mint_quantity

    print(chain.time())
    with brownie.reverts():
        # Should throw a VirtualMachineError
        avvenire_contract.publicSaleMint(
            mint_quantity, PUBLIC_SALE_KEY, {"from": accounts[2], "value": mint_cost}
        )

    chain.sleep(PUBLIC_SALE_START_TIME_FROM_EPOCH + 1)
    chain.mine()

    for account in mint_accounts:

        balance_before_mint = account.balance()

        # purposefully overpay for mint...
        avvenire_contract.publicSaleMint(
            mint_quantity, PUBLIC_SALE_KEY, {"from": account, "value": (mint_cost * 2)}
        )

        balance_after_mint = account.balance()

        total_paid = balance_before_mint - balance_after_mint

        assert total_paid == Web3.toWei(1, "ether")
        assert avvenire_contract.numberMinted(account) == 2
