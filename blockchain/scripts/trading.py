from brownie import AvvenireCitizens, Wei
from scripts.helpful_scripts import get_account, get_dev_account
import random


def setup_fees():
    contract = AvvenireCitizens[-1]

    # set a change cost
    change_cost = Wei("0.05 ether")

    # set the change cost and royalty
    contract.setMutabilityCost(change_cost, {'from': get_account()})

    # set a royalty
    royalty = int(random.uniform(0, 1) * 100)

    contract.setDevRoyalty(royalty, {'from': get_dev_account()})
