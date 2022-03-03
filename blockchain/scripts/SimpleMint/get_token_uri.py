#!/usr/bin/python3
from brownie import SimpleMint, accounts, network, config

GAS_LIMIT = 100000

TOKEN_ID = 3


def main():
    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())

    # where are we getting the simple collectible from?
    simple_mint = SimpleMint[len(SimpleMint) - 1]
    print(f"Interacting with contract at {simple_mint.address}")

    uri = simple_mint.tokenURI(
        TOKEN_ID, {"from": dev})

    print(f"token uri: {uri}")
