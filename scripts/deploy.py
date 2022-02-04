from brownie import accounts, Avvenire, network


def deploy_avvenire():
    # Gets the appropiate account
    account = get_account()
    avvenire_contract = Avvenire.deploy("Avvenire", "AVV", {"from": account})
    print(f"Contract deployed to {avvenire_contract.address}")

    transaction1 = avvenire_contract.setMintStatus(True)
    transaction1.wait(1)

    transaction2 = avvenire_contract.safeMint(
        "0x851582A0BC7B2F73F9D3D8AA78AAA43E91AC84D7", 10
    )
    transaction2.wait(1)

    number_minted = avvenire_contract.numberMinted(
        "0x851582A0BC7B2F73F9D3D8AA78AAA43E91AC84D7"
    )
    print(number_minted)


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.load("testNetworkAccount")


def main():
    deploy_avvenire()
