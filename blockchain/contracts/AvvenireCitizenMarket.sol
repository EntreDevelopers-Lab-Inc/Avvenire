// SPDX-License-Identifier: MIT

/**
 * @title AvvenireCitizens Trait Management Contract
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "../interfaces/AvvenireCitizenDataInterface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AvvenireCitizenMarket is Ownable, AvvenireCitizenDataInterface {
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
    @notice the constructor of the contract
    @param avvenireCitizensContractAddress the address for the existing avvvenireCitizens contract  
     */
    constructor(address avvenireCitizensContractAddress) {
        avvenireCitizens = AvvenireCitizensInterface(
            avvenireCitizensContractAddress
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

        _;
    }

    /**
     * @notice a function to combine the token's parts
     * this must be payable in order to request changes to each individual component
     * IF the file gets too big, this can be an array, but that would be suboptimal, as it would not require that only one of each trait could be passed
     * in order to decompose traits, just pass all the traits to change as null --> use the frontend to check out what traits are non-defaults --> only change those
     * we never check for the case that there are a bunch of non-changes, as we will do so on the frontend (if someone is interacting with the contract directly, we assume that they know not to request a change with no values)
     * @param citizenId for getting the citizen
     * @param traitChanges for getting the traits
     */
    function combine(uint256 citizenId, TraitChanges memory traitChanges)
        external
        payable
        canChange(citizenId)
    {
        // have some amount to mint
        uint256 toMint;

        // get the cost of requesting one change
        uint256 changeCost = avvenireCitizens.getChangeCost();

        // track the total cost
        uint256 totalCost;

        // check each traitId individually --> bind it if a change has been requested
        // each trait's mergability will be checked on binding (to reduce gas costs, access the mapping on the frontend before using this function)
        // if changing and traitId == 0, add it to the list that need to be minted, else bind the trait directly
        if (traitChanges.backgroundChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.backgroundChange);
        }

        if (traitChanges.bodyChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.bodyChange);
        }

        if (traitChanges.tattooChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.tattooChange);
        }

        if (traitChanges.eyesChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.eyesChange);
        }

        if (traitChanges.mouthChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.mouthChange);
        }

        if (traitChanges.maskChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.maskChange);
        }

        if (traitChanges.necklaceChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.necklaceChange);
        }

        if (traitChanges.clothingChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.clothingChange);
        }

        if (traitChanges.earringsChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.earringsChange);
        }

        if (traitChanges.hairChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.hairChange);
        }

        if (traitChanges.effectChange.toChange) {
            _bindTrait(citizenId, toMint, traitChanges.effectChange);
        }

        // if there are any to mint, do so
        if (toMint > 0) {
            // add the amount to mint to the total cost
            totalCost += toMint * changeCost;

            // for every new trait to mint, a change will be requested, so send the appropriate amount of eth (do so directly, as safe mint is not payable)
            (bool success, ) = address(avvenireCitizens).call{value: totalCost}(
                ""
            );
            require(success, "Insufficient funds for new traits minted.");

            // mint the citzens
            avvenireCitizens.safeMint(tx.origin, toMint);

            //_refundIfOver(totalCost);
        }

        // request a character change
        if (changeCost > 0) {
            // send the value of one change
            avvenireCitizens.requestChange{value: changeCost}(citizenId);

            // add the amount paid to track the total cost
            totalCost += changeCost;

            // refund the rest of the transaction value if the transaction is over
            _refundIfOver(totalCost);
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
        uint256 toMint,
        TraitChange memory traitChange
    ) internal {
        if (traitChange.traitId == 0) {
            toMint += 1;
        } else {
            avvenireCitizens.bind(
                citizenId,
                traitChange.traitId,
                traitChange.sex,
                traitChange.traitType
            );
        }
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

    /**
     * @notice internal function to request a change
     * @param tokenId the id of the token that should be changed
     */
    function _requestChange(uint256 tokenId) internal {
        avvenireCitizens.requestChange(tokenId);
    }

    // ** NEEDS TO BE DELETED LATER **
    // SOLE PURPOSE IS FOR EXPLICIT TESTING
    function requestChange(uint256 tokenId) public {
        _requestChange(tokenId);
    }

    /**
     * @notice refunds excess eth
     * @param cost the amount required for the change
     */
    function _refundIfOver(uint256 cost) internal {
        // make sure the msg sent enough eth
        require(msg.value > cost, "Insufficient funds.");

        if (msg.value > cost) {
            payable(msg.sender).transfer(msg.value - cost); // pay the user the excess
        }
    }
}
