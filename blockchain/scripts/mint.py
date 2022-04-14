import brownie 


from web3 import Web3
from brownie import network, chain, AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, AvvenireCitizensData
from scripts.helpful_scripts import get_account

from tools.ChainHandler import CitizenMarketBroker

from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.script_definitions import drop_interval
from scripts.auction import end_auction_and_enable_changes


# mint some citizens
def mint_citizens(amount, account):
    avvenire_auction_contract = AvvenireTest[-1]
    cost = avvenire_auction_contract.getAuctionPrice() * amount
    tx = avvenire_auction_contract.auctionMint(
        amount, {"from": account, "value": cost})
    
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        tx.wait(3)

# mint some citizens to an account and end it
def mint_citizens_and_end(amount, account):
    mint_citizens(amount, account)
    # end the auction
    end_auction_and_enable_changes()


# mint and initialize
def mint_citizens_and_initialize(amount, account):
    data_contract = AvvenireCitizensData[-1]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    
    mint_citizens(amount, account)
    
    # avvenire_citizens_contract.setOwnersExplicit(amount, {"from": admin_account})
    
    start_index = avvenire_citizens_contract.getTotalSupply() - amount
    # initialize citizen 0
    for i in range(amount):
        # set the citizen's sex
        broker = CitizenMarketBroker(data_contract, i + start_index)
        broker.set_sex()


        
