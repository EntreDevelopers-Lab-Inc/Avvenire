#!/usr/bin/python3
from brownie import SimpleMint, accounts, network, config
import web3
import random

OPENSEA_FORMAT = 'f"https://testnets.opensea.io/assets/{}/{}"'
PRICE = 0.01
GAS_LIMIT = 100000
GAS_PRICE = 100  # artificially high


def main():
    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())

    # where are we getting the simple collectible from?
    simple_mint = SimpleMint[len(SimpleMint) - 1]
    print(f"Interacting with contract at {simple_mint.address}")

    # mint a random amount of NFTs
    amount = random.randint(1, 3)

    # get the gas in eth = gas limt * gas price / gwei per eth
    gas_limit_cost = GAS_LIMIT * GAS_PRICE

    print(f"contract price: {PRICE * amount}")

    # set the cost --> is this the right way to do it?
    # will the contract deduct the total value?
    # unlikely, see dan's --> the contract only pulls the max amount
    total_cost = web3.Web3.toWei(PRICE * amount, "ether")

    # add the gas limit cost
    total_cost += gas_limit_cost

    transaction = simple_mint.mintNFTs(
        amount, {"from": dev, "value": total_cost, "gas_limit": GAS_LIMIT})
    transaction.wait(3)

    print(f"Successfully minted {amount} NFTs.")
