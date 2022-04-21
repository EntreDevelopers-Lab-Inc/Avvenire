// SPDX-License-Identifier: MIT

/**
 * @title Avvenire Traits Contract
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chiru-labs/contracts/ERC721A.sol";
// _setOwnersExplicit( ) moved from the ERC721A contract to an extension
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

error NotSender();

contract AvvenireTraits is
    Ownable,
    ERC721A,
    ERC721AOwnersExplicit,
    AvvenireTraitsInterface
    {

        string baseURI; // a uri for minting, but this allows the contract owner to change it later
        string public loadURI; // a URI that the NFT will be set to while waiting for changes

        // Contract containing data
        AvvenireCitizensMappingsInterface public avvenireCitizensData;

        // mapping for allowing other contracts to interact with this one
        mapping(address => bool) private allowedContracts;

            bool isStopped;

    constructor(
        string memory ERC721Name_,
        string memory ERC721AId_,
        string memory baseURI_,
        string memory loadURI_,
        address dataContractAddress_
    ) ERC721A(ERC721Name_, ERC721AId_) Ownable() {
        // set the mint URI
        baseURI = baseURI_;

        // set the load uri
        loadURI = loadURI_;

        // set the receiving address to the publisher of this contract
        allowedContracts[msg.sender] = true;

        // Set data contract
        avvenireCitizensData = AvvenireCitizensMappingsInterface(dataContractAddress_);
    }

    /**
      Modifier to check if the contract is allowed to call this contract
    */
    modifier callerIsAllowed() {
        if (!allowedContracts[msg.sender]) revert NotSender();
        _;
    }

    modifier stoppedInEmergency {
        require(!isStopped, "Emergency stop active");
        _;
    }

     /**
     * @notice returns the tokenURI of a token id (overrides ERC721 function)
     * @param tokenId allows the user to request the tokenURI for a particular token id
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory)
    {
        // check to make sure that the tokenId exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken(); // error from ERC721A

        // if a change has been requested, only show the loading URI
        if (avvenireCitizensData.getTokenChangeRequest(tokenId)) {
            return loadURI;
        }

        if (bytes(avvenireCitizensData.getTrait(tokenId).uri).length > 0) {
            return avvenireCitizensData.getTrait(tokenId).uri;
        }

        // if there is no load uri, citizen uri, or trait uri, just return the base
        return string(abi.encodePacked(baseURI, Strings.toString(tokenId)));
    }

        /**
     * @notice set the trait data (id, uri, any traits)
     * @param trait allows a contract to set the trait's data to new information
     * @param changeUpdate sets the change data to the correct boolean (allows the option to set the changes to false after something has been updated OR keep it at true if the update isn't done)
     */
    function setTraitData(Trait memory trait, bool changeUpdate)
        external
        callerIsAllowed
        stoppedInEmergency
    {
        // set the trait data
        avvenireCitizensData.setTrait(trait);

        // set the token change data
        avvenireCitizensData.setTokenChangeRequest(trait.tokenId, changeUpdate);
    }


    /**
     * @notice external safemint function for allowed contracts
     * @param address_ for where to mint to
     * @param quantity_ for the amount
     */
    function safeMint(address address_, uint256 quantity_)
        external
        callerIsAllowed
        stoppedInEmergency
    {
        require(tx.origin != msg.sender, "The caller is a user.");
        _safeMint(address_, quantity_);
    }

    /**
     * @notice returns the number minted from specified address
     * @param owner an address of an owner in the NFT collection
     */
    function numberMinted(address owner) public view returns (uint256) {
        // check how many have been minted to this owner --> where is this data stored, in the standard?
        // _addressData mapping in the ERC721A standard; line 51 - Daniel
        return _numberMinted(owner);
    }

    /**
     * @notice Returns a struct, which contains a token owner's address and the time they acquired the token
     * @param tokenId the tokenID
     */
    function getOwnershipData(
        uint256 tokenId // storing all the old ownership
    ) external view returns (TokenOwnership memory) {
        return _ownershipOf(tokenId); // get historic ownership
    }

    /**
     * @notice setter  for emergency stop
     */
    function setEmergencyStop(bool _isStopped) external onlyOwner {
        isStopped = _isStopped; 
    }

    /**
     * @notice Sets the mint uri
     * @param baseURI_ represents the new base uri
     */
    function setBaseURI(string calldata baseURI_) external onlyOwner {
        // set thte global baseURI to this new baseURI_
        baseURI = baseURI_;
    }

    /**
     * @notice Sets the load uri
     * @param loadURI_ represents the new load uri
     */
    function setLoadURI(string calldata loadURI_) external onlyOwner {
        // set thte global loadURI to this new loadURI_
        loadURI = loadURI_;
    }

        /**
     * @notice a burn function to burn an nft.  The tx.origin must be the owner
     * @param tokenId the desired token to be burned
     */
    function burn(uint256 tokenId) external callerIsAllowed {
        require (tx.origin == ownerOf(tokenId), "Not owner");
        _burn(tokenId);
    }

    /**
     * @notice getter function for number of tokens that a user has burned
     * @param _owner the user's address
     */
    function numberBurned(address _owner) external view returns (uint256) {
        return _numberBurned(_owner); 
    }

    /**
     * @notice gets rid of the loops used in the ownerOf function in the ERC721A standard
     * @param quantity the number of tokens that you want to eliminate the loops for
     */
    function setOwnersExplicit(uint256 quantity)
        external
        callerIsAllowed
    {
        _setOwnersExplicit(quantity);
    }

    /**
     * @notice function that gets the total supply from the ERC721A contract
     */
    function getTotalSupply() external view returns (uint256) {
        return totalSupply();
    }


    }