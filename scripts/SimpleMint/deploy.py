#!/usr/bin/python3
from brownie import SimpleMint, accounts, network, config

# set the IPFS root link
BASE_URI = 'https://gateway.pinata.cloud/ipfs/QmQyt3UrwuC9yXxmmCHi6jaPGSx4KuFp1tn3zn8m4WFi8h/'
LOAD_URI = 'https://gateway.pinata.cloud/ipfs/QmUJ8u3Rx6GMkbvdRN6edweNgmMr5LNisxgitmPDfWr1fm'

# set the total supply
COLLECTION_SIZE = 100


def main():
    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())

    # this just deploys some contract
    SimpleMint.deploy(BASE_URI, LOAD_URI, COLLECTION_SIZE, {
        "from": dev}, publish_source=True)
