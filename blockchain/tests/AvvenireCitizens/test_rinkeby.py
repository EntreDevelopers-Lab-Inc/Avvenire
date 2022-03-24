import brownie, pytest

from brownie import AvvenireTest, AvvenireCitizenMarket
from web3 import Web3

from scripts.script_definitions import *
from scripts.helpful_scripts import *
from scripts.auction import *
from scripts.mint import *

DEV_PAYMENT = Web3.toWei(0.5, "ether")

from web3 import Web3

from tools.ChainHandler import CitizenMarketBroker, TraitManager

# always have an auction, and initialize the citizens
@pytest.fixture()
def auction_set():
    setup_auction()

    # make citizens (0, 1, 3 are males; 2, 4 are females)
    # mint_citizens()
    account = get_dev_account()
    mint_citizens_and_initialize(3, account)


# def test_deployment():
#     dev_account = get_dev_account()
#     # uint256 maxPerAddressDuringAuction_,
#     # uint256 maxPerAddressDuringWhiteList_,
#     # uint256 collectionSize_,
#     # uint256 amountForAuctionAndTeam_,
#     # uint256 amountForTeam_,
#     # address devAddress_,
#     # uint256 paymentToDevs_
#     deploy_contract(3, 2, 20, 15, 5, dev_account, DEV_PAYMENT)
#     avvenire_contract = AvvenireTest[-1]
    
#     assert avvenire_contract.maxPerAddressDuringAuction() == 3
#     assert avvenire_contract.maxPerAddressDuringWhiteList() == 2
#     assert avvenire_contract.collectionSize() == 20
#     assert avvenire_contract.amountForAuctionAndTeam() == 15
#     assert avvenire_contract.amountForTeam() == 5
    
# test changing body
def test_new_body(auction_set):
    # keep track of the contracts
    market_contract = AvvenireCitizenMarket[-1]
    citizens_contract = AvvenireCitizens[-1]

    # use account 2 for the test user
    account = get_dev_account()

    # take off the male body
    # request from the market to remove the hair of a citizen
    male_trait_changes = [
        [0, False, 1, 1],
        [0, True, 1, 2],  # put on default body
        [0, False, 1, 3],
        [0, False, 1, 4],
        [0, False, 1, 5],
        [0, False, 1, 6],
        [0, False, 1, 7],
        [0, False, 1, 8],
        [0, False, 1, 9],
        [0, False, 1, 10],
        [0, False, 1, 11],
    ]

    # put on default body
    market_contract.combine(0, male_trait_changes, {"from": account})

    # make sure that the trait came off of the citizen
    assert citizens_contract.tokenIdToCitizen(0)[4][2][2] is False
    assert citizens_contract.tokenIdToCitizen(0)[4][2][3] is False

    # set the new trait id
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the new trait has the proper information
    assert citizens_contract.tokenIdToTrait(new_trait_id) == (
        new_trait_id, '', True, True, 1, 2, 0)

    # update the hair's uri
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()  # this is updating the effect

    assert new_trait == citizens_contract.tokenIdToTrait(new_trait_id)

    # update the male
    broker = CitizenMarketBroker(citizens_contract, 0)
    citizen = broker.update_citizen()

    # ensure that the male on chain is what you set him to
    assert citizen == citizens_contract.tokenIdToCitizen(0)

    # now, put the body on citizen 1
    male_trait_changes = [
        [0, False, 1, 1],
        [new_trait_id, True, 1, 2],  # put on new body
        [0, False, 1, 3],
        [0, False, 1, 4],
        [0, False, 1, 5],
        [0, False, 1, 6],
        [0, False, 1, 7],
        [0, False, 1, 8],
        [0, False, 1, 9],
        [0, False, 1, 10],
        [0, False, 1, 11],
    ]

    print(
        f"citizen before combination: {citizens_contract.tokenIdToCitizen(1)}")

    other_citizen = citizens_contract.tokenIdToCitizen(1)
    
    # Assert the citizen is in fact a male... 
    assert other_citizen[3] == citizen[3]

    # put on the new body
    market_contract.combine(1, male_trait_changes, {"from": account})

    # make sure that the trait is on the citizen
    assert citizens_contract.tokenIdToCitizen(1)[4][2][0] == new_trait_id
    assert citizens_contract.tokenIdToCitizen(1)[4][2][2] is False
    assert citizens_contract.tokenIdToCitizen(1)[4][2][3] is True

    # update the information with a new citizen broker
    broker = CitizenMarketBroker(citizens_contract, 1)
    new_citizen = broker.update_citizen()

    # check that the ipfs data made it
    assert new_citizen == citizens_contract.tokenIdToCitizen(1)

    # make sure the trait is as expected
    new_trait_id = citizens_contract.getTotalSupply() - 1

    # check that the chain trait is uploaded as expected
    assert citizens_contract.tokenIdToTrait(new_trait_id) == (
        new_trait_id, '', True, True, 1, 2, 0)

    # check that the ipfs data uploaded
    trait_manager = TraitManager(citizens_contract, new_trait_id)
    new_trait = trait_manager.update_trait()

    assert new_trait == citizens_contract.tokenIdToTrait(new_trait_id)