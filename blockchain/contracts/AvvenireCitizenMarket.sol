// SPDX-License-Identifier: MIT

/**
 * @title AvvenireCitizens Trait Management Contract
*/
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "../interfaces/AvvenireCitizenDataInterface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AvvenireCitizenMarket is
    Ownable,
    AvvenireCitizenDataInterface
{
    // store the avvenireCitizens contract
    AvvenireCitizensInterface public avvenireCitizens;

    // struct for storing a trait change
    struct TraitChange {
        uint256 traitId; // setting this to 0 will bind the trait to its default (NULL)
        bool toChange; // will be checked in the for loop to see if the trait needs to be changed
        TraitType traitType;
        Sex sex;
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
     * @notice a function to combine the token's parts
     * this must be payable in order to request changes to each individual component
     * IF the file gets too big, this can be an array, but that would be suboptimal, as it would not require that only one of each trait could be passed
     * @param citizenId for getting the citizen
     * @param traitChanges for getting the traits
    */
    function combine(uint256 citizenId, TraitChanges memory traitChanges) external payable
    {
        // make sure that tokens are mutable
        require(avvenireCitizens.getMutabilityMode(), "Tokens are currently immutable.");

        // check that the citizen's owner is the transaction
        require(avvenireCitizens.ownerOf(citizenId) == msg.sender, "You do not own this token.");


        // have some amount to mint
        uint256 toMint = 0;

        // check each traitId individually --> bind it if a change has been requested
        // each trait's mergability will be checked on binding (to reduce gas costs, access the mapping on the frontend before using this function)
        // if changing and traitId == 0, add it to the list that need to be minted, else bind the trait directly
        if (traitChanges.backgroundChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.backgroundChange);
        }

        if (traitChanges.bodyChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.bodyChange);
        }

        if (traitChanges.tattooChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.tattooChange);
        }

        if (traitChanges.eyesChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.eyesChange);
        }

        if (traitChanges.mouthChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.mouthChange);
        }

        if (traitChanges.maskChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.maskChange);
        }

        if (traitChanges.necklaceChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.necklaceChange);
        }

        if (traitChanges.clothingChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.clothingChange);
        }

        if (traitChanges.earringsChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.earringsChange);
        }

        if (traitChanges.hairChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.hairChange);
        }

        if (traitChanges.effectChange.toChange)
        {
            _bindTrait(citizenId, toMint, traitChanges.effectChange);
        }

        // if there are any to mint, do so
        if (toMint > 0)
        {
            avvenireCitizens.safeMint(tx.origin, toMint);
        }

        // request a character change
    }

    /**
     * @notice bind a trait to a citizen with some light logic
     * ASSUME that the trait has already been checked that it wants to be changed
     * @param citizenId for locating the citizen
     * @param traitChange for indicating how the trait will change
    */
    function _bindTrait(uint256 citizenId, uint256 toMint, TraitChange memory traitChange) internal
    {
        if (traitChange.traitId == 0)
        {
            toMint += 1;
        }
        else
        {
            avvenireCitizens.bind(citizenId, traitChange.traitId, traitChange.sex, traitChange.traitType);
        }

    }

    /**
     * @notice a function to set the avvenireCitizens contract address (only from owner)
    */
    function setAvvenireContractAddress(address contractAddress) external onlyOwner
    {
        avvenireCitizens = AvvenireCitizensInterface(contractAddress);
    }

}


