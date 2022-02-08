from brownie import Avvenire, accounts


def safe_mint(x):
    # Avvenire[-1] returns the most recent deployment
    avvenire_contract = Avvenire[-1]
    # ABI

    # Address
    print(avvenire_contract.safeMint(x))


def main():
    safe_mint()
