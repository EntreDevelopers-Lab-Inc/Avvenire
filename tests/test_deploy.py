import pytest, brownie, time

from brownie import AvvenireTest, chain, network
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *

# devAddress and paymentToDevs are internal.  Can't test

DEV_PAYMENT = Web3.toWei(2, "ether")


def test_deployment():
    dev_account = get_dev_account()
    # uint256 maxPerAddressDuringAuction_,
    # uint256 maxPerAddressDuringWhiteList_,
    # uint256 collectionSize_,
    # uint256 amountForAuctionAndTeam_,
    # uint256 amountForTeam_,
    # address devAddress_,
    # uint256 paymentToDevs_
    deploy_contract(3, 2, 20, 15, 5, dev_account, DEV_PAYMENT)
    avvenire_contract = AvvenireTest[-1]

    assert avvenire_contract.maxPerAddressDuringAuction() == 3
    assert avvenire_contract.maxPerAddressDuringWhiteList() == 2
    assert avvenire_contract.collectionSize() == 20
    assert avvenire_contract.amountForAuctionAndTeam() == 15
    assert avvenire_contract.amountForTeam() == 5
