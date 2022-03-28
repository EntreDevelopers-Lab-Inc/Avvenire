// SPDX-License-Identifier: MIT

/**
 * @title Avvenire Citizens Data Contract
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chiru-labs/contracts/ERC721A.sol";
// _setOwnersExplicit( ) moved from the ERC721A contract to an extension
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

error TraitTypeDoesNotExist();
error TransferFailed();
error ChangeAlreadyRequested();
error NotSender();

// token mutator changes the way that an ERC721A contract interacts with tokens
contract AvvenireCitizensData is
    Ownable, AvvenireCitizensMappingsInterface {

    // mapping for tokenId to citizen
    mapping(uint256 => Citizen) private tokenIdToCitizen;

    // mapping for tokenId to trait
    mapping(uint256 => Trait) private tokenIdToTrait;

    // mapping for allowing other contracts to interact with this one
    mapping(address => bool) private allowedContracts;

    constructor() Ownable() {
        allowedContracts[msg.sender] = true;
    }

    modifier callerIsAllowed() {
        if (!allowedContracts[msg.sender]) revert NotSender();
        _;
    }

    /**
     * @notice trait setter function 
     * @param _trait the trait to store
     */ 
    function setTrait (Trait memory _trait) external callerIsAllowed {
        tokenIdToTrait[_trait.tokenId] = _trait; 
    }

    /**
     * @notice trait.free setter function
     * @param tokenId the trait's token id
     * @param _free bool to what trait.free should be set to
     */
    function setTraitFreedom(uint256 tokenId, bool _free) external callerIsAllowed {
        tokenIdToTrait[tokenId].free = _free;
    }

    function setCitizen (Citizen memory _citizen) external callerIsAllowed {
        tokenIdToCitizen[_citizen.tokenId] = _citizen;
    }

    /**
     * @notice getter function for traits
     * @param tokenId the trait's tokenId 
     */
    function getTrait (uint256 tokenId) external view returns (Trait memory) {
        return tokenIdToTrait[tokenId];
    }

    /**
     * @notice getter function for citizens
     * @param tokenId the citizen's tokenId 
     */
    function getCitizen (uint256 tokenId) external view returns (Citizen memory) {
        return tokenIdToCitizen[tokenId];
    }

    function setAllowedPermission(address address_, bool setting) external onlyOwner
    {
        allowedContracts[address_] = setting;
    }

    /**
     * @notice returns bool that is true if citizen is initialized; false otherwise
     * @param citizenId the citizen's tokenId 
     */
    function isCitizenInitialized(uint256 citizenId) external view returns (bool) {
        return tokenIdToCitizen[citizenId].sex != Sex.NULL;
    }
} 