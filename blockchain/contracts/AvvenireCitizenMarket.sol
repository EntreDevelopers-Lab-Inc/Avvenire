// SPDX-License-Identifier: MIT

/**
 * @title AvvenireCitizens Trait Management Contract
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "../interfaces/AvvenireCitizenDataInterface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract AvvenireCitizenMarket is
    Ownable,
    AvvenireCitizenDataInterface,
    ReentrancyGuard
{
    // store the avvenireCitizens contract
    AvvenireCitizensInterface public avvenireCitizens;

    // store the avvenireCitizensData contract
    AvvenireCitizensMappingsInterface public avvenireCitizensData;

    bool isStopped = false;

    // struct for storing a trait change
    struct TraitChange {
        uint256 traitId; // setting this to 0 will bind the trait to its default (NULL)
        bool toChange; // will be checked in the for loop to see if the trait needs to be changed
        Sex sex;
        TraitType traitType;
    }

    // struct for storing an entire bunch of trait changes
    struct TraitChanges {
        TraitChange backgroundChange;
        TraitChange bodyChange;
        TraitChange tattooChange;
        TraitChange eyesChange;
        TraitChange mouthChange;
        TraitChange maskChange;
        TraitChange necklaceChange;
        TraitChange clothingChange;
        TraitChange earringsChange;
        TraitChange hairChange;
        TraitChange effectChange;
    }

    /**
    @notice the constructor of the contract
    @param avvenireCitizensContractAddress the address for the existing avvvenireCitizens contract  
     */
    constructor(
        address avvenireCitizensContractAddress,
        address avvenireCitizensDataAddress
    ) Ownable() {
        avvenireCitizens = AvvenireCitizensInterface(
            avvenireCitizensContractAddress
        );
        avvenireCitizensData = AvvenireCitizensMappingsInterface(
            avvenireCitizensDataAddress
        );
    }

    /**
     * @notice a modifier to check if the citizen can be changed (as all changes require a citizen)
     * @param citizenId represents the citizen's id
     */
    modifier canChange(uint256 citizenId) {
        // make sure that tokens are mutable
        require(
            avvenireCitizens.getMutabilityMode(),
            "Tokens are currently immutable."
        );

        // check that the citizen's owner is the transaction
        require(
            avvenireCitizens.ownerOf(citizenId) == msg.sender,
            "You do not own this token."
        );

        // make sure the citizen has a sex
        require(
            avvenireCitizensData.isCitizenInitialized(citizenId),
            "Must initialize the citizen before changing it."
        );

        _;
    }

    modifier stoppedInEmergency() {
        require(!isStopped, "Emergency stop activated");
        _;
    }

    /**
     * @notice a function to initialize the citizen (just requests a change to set the sex from ipfs)
     * @param citizenId gives the contract a citizen to look for
     */
    function initializeCitizen(uint256 citizenId) external payable stoppedInEmergency {
        // make sure the sex is null, or the citizen has already been initialized
        // this is currently disabled as the enumerables are giving us an odd error
        require(
            avvenireCitizensData.getCitizen(citizenId).sex == Sex.NULL,
            "This citizen has already been initialized."
        );

        uint256 cost = avvenireCitizens.getChangeCost();

        // just request a change --> sets the sex
        // this function will perform all ownership and mutability checks in the other contract
        avvenireCitizens.requestChange{value: cost}(citizenId);

        _refundIfOver(cost);
    }

    /**
     * @notice a function to combine the token's parts
     * this must be payable in order to request changes to each individual component
     * IF the file gets too big, this can be an array, but that would be suboptimal, as it would not require that only one of each trait could be passed
     * in order to decompose traits, just pass all the traits to change as null --> use the frontend to check out what traits are non-defaults --> only change those
     * we never check for the case that there are a bunch of non-changes, as we will do so on the frontend (if someone is interacting with the contract directly, we assume that they know not to request a change with no values)
     * the bind function used actually sets the citizen trait --> all data on chain will be "correct" (note: tokenURIs may need to be set for newly minted tokens)
     * @param citizenId for getting the citizen
     * @param traitChanges for getting the traits
     */
    function combine(uint256 citizenId, TraitChanges memory traitChanges)
        external
        payable
        stoppedInEmergency
        canChange(citizenId)
    {
        // keep track of the ones to mint
        TraitChange[11] memory newTraits;

        // track new trait count
        uint256 toMint;

        // get the cost of requesting one change
        uint256 changeCost = avvenireCitizens.getChangeCost();

        // track the total cost
        uint256 totalCost;

        Trait memory _trait;

        // check each traitId individually --> bind it if a change has been requested
        // each trait's mergability will be checked on binding (to reduce gas costs, access the mapping on the frontend before using this function)
        // if changing and traitId == 0, add it to the list that need to be minted, else bind the trait directly
        if (traitChanges.backgroundChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.background,
                newTraits,
                toMint,
                traitChanges.backgroundChange
            );
        }

        if (traitChanges.bodyChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.body,
                newTraits,
                toMint,
                traitChanges.bodyChange
            );
        }

        if (traitChanges.tattooChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.tattoo,
                newTraits,
                toMint,
                traitChanges.tattooChange
            );
        }

        if (traitChanges.eyesChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.eyes,
                newTraits,
                toMint,
                traitChanges.eyesChange
            );
        }

        if (traitChanges.mouthChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.mouth,
                newTraits,
                toMint,
                traitChanges.mouthChange
            );
        }

        if (traitChanges.maskChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.mask,
                newTraits,
                toMint,
                traitChanges.maskChange
            );
        }

        if (traitChanges.necklaceChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.necklace,
                newTraits,
                toMint,
                traitChanges.necklaceChange
            );
        }

        if (traitChanges.clothingChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.clothing,
                newTraits,
                toMint,
                traitChanges.clothingChange
            );
        }

        if (traitChanges.earringsChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.earrings,
                newTraits,
                toMint,
                traitChanges.earringsChange
            );
        }

        if (traitChanges.hairChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.hair,
                newTraits,
                toMint,
                traitChanges.hairChange
            );
        }

        if (traitChanges.effectChange.toChange) {
            toMint = _bindTrait(
                citizenId,
                avvenireCitizensData.getCitizen(citizenId).traits.effect,
                newTraits,
                toMint,
                traitChanges.effectChange
            );
        }

        // if there are any to mint, do so
        if (toMint > 0) {
            // pay if the change cost is greater than 0
            if (changeCost > 0) {
                // add the amount to mint to the total cost
                totalCost += toMint * changeCost;
            }

            // mint the citzens --> this will only set ownership, will not indicate how to set traits and sexes
            uint256 startTokenId = avvenireCitizens.getTotalSupply();
            avvenireCitizens.safeMint(tx.origin, toMint);
            avvenireCitizens.setOwnersExplicit(toMint);

            // this can be implied with toMint, as we minted exactly that many
            // uint256 pastLimit = avvenireCitizens.getTotalSupply();

            // iterate between the start token id and the limit --> set the trait data to the correct citizen, sex, and trait type --> only the URI will need to be set
            _setTraitData(startTokenId, citizenId, newTraits, toMint);
        }

        // add the amount paid to track the total cost
        totalCost += changeCost;

        // request a character change
        avvenireCitizens.requestChange{value: totalCost}(citizenId);

        // refund the rest of the transaction value if the transaction is over
        // guarantees that msg.value is > totalCost


        // for every new trait to mint, a change will be requested, so send the appropriate amount of eth (do so directly, as safe mint is not payable)
        // if (totalCost > 0) {
        //     (bool success, ) = address(avvenireCitizens).call{value: totalCost}("");
        //     require(success, "Unsuccessful transfer");
        // }
    }

    function _setTraitData(
        uint256 _startTokenId,
        uint256 _citizenId,
        TraitChange[11] memory newTraits,
        uint256 _toMint
    ) internal {
        uint256 tokenId;
        Trait memory _trait;

        for (uint256 i = 0; i < _toMint; i += 1) {
            // get the old trait information (some has been set already)
            tokenId = _startTokenId + i;

            _trait = Trait({
                tokenId: tokenId,
                uri: "",
                free: true,
                exists: true,
                sex: avvenireCitizensData.getCitizen(_citizenId).sex, // make sure to set to the citizen sex, as it will not check on initial trait mint
                traitType: newTraits[i].traitType, // these are checked
                originCitizenId: _citizenId
            });

            // push the trait onto the data contract
            // need to do this to differentiate the new traits created (for which properties)
            // in an accessory (tattoo) contract, if the token URIs are set, we can set those here too, but we don't have them for freshly minted tokens (as the trait's values, not types, are on ipfs and have NO relation to the tokenId)
            // would need to manufacture a relationship between token id and trait uri to bind the uri here
            // still need to update the uri, so keep the update as true
            avvenireCitizens.setTraitData(_trait, true);
        }
    }

    /**
     * @notice bind a trait to a citizen with some light logic
     * ASSUME that the trait has already been checked that it wants to be changed
     * @param citizenId for locating the citizen
     * @param traitChange for indicating how the trait will change
     */
    function _bindTrait(
        uint256 citizenId,
        Trait memory oldTrait,
        TraitChange[11] memory newTraits,
        uint256 toMint,
        TraitChange memory traitChange
    ) internal returns (uint256) {
        // ensure that the traits are of the same type, as it is not checked anywhere else (will be resorted in bind)
        require(
            oldTrait.traitType == traitChange.traitType,
            "Trait type mismatch"
        );

        if ((oldTrait.tokenId == 0) && (oldTrait.exists)) {
            // add the trait to the newTraits array
            newTraits[toMint] = traitChange;

            // increment toMint to make the count accurate
            toMint += 1;
        }

        // always need to bind a new trait, or notthing will happen (after all, this is the core purpose of the function)
        avvenireCitizens.bind(
            citizenId,
            traitChange.traitId,
            traitChange.sex,
            traitChange.traitType
        );

        // return the new mint amount
        return toMint;
    }

    /**
     * @notice a function to set the avvenireCitizens contract address (only from owner)
     */
    function setAvvenireContractAddress(address contractAddress)
        external
        onlyOwner
    {
        avvenireCitizens = AvvenireCitizensInterface(contractAddress);
    }

    function setAvvenireCitizensDataAddress(address contractAddress)
        external
        onlyOwner
    {
        avvenireCitizensData = AvvenireCitizensMappingsInterface(
            contractAddress
        );
    }

    /**
     * @notice refunds excess eth
     * @param cost the amount required for the change
     */
    function _refundIfOver(uint256 cost) internal {
        // make sure the msg sent enough eth
        require(msg.value >= cost, "Insufficient funds.");

        if (msg.value > cost) {
            payable(msg.sender).transfer(msg.value - cost); // pay the user the excess
        }
    }
}
