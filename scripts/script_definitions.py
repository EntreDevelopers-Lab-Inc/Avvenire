from brownie import AvvenireTest
from scripts.helpful_scripts import get_account, get_dev_account
from web3 import Web3

WHITELIST_DISCOUNT = 0.7

# * unless mentioned in a comment, account variables in each script should be assume to be by the owner
# * some account variables need to be set as the user account for actual deployment


# Deployment Script
# Implementation can be changed so that specifications are passed as params instead of intiialized within the function
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


# Logistic Functions*


# Might be better to get the current time_stamp then add to start_time
def set_auction_start_time(start_time):
    assert isinstance(start_time, int)
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setAuctionSaleStartTime(start_time, {"from": account})

    # setPublicSaleKey


def set_public_sale_key(public_key):
    assert isinstance(public_key, int)
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setPublicSaleKey(public_key, {"from": account})


def set_base_uri(baseURI):
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setBaseURI(baseURI, {"from": account})


def end_auction(ending_auction_price, public_sale_start_time):
    assert isinstance(ending_auction_price, int)
    assert isinstance(public_sale_start_time, int)
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    whitelist_price = int(WHITELIST_DISCOUNT * ending_auction_price)

    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price, ending_auction_price, public_sale_start_time, {"from": account}
    )


# Mint Functions


def team_mint():
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.teamMint({"from": account})


# account variable needs to be changed to user's account
def auction_mint(quantity):
    avvenire_contract = AvvenireTest[-1]
    account = get_dev_account()
    avvenire_contract.auctionMint(quantity, {"from": account})


# account variable needs to be changed to user's account
def whitelist_mint(quantity):
    avvenire_contract = AvvenireTest[-1]
    account = get_dev_account()
    avvenire_contract.whiteListMint(quantity, {"from": account})


# account variable needs to be changed to user's account
def public_mint(quantity, sale_key):
    avvenire_contract = AvvenireTest[-1]
    account = get_dev_account()
    avvenire_contract.publicSaleMint(quantity, sale_key, {"from": account})


# Whitelist and refund functions


def seed_whitelist(whitelist):
    assert isinstance(whitelist, list)

    for address_ in whitelist:
        assert Web3.isAddress(address_)

    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.seedWhiteList(whitelist, {"from": account})


def remove_from_whitelist(to_remove):
    assert Web3.isAddress(to_remove)
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.removeFromWhitelist(to_remove, {"from": account})


# Refund all function
# @param the list/array that contains the addresses to refund
def refund_all(refund_list):
    assert isinstance(refund_list, list)
    avvenire_contract = AvvenireTest[-1]
    account = get_account()

    for to_refund in refund_list:
        # Throws error if to_refund is not an address
        assert Web3.isAddress(to_refund)
        avvenire_contract.refund(to_refund, {"from": account})


# setOwnersExplicit function
# Unsure if I should refactor in the contract to just set all owners explicit...
def set_all_owners_explicit():
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    supply = avvenire_contract.totalSupply()
    avvenire_contract.setOwnersExplicit(supply, {"from": account})


# Withdraw function
def withdraw():
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.withdrawMoney({"from": account})


# All queryable, view functions*


def is_public_sale_on(public_price_eth, public_sale_key, public_start_time):
    avvenire_contract = AvvenireTest[-1]
    public_price_wei = Web3.toWei(public_price_eth, "ether")
    return avvenire_contract.isPublicSaleOn(
        public_price_wei, public_sale_key, public_start_time
    )


def get_auction_price(time):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.getAuctionPrice(time)


def get_base_uri():
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract._baseURI()


def get_token_uri(tokenID):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.tokenURI(tokenID)


def number_minted(account):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.numberMinted(account)


def owner_of(tokenID):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.ownerOf(tokenID)
