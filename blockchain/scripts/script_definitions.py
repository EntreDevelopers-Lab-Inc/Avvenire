from brownie import (
    AvvenireTest,
    AvvenireCitizens,
    AvvenireCitizenMarket,
    network,
    chain,
)
from scripts.helpful_scripts import (
    get_account,
    get_dev_account,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from web3 import Web3

WHITELIST_DISCOUNT = 0.7

# * unless mentioned in a comment, account variables in each script should be assume to be by the owner
# * some account variables need to be set as the user account for actual deployment


# Deployment Script
# Implementation can be changed so that specifications are passed as params instead of intiialized within the function
def deploy_contract(
    max_per_address_during_auctioin,
    max_per_address_during_whitelist,
    collection_size,
    amount_for_auction_and_team,
    amount_for_team,
    dev_address,
    payment_to_devs,
    number_of_traits,
):
    account = get_account()
    payment_to_devs_ETH = Web3.toWei(payment_to_devs, "ether")

    # if not Web3.isAddress(devAddress):

    # deploy avvenire citizens contract
    avvenire_citizens_contract = AvvenireCitizens.deploy(
        "AvvenireCitizens",
        "AVC",
        "",
        "",
        dev_address,
        collection_size,
        number_of_traits,
        {"from": account},
    )

    avvenire_market_contract = AvvenireCitizenMarket.deploy(
        avvenire_citizens_contract.address, {"from": account}
    )

    # deploy avvenire test contract
    avvenire_contract = AvvenireTest.deploy(
        max_per_address_during_auctioin,
        max_per_address_during_whitelist,
        collection_size,
        amount_for_auction_and_team,
        amount_for_team,
        dev_address,
        payment_to_devs_ETH,
        avvenire_citizens_contract.address,
        {"from": account},
    )

    # allow the test contract to interact with the citizens contract
    avvenire_citizens_contract.setAllowedPermission(
        avvenire_contract.address, True, {"from": account}
    )

    avvenire_citizens_contract.setAllowedPermission(
        avvenire_market_contract.address, True, {"from": account}
    )

    print(f"Contract deployed to {avvenire_contract.address}")


# Logistic Functions*


# Might be better to get the current time_stamp then add to start_time
def set_auction_start_time(time_from_epoch):
    if not isinstance(time_from_epoch, int):
        raise ValueError("Start time isn't an int")
    avvenire_contract = AvvenireTest[-1]
    account = get_account()

    start_time = None

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        start_time = chain.time() + time_from_epoch
    else:
        most_recent_block = Web3.eth.get_block("latest")
        start_time = most_recent_block["timestamp"] + time_from_epoch

    avvenire_contract.setAuctionSaleStartTime(start_time, {"from": account})


def set_public_sale_key(public_key):
    if not isinstance(public_key, int):
        raise ValueError("Public key isn't an int")
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setPublicSaleKey(public_key, {"from": account})


def set_base_uri(baseURI):
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.setBaseURI(baseURI, {"from": account})


def end_auction(ending_auction_price, time_from_epoch):
    if not isinstance(ending_auction_price, int):
        raise ValueError("ending_auction_price isn't an int")
    if not isinstance(time_from_epoch, int):
        raise ValueError("time_from_epoch isn't an int")
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    whitelist_price = int(WHITELIST_DISCOUNT * ending_auction_price)

    public_sale_start_time = None

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        public_sale_start_time = chain.time() + time_from_epoch
    else:
        most_recent_block = Web3.eth.get_block("latest")
        public_sale_start_time = most_recent_block["timestamp"] + time_from_epoch

    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price, ending_auction_price, public_sale_start_time, {"from": account}
    )


def drop_interval(number_of_drops):
    drop_time = int(60 * 7.5 * number_of_drops)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(drop_time)
        chain.mine(1)
    else:
        time.sleep(drop_time)


# Mint Functions


def team_mint():
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.teamMint({"from": account})


# account variable needs to be changed to user's account
def auction_mint(quantity):
    avvenire_contract = AvvenireTest[-1]
    account = get_dev_account()
    avvenire_contract.auctionMint(quantity, {"from": account})


# account variable needs to be changed to user's account
def whitelist_mint(quantity):
    avvenire_contract = AvvenireTest[-1]
    account = get_dev_account()
    avvenire_contract.whiteListMint(quantity, {"from": account})


# account variable needs to be changed to user's account
def public_mint(quantity, sale_key):
    avvenire_contract = AvvenireTest[-1]
    account = get_dev_account()
    avvenire_contract.publicSaleMint(quantity, sale_key, {"from": account})


# Whitelist and refund functions


def seed_whitelist(whitelist):
    if not isinstance(whitelist, list):
        raise ValueError("whitelist argument is not a list")

    for index, address_ in enumerate(whitelist):
        if not Web3.isAddress(address_):
            raise ValueError(f"Address #{index} is invalid in whitelist")

    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.seedWhiteList(whitelist, {"from": account})


def remove_from_whitelist(to_remove):
    if not Web3.isAddress(to_remove):
        raise ValueError("to_remove is not a valid address")
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.removeFromWhitelist(to_remove, {"from": account})


# Refund all function
# @param the list/array that contains the addresses to refund
def refund_all(refund_list):
    if not isinstance(refund_list, list):
        raise ValueError("refund_list is not a list")
    avvenire_contract = AvvenireTest[-1]
    account = get_account()

    for index, to_refund in enumerate(refund_list):
        # Throws error if to_refund is not an address
        if not Web3.isAddress(to_refund):
            raise ValueError(f"Address #{index} is invalid in refund_list")
        avvenire_contract.refund(to_refund, {"from": account})


# setOwnersExplicit function
# Unsure if I should refactor in the contract to just set all owners explicit...
def set_all_owners_explicit():
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    supply = avvenire_contract.totalSupply()
    avvenire_contract.setOwnersExplicit(supply, {"from": account})


# Withdraw function
def withdraw():
    avvenire_contract = AvvenireTest[-1]
    account = get_account()
    avvenire_contract.withdrawMoney({"from": account})


# All queryable, view functions*


def is_public_sale_on(public_price_eth, public_sale_key, public_start_time):
    avvenire_contract = AvvenireTest[-1]
    public_price_wei = Web3.toWei(public_price_eth, "ether")
    return avvenire_contract.isPublicSaleOn(
        public_price_wei, public_sale_key, public_start_time
    )


def get_auction_price():
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.getAuctionPrice()


def get_base_uri():
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract._baseURI()


def get_token_uri(tokenID):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.tokenURI(tokenID)


def number_minted(account):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.numberMinted(account)


def owner_of(tokenID):
    avvenire_contract = AvvenireTest[-1]
    return avvenire_contract.ownerOf(tokenID)
