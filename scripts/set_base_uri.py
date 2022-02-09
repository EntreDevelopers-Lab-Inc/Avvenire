from brownie import AvvenireTest
from scripts.helpful_scripts import get_account


def set_base_uri(baseURI):
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setBaseURI(baseURI, {"from": account})


def main():
    set_base_uri("https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/")
