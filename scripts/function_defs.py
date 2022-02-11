from brownie import AvvenireTest
from scripts.helpful_scripts import get_account, get_dev_account
from web3 import Web3

# Deploy Function
def deploy_contract():
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


# Set Auction Start Function
# Might be better to get the current time_stamp then add to start_time
def set_auction_start(start_time):
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setAuctionSaleStartTime(start_time, {"from": account})


def set_base_uri(baseURI):
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setBaseURI(baseURI, {"from": account})


def team_mint():
    # Avvenire[-1] returns the most recent deployment
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.teamMint({"from": account})


# All queryable, view functions*


def get_token_uri(tokenID):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.tokenURI(tokenID)


def number_minted():
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    return avvenire_contract.numberMinted(account)


def owner_of(tokenID):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.ownerOf(tokenID)


def get_auction_price(time):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.getAuctionPrice(time)
