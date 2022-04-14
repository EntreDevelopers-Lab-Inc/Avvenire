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
error CallerNotServer();

// token mutator changes the way that an ERC721A contract interacts with tokens
contract AvvenireCitizensData is
    Ownable, AvvenireCitizensMappingsInterface {
    // events
    event SetTrait(uint256 tokenId);
    event SetCitizen(uint256 tokenId);

    // mapping for tokenId to citizen
    mapping(uint256 => Citizen) private tokenIdToCitizen;

    // mapping for tokenId to trait
    mapping(uint256 => Trait) private tokenIdToTrait;

    // mapping for allowing other contracts to interact with this one
    mapping(address => bool) private allowedContracts;

    // Address for server 
    address private serverAddress; 

    constructor() Ownable() {
        allowedContracts[msg.sender] = true;
    }

    modifier callerIsAllowed() {
        if (!allowedContracts[msg.sender]) revert NotSender();
        _;
    }

    modifier callerIsServer() {
        if(msg.sender != serverAddress) revert CallerNotServer(); 
        _;
    }

    function setServer(address _server) external onlyOwner {
        serverAddress = _server;
    }

    /**
     * @notice trait setter function 
     * @param _trait the trait to store
     */ 
    function setTrait (Trait memory _trait) external callerIsAllowed {
        tokenIdToTrait[_trait.tokenId] = _trait; 
        emit SetTrait(_trait.tokenId);
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
        emit SetCitizen(_citizen.tokenId);
    }


    // ***
    // Functions for server
    // *** 
    function setTraitURI(uint256 traitId, string memory _uri) external callerIsServer {
        tokenIdToTrait[traitId].uri = _uri;
    }

    function setCitizenURI(uint256 citizenId, string memory _uri) external callerIsServer {
        tokenIdToCitizen[citizenId].uri = _uri;
    }

    function setCitizenSex(uint256 citizenId, Sex _sex) external callerIsServer {
        tokenIdToCitizen[citizenId].sex = _sex;
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
