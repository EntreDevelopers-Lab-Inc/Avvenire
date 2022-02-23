#!/usr/bin/python3
from brownie import SimpleMint, accounts, network, config

# set the IPFS root link
BASE_URI = 'https://gateway.pinata.cloud/ipfs/QmQyt3UrwuC9yXxmmCHi6jaPGSx4KuFp1tn3zn8m4WFi8h/'


def main():
    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())

    # this just deploys some contract
    SimpleMint.deploy(BASE_URI, {"from": dev}, publish_source=True)
