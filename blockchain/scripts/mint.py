from web3 import Web3
from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket

from tools.ChainHandler import CitizenMarketBroker

from scripts.script_definitions import drop_interval
from scripts.auction import end_auction_and_enable_changes


# mint some citizens to an account and end it
def mint_citizens_and_end(amount, account):
    avvenire_auction_contract = AvvenireTest[-1]
    cost = Web3.toWei(
        amount, "ether")
    avvenire_auction_contract.auctionMint(
        amount, {"from": account, "value": cost})
    drop_interval(1)

    # end the auction
    end_auction_and_enable_changes()
    drop_interval(1)


# mint and initialize
def mint_citizens_and_initialize(amount, account):
    avvenire_citizens_contract = AvvenireCitizens[-1]
    avvenire_market_contract = AvvenireCitizenMarket[-1]

    mint_citizens_and_end(amount, account)

    # initialize citizen 0
    avvenire_market_contract.initializeCitizen(0, {'from': account})

    # set the citizen's sex
    broker = CitizenMarketBroker(avvenire_citizens_contract, 0)
    broker.set_sex()

    return broker
