import pytest
import brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, accounts
from web3 import Web3
from scripts.helpful_scripts import get_account

from scripts.script_definitions import drop_interval
from scripts.auction import *


@pytest.fixture(autouse=True)
def auction_set(fn_isolation):
    setup_auction()
    perform_auction()


def test_set_mutability_mode():
    admin_account = get_account()
    avvenire_citizens_contract = AvvenireCitizens[-1]

    avvenire_citizens_contract.setMutabilityMode(True, {"from": admin_account})
    assert avvenire_citizens_contract.getMutabilityMode() == True

    avvenire_citizens_contract.setMutabilityMode(False, {"from": admin_account})
    assert avvenire_citizens_contract.getMutabilityMode() == False


def test_ownership_of():
    avvenire_citizens_contract = AvvenireCitizens[-1]
    admin_account = get_account()
    avvenire_citizens_contract.getOwnershipData(1, {"from": admin_account})
