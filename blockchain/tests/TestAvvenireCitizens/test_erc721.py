import pytest, brownie

from brownie import AvvenireTest, AvvenireCitizens, AvvenireCitizenMarket, accounts
from scripts.auction import setup_auction


# *** CURRENT IMPLEMENTATION HAS NO LIMIT ON # OF CITIZENS THAT CAN BE MINTED ***

# @pytest.fixture(autouse=True)
# def auction_set(fn_isolation):
#     setup_auction()


# def test_safe_mint():
#     account = accounts[0]
#     avvenire_citizens_contract = AvvenireCitizens[-1]

#     collection_size = avvenire_citizens_contract.collectionSize()
#     number_of_traits = avvenire_citizens_contract.numberOfTraits()

#     for i in range(number_of_traits + 1):
#         avvenire_citizens_contract.safeMint(account, collection_size, {"from": account})

#     assert (
#         avvenire_citizens_contract.totalSupply()
#         == (number_of_traits + 1) * collection_size
#     )
#     #
#     with brownie.reverts():
#         avvenire_citizens_contract.safeMint(account, 1, {"from": account})
