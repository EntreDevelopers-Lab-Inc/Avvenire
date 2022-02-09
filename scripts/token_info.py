from brownie import AvvenireTest
from scripts.helpful_scripts import get_account

# Tests all functions related to querying info regarding tokens


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


def main():
    print(get_token_uri(2))
    print(number_minted())
    print(owner_of(3))
    print(get_auction_price(0))
