from brownie import (
    AvvenireAuction,
    AvvenireCitizens,
    AvvenireCitizenMarket,
    AvvenireCitizensData,
    AvvenireTraits,
    AvvenireBlackhole,
    network,
    chain,
)
from scripts.helpful_scripts import (
    get_account,
    get_dev_account,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_server_account,
)
from web3 import Web3

import time

WHITELIST_DISCOUNT = 0.7

# * unless mentioned in a comment, account variables in each script should be assume to be by the owner
# * some account variables need to be set as the user account for actual deployment


# Deployment Script
# Implementation can be changed so that specifications are passed as params instead of intiialized within the function
def deploy_contract(
    max_per_address_during_whitelist,
    collection_size,
    amount_for_auction_and_team,
    amount_for_team
):
    account = get_account()

    # if not Web3.isAddress(devAddress):
    avvenire_data_contract = AvvenireCitizensData.deploy({"from": account})
    
    avvenire_blackhole = AvvenireBlackhole.deploy({"from": account})
    
    avvenire_traits_contract = AvvenireTraits.deploy(
        "AvvenireTraits",
        "AVT",
        "",
        "",
        AvvenireCitizensData[-1].address,
        AvvenireBlackhole[-1].address
        {"from": account},
    )

    # deploy avvenire citizens contract
    avvenire_citizens_contract = AvvenireCitizens.deploy(
        "AvvenireCitizens",
        "AVC",
        "",
        "",
        AvvenireCitizensData[-1].address,
        AvvenireTraits[-1].address,
        {"from": account},
    )
    
    avvenire_data_contract.setAllowedPermission(AvvenireCitizens[-1].address, True, {"from": account})
    avvenire_data_contract.setAllowedPermission(AvvenireTraits[-1].address, True, {"from": account})

    avvenire_market_contract = AvvenireCitizenMarket.deploy(
        AvvenireCitizens[-1].address, AvvenireTraits[-1].address, AvvenireCitizensData[-1].address, {"from": account})

    avvenire_auction_contract = AvvenireAuction.deploy(
        max_per_address_during_whitelist,
        collection_size,
        amount_for_auction_and_team,
        amount_for_team,
        AvvenireCitizens[-1].address,
        {"from": account},
    )

    # allow the test contract to interact with the citizens contract
    avvenire_citizens_contract.setAllowedPermission(
        AvvenireAuction[-1].address, True, {"from": account}
    )

    avvenire_citizens_contract.setAllowedPermission(
        AvvenireCitizenMarket[-1].address, True, {"from": account}
    )
    
    avvenire_traits_contract.setAllowedPermission(
        AvvenireCitizenMarket[-1].address, True, {"from": account}
    )
    
    avvenire_traits_contract.setAllowedPermission(
        AvvenireCitizens[-1].address, True, {"from": account}
    )
    
    server_account = get_server_account()
    avvenire_data_contract.setServer(server_account, {"from": account})
    
def deploy_for_auction(
    max_per_address_during_whitelist,
    collection_size,
    amount_for_auction_and_team,
    amount_for_team
):
    account = get_account()

    # if not Web3.isAddress(devAddress):
    avvenire_data_contract = AvvenireCitizensData.deploy({"from": account})
    
    avvenire_traits_contract = AvvenireTraits.deploy(
        "AvvenireTraits",
        "AVT",
        "",
        "",
        AvvenireCitizensData[-1].address,
        {"from": account},
    )

    # deploy avvenire citizens contract
    avvenire_citizens_contract = AvvenireCitizens.deploy(
        "AvvenireCitizens",
        "AVC",
        "",
        "",
        AvvenireCitizensData[-1].address,
        AvvenireTraits[-1].address,
        {"from": account},
    )
    
    avvenire_data_contract.setAllowedPermission(AvvenireCitizens[-1].address, True, {"from": account})
    avvenire_data_contract.setAllowedPermission(AvvenireTraits[-1].address, True, {"from": account})

    avvenire_auction_contract = AvvenireAuction.deploy(
        max_per_address_during_whitelist,
        collection_size,
        amount_for_auction_and_team,
        amount_for_team,
        AvvenireCitizens[-1].address,
        {"from": account},
    )

    # allow the test contract to interact with the citizens contract
    avvenire_citizens_contract.setAllowedPermission(
        AvvenireAuction[-1].address, True, {"from": account}
    )
    
    avvenire_traits_contract.setAllowedPermission(
        AvvenireCitizens[-1].address, True, {"from": account}
    )



# Logistic Functions*


# Might be better to get the current time_stamp then add to start_time
def set_auction_start_time(time_from_epoch):
    if not isinstance(time_from_epoch, int):
        raise ValueError("Start time isn't an int")
    avvenire_contract = AvvenireAuction[-1]
    account = get_account()

    start_time = None

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        start_time = chain.time() + time_from_epoch
    else:
        w3 = Web3(Web3.HTTPProvider(
            "https://mainnet.infura.io/v3/6f8af8dcbb974218a1f3aec661b9fc30"))
        most_recent_block = w3.eth.get_block("latest")
        start_time = most_recent_block["timestamp"] + time_from_epoch

    avvenire_contract.setAuctionSaleStartTime(start_time, {"from": account})


def set_public_sale_key(public_key):
    if not isinstance(public_key, int):
        raise ValueError("Public key isn't an int")
    avvenire_contract = AvvenireAuction[-1]
    account = get_account()
    avvenire_contract.setPublicSaleKey(public_key, {"from": account})

def end_auction(public_price, whitelist_price, time_from_epoch):
    if not isinstance(public_price, int):
        raise ValueError("ending_auction_price isn't an int")
    if not isinstance(whitelist_price, int):
            raise ValueError("whitelist price isn't int")
    if not isinstance(time_from_epoch, int):
        raise ValueError("time_from_epoch isn't an int")
    
    avvenire_contract = AvvenireAuction[-1]
    account = get_account()

    public_sale_start_time = None

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        public_sale_start_time = chain.time() + time_from_epoch
    else:
        w3 = Web3(Web3.HTTPProvider(
            "https://mainnet.infura.io/v3/6f8af8dcbb974218a1f3aec661b9fc30"))
        most_recent_block = w3.eth.get_block("latest")
        public_sale_start_time = most_recent_block["timestamp"] + time_from_epoch

    avvenire_contract.endAuctionAndSetupNonAuctionSaleInfo(
        whitelist_price, public_price, public_sale_start_time, {
            "from": account}
    )


def drop_interval(number_of_drops):
    avvenire_contract = AvvenireAuction[-1]
    drop_interval = avvenire_contract.AUCTION_DROP_INTERVAL()
    drop_time = int(drop_interval * number_of_drops)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chain.sleep(drop_time)
        chain.mine(1)
    else:
        time.sleep(drop_time)


# Mint Functions
def team_mint(quantity):
    avvenire_contract = AvvenireAuction[-1]
    account = get_account()
    avvenire_contract.teamMint(quantity, {"from": account})


# account variable needs to be changed to user's account
def auction_mint(quantity):
    avvenire_contract = AvvenireAuction[-1]
    account = get_dev_account()
    avvenire_contract.auctionMint(quantity, {"from": account})

# account variable needs to be changed to user's account
def public_mint(quantity, sale_key):
    avvenire_contract = AvvenireAuction[-1]
    account = get_dev_account()
    avvenire_contract.publicSaleMint(quantity, sale_key, {"from": account})

# Whitelist and refund functions
def seed_whitelist(whitelist):
    if not isinstance(whitelist, list):
        raise ValueError("whitelist argument is not a list")

    for index, address_ in enumerate(whitelist):
        if not Web3.isAddress(address_):
            raise ValueError(f"Address #{index} is invalid in whitelist")

    avvenire_contract = AvvenireAuction[-1]
    account = get_account()
    avvenire_contract.seedWhiteList(whitelist, {"from": account})


def remove_from_whitelist(to_remove):
    if not Web3.isAddress(to_remove):
        raise ValueError("to_remove is not a valid address")
    avvenire_contract = AvvenireAuction[-1]
    account = get_account()
    avvenire_contract.removeFromWhitelist(to_remove, {"from": account})


# Refund all function
# @param the list/array that contains the addresses to refund
def refund_all(refund_list):
    if not isinstance(refund_list, list):
        raise ValueError("refund_list is not a list")
    avvenire_contract = AvvenireAuction[-1]
    account = get_account()

    for index, to_refund in enumerate(refund_list):
        # Throws error if to_refund is not an address
        if not Web3.isAddress(to_refund):
            raise ValueError(f"Address #{index} is invalid in refund_list")
        avvenire_contract.refund(to_refund, {"from": account})


# setOwnersExplicit function
# Unsure if I should refactor in the contract to just set all owners explicit...
def set_all_owners_explicit():
    citizens_contract = AvvenireCitizens[-1]
    account = get_account()
    supply = citizens_contract.totalSupply()
    citizens_contract.setOwnersExplicit(supply, {"from": account})



# Withdraw function
def withdraw():
    avvenire_contract = AvvenireAuction[-1]
    account = get_account()
    avvenire_contract.withdrawMoney({"from": account})


# All queryable, view functions*

def turn_off_permissions(): 
    citizen_contract = AvvenireCitizens[-1]
    trait_contract = AvvenireTraits[-1]


def is_public_sale_on(public_price_eth, public_sale_key, public_start_time):
    avvenire_contract = AvvenireAuction[-1]
    public_price_wei = Web3.toWei(public_price_eth, "ether")
    return avvenire_contract.isPublicSaleOn(
        public_price_wei, public_sale_key, public_start_time
    )


def get_auction_price():
    avvenire_contract = AvvenireAuction[-1]
    return avvenire_contract.getAuctionPrice()


def get_base_uri():
    avvenire_contract = AvvenireAuction[-1]
    return avvenire_contract._baseURI()


def get_token_uri(tokenID):
    avvenire_contract = AvvenireAuction[-1]
    return avvenire_contract.tokenURI(tokenID)


def number_minted(account):
    avvenire_contract = AvvenireAuction[-1]
    return avvenire_contract.numberMinted(account)


def owner_of(tokenID):
    avvenire_contract = AvvenireAuction[-1]
    return avvenire_contract.ownerOf(tokenID)
