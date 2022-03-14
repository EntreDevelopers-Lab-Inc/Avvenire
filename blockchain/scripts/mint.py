from web3 import Web3
from brownie import AvvenireTest

from scripts.script_definitions import drop_interval
from scripts.auction import end_auction_and_enable_changes


# mint some citizens to an account and end it
def mint_citizens_and_end(amount, account):
    avvenire_auction_contract = AvvenireTest[-1]
    cost = Web3.toWei(amount, "ether")
    avvenire_auction_contract.auctionMint(amount, {"from": account, "value": cost})
    # end the auction
    end_auction_and_enable_changes()