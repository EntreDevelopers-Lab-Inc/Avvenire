import brownie

from brownie import AvvenireAuction, AvvenireCitizenMarket
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

# devAddress and paymentToDevs are internal.  Can't test

DEV_PAYMENT = Web3.toWei(.02, "ether")


def test_deployment():
    dev_account = get_dev_account()
    # uint256 maxPerAddressDuringAuction_,
    # uint256 maxPerAddressDuringWhiteList_,
    # uint256 collectionSize_,
    # uint256 amountForAuctionAndTeam_,
    # uint256 amountForTeam_,
    # address devAddress_,
    # uint256 paymentToDevs_
    deploy_contract(2, 20, 15, 5)
    auction_contract = AvvenireAuction[-1]

    assert auction_contract.maxPerAddressDuringAuction() == 3
    assert auction_contract.maxPerAddressDuringWhiteList() == 2
    assert auction_contract.collectionSize() == 20
    assert auction_contract.amountForAuctionAndTeam() == 15
    assert auction_contract.amountForTeam() == 5

    # Try to get auction price before auction is set...
    with brownie.reverts():
        assert auction_contract.getAuctionPrice()

    # Try to mint before start of auction...
    eth = Web3.toWei(1, "ether")
    with brownie.reverts():
        assert auction_contract.whiteListMint(1, {"from": dev_account, "value": eth})

    with brownie.reverts():
        assert auction_contract.auctionMint(1, {"from": dev_account, "value": eth})
    
    avvenire_market_contract = AvvenireCitizenMarket[-1]
