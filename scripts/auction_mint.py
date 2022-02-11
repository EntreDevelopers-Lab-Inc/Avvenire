from brownie import AvvenireTest, chain
from scripts.helpful_scripts import get_account
from time import time


def auction_mint(quantity):
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.auctionMint(quantity)
