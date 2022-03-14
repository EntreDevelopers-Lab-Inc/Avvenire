import pytest, brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, accounts
from scripts.auction import setup_auction


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()


# Should be unable to safemint from the Avvenire_Citizens contract
def test_safe_mint():
    account = accounts[0]
    avvenire_citizens_contract = AvvenireCitizens[-1]
    with brownie.reverts():
        avvenire_citizens_contract.safeMint(1, {"from": account})
    assert avvenire_citizens_contract.numberMinted(account) == 0
