from brownie import AvvenireTest
from scripts.helpful_scripts import get_account


def team_mint():
    # Avvenire[-1] returns the most recent deployment
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.teamMint({"from": account})


def main():
    team_mint()
