from brownie import AvvenireTest, accounts


def safe_mint(x):
    # Avvenire[-1] returns the most recent deployment
    avvenire_contract = AvvenireTest[-1]
    # ABI

    # Address
    avvenire_contract.safeMint(x)


def main():
    safe_mint(5)
