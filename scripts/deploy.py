from brownie import accounts, Avvenire, network


def deploy_avvenire():
    # Gets the appropiate account
    account = get_account()
    avvenire_contract = Avvenire.deploy({"from": account})

    transaction1 = avvenire_contract.setMintStatus(True)
    transaction1.wait(1)

    transaction2 = avvenire_contract.safeMint(10)
    transaction2.wait(1)

    number_minted = avvenire_contract.numberMinted(account)
    print(number_minted)


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.load("testNetworkAccount")


def main():
    deploy_avvenire()
