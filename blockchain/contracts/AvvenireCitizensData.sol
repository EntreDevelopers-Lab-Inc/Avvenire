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

    function setTrait (Trait memory _trait) external callerIsAllowed {
        tokenIdToTrait[_trait.tokenId] = _trait; 
    }

    function setTraitFreedom(uint256 tokenId, bool _free) external callerIsAllowed {
        tokenIdToTrait[tokenId].free = _free;
    }

    function setCitizen (Citizen memory _citizen) external callerIsAllowed {
        tokenIdToCitizen[_citizen.tokenId] = _citizen;
    }

    // *******
    // TEST FIRST...
    // IF WORKS, SET INDIVIDUAL SETTERS IN BIND of ERC721A contract
    //**** 

    function getTrait (uint256 tokenId) external view returns (Trait memory) {
        return tokenIdToTrait[tokenId];
    }

    function getCitizen (uint256 tokenId) external view returns (Citizen memory) {
        return tokenIdToCitizen[tokenId];
    }

    function setAllowedPermission(address address_, bool setting) external onlyOwner
    {
        allowedContracts[address_] = setting;
    }

    function isCitizenInitialized(uint256 citizenId) external view returns (bool) {
        return tokenIdToCitizen[citizenId].sex != Sex.NULL;
    }
} 