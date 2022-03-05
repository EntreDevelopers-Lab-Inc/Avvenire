#!/usr/bin/python3
from brownie import SimpleMint, accounts, network, config

SWITCH = True

NEW_URI = 'https://gateway.pinata.cloud/ipfs/QmUJ8u3Rx6GMkbvdRN6edweNgmMr5LNisxgitmPDfWr1fm'


def main():
    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())

    # where are we getting the simple collectible from?
    simple_mint = SimpleMint[len(SimpleMint) - 1]
    print(f"Interacting with contract at {simple_mint.address}")

    transaction = simple_mint.setBaseURI(
        NEW_URI, {"from": dev})
    transaction.wait(3)
