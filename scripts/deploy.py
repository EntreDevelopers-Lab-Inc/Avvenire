from brownie import accounts, Avvenire, network


def deploy_avvenire():
    account = get_account


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.load("testNetworkAccount")
