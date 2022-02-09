from brownie import AvvenireTest
from scripts.helpful_scripts import get_account, get_dev_account
from web3 import Web3


def deploy_avvenire():
    account = get_account()

    # Parameters for Avvenire contract:
    # uint256 maxPerAddressDuringAuction_, uint256 maxPerAddressDuringWhiteList_,
    # uint256 collectionSize_, uint256 amountForAuctionAndTeam_,
    # uint256 amountForTeam_, address devAddress_, uint256 paymentToDevs_

    maxPerAddressDuringAuction = 3
    maxPerAddressDuringWhiteList = 2
    collectionSize = 20
    amountForAuctionAndTeam = 15
    amountForTeam = 5
    devAddress = get_dev_account()
    paymentToDevs = Web3.toWei(2, "ether")

    # if not Web3.isAddress(devAddress):

    avvenire_contract = AvvenireTest.deploy(
        maxPerAddressDuringAuction,
        maxPerAddressDuringWhiteList,
        collectionSize,
        amountForAuctionAndTeam,
        amountForTeam,
        devAddress,
        paymentToDevs,
        {"from": account},
    )

    print(f"Contract deployed to {avvenire_contract.address}")


def main():
    deploy_avvenire()
