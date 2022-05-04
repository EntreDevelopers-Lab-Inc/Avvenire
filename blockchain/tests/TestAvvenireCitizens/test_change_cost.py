import pytest
from brownie import AvvenireCitizens, AvvenireCitizensData, Wei, accounts
from scripts.helpful_scripts import get_account, get_dev_account
from scripts.auction import setup_auction
from scripts.mint import mint_citizens_and_end
import random


@pytest.fixture(autouse=True)
def env_set(fn_isolation):
    setup_auction()
    mint_citizens_and_end(2, accounts[2])


# set the change cost and get it back
def test_change_cost():
    # get the contract
    citizens_contract = AvvenireCitizens[-1]
    data_contract = AvvenireCitizensData[-1]

    # set a change cost
    change_cost = Wei("0.05 ether")

    # set the change cost and royalty
    data_contract.setMutabilityCost(change_cost, {'from': get_account()})

    # check the change cost before the royalty is set
    assert data_contract.getChangeCost() == change_cost

    # set a royalty
    royalty = int(random.uniform(0, 1) * 100)

    citizens_contract.setDevRoyalty(royalty, {'from': get_dev_account()})

    # check if the change cost in the contract is correct
    assert pytest.approx(data_contract.getChangeCost(),
                         change_cost * ((100 + royalty) / 100))
