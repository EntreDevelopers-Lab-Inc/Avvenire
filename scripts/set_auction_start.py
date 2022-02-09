from brownie import AvvenireTest, chain
from scripts.helpful_scripts import get_account


def set_auction_start(start_time):
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setAuctionSaleStartTime(start_time, {"from": account})


def main():
    print(chain)
