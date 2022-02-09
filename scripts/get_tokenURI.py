from brownie import AvvenireTest
from scripts.helpful_scripts import get_account


def get_token_uri(tokenID):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.tokenURI(tokenID)


def main():
    print(get_token_uri(2))
