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
    event MutabilityModeConfigured(bool configuration);
    event MutabilityCostConfigured(uint256 configuration);

    MutabilityConfig public mutabilityConfig;

    // mapping for tokenId to citizen
    mapping(uint256 => Citizen) private tokenIdToCitizen;

    // mapping for tokenId to trait
    mapping(uint256 => Trait) private tokenIdToTrait;

    // mapping for allowing other contracts to interact with this one
    mapping(address => bool) private allowedContracts;

    // mapping for citizen change requests
    mapping(uint256 => bool) public citizenChangeRequests;

    // mapping for trait change requests 
    mapping(uint256 => bool) public traitChangeRequests;

    // Address for server 
    address private serverAddress; 

    bool public isStopped; 

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

    modifier stoppedInEmergency {
        require(!isStopped, "Emergency stop active");
        _;
    }

    /**
     * @notice setter for emergency stop
     */
    function setEmergencyStop(bool _isStopped) external onlyOwner {
        isStopped = _isStopped; 
    }


    function setCitizenChangeRequest(uint256 citizenId, bool changeRequest) external callerIsAllowed {
        citizenChangeRequests[citizenId] = changeRequest; 
    }

    function getCitizenChangeRequest(uint256 citizenId) external view returns(bool)  {
        return citizenChangeRequests[citizenId]; 
    }

    function setTraitChangeRequest (uint256 traitId, bool changeRequest) external callerIsAllowed {
        traitChangeRequests[traitId] = changeRequest; 
    }

    function getTraitChangeRequest(uint256 traitId) external view returns(bool)  {
        return traitChangeRequests[traitId];
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
    function updateTraitSexAndURI(uint256 traitId, Sex _sex, string memory _uri) external callerIsServer stoppedInEmergency{
        tokenIdToTrait[traitId].uri = _uri;
        tokenIdToTrait[traitId].sex = _sex;
        traitChangeRequests[traitId] = false;
    }

    function updateCitizenURI(uint256 citizenId, string memory _uri) external callerIsServer stoppedInEmergency {
        tokenIdToCitizen[citizenId].uri = _uri;
        citizenChangeRequests[citizenId] = false; 
    }

    function setCitizenSex(uint256 citizenId, Sex _sex) external callerIsServer stoppedInEmergency {
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

    /** @notice a function that gives the change cost
     */
    function getChangeCost() external view returns (uint256) {
        return mutabilityConfig.mutabilityCost;
    }

    /**
     * @notice returns bool that is true if mutability mode is on
     */
    function getMutabilityMode() external view returns (bool) {
        return mutabilityConfig.mutabilityMode;
    }

    /**
     * @notice returns bool that is true if you can trade before a change takes place
     */
    function getTradeBeforeChange() external view returns (bool) {
        return mutabilityConfig.tradeBeforeChange;
    }

    /**
     * @notice a getter function that returns the mutabilityConfig
     */
    function getMutabilityConfig() external view returns (MutabilityConfig memory) {
        return mutabilityConfig;
    }

    /**
     * @notice Sets the mutability of the contract (whether changes are accepted)
     * @param mutabilityMode_ allows the contract owner to change the mutability of the tokens
     */
    function setMutabilityMode(bool mutabilityMode_) external onlyOwner {
        // set te new mutability mode to this boolean
        mutabilityConfig.mutabilityMode = mutabilityMode_;

        emit MutabilityModeConfigured(mutabilityMode_);
    }

    
    /**
     * @notice Sets the mutability cost
     * @param mutabilityCost_ is the new mutability cost
     */
    function setMutabilityCost(uint256 mutabilityCost_) external onlyOwner {
        mutabilityConfig.mutabilityCost = mutabilityCost_;

        emit MutabilityCostConfigured(mutabilityCost_);
    }


    /**
     * @notice set whether or not the token can be traded while changes are pending
     * @param setting is a boolean of the change
     */
    function setTokenTradeBeforeChange(bool setting) external onlyOwner {
        mutabilityConfig.tradeBeforeChange = setting;
    }


} 

