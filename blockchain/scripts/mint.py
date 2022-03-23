from web3 import Web3
from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket

from tools.ChainHandler import CitizenMarketBroker

from scripts.script_definitions import drop_interval
from scripts.auction import end_auction_and_enable_changes


# mint some citizens
def mint_citizens(amount, account):
    avvenire_auction_contract = AvvenireTest[-1]
    cost = Web3.toWei(amount, "ether")
    avvenire_auction_contract.auctionMint(
        amount, {"from": account, "value": cost})


# mint some citizens to an account and end it
def mint_citizens_and_end(amount, account):
    mint_citizens(amount, account)
    # end the auction
    end_auction_and_enable_changes()


# mint and initialize
def mint_citizens_and_initialize(amount, account):
    avvenire_citizens_contract = AvvenireCitizens[-1]

    mint_citizens_and_end(amount, account)

    # initialize citizen 0
    for i in range(amount):
        # set the citizen's sex
        broker = CitizenMarketBroker(avvenire_citizens_contract, i)
        broker.set_sex()

        drop_interval(1)
