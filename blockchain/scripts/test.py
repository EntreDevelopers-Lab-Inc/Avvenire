from brownie import (
    AvvenireTest,
    AvvenireCitizens,
    AvvenireCitizenMarket,
    network,
    chain,
)

from scripts.helpful_scripts import get_dev_account, get_account

account = get_account()
dev_address = get_dev_account()

avvenire_citizens_contract = AvvenireCitizens.deploy(
        "AvvenireCitizens",
        "AVC",
        "",
        "",
        dev_address,
        {"from": account},
    )

print(AvvenireCitizens[-1])
print(AvvenireCitizens[-1].address)