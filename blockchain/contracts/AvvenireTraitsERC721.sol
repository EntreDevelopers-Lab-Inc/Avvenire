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
error ChangeAlreadyRequested();

contract AvvenireTraits is
    Ownable,
    ERC721A,
    ERC721AOwnersExplicit,
    AvvenireTraitsInterface
    {
        event ChangeRequested(uint256 tokenId, address contractAddress, address sender);
        event TraitTransferrable(uint256 tokenId);
        event TraitNonTransferrable(uint256 tokenId);

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
     * Starting tokenId must be 1 because bind in AvvenireCitizen's checks if the traitId is 0
     */
    function _startTokenId() internal view override returns (uint256) {
        return 1;
    }

    /**
     * @notice sets an address's allowed list permission (for future interaction)
     * @param address_ is the address to set the data for
     * @param setting is the boolean for the data
     */
    function setAllowedPermission(address address_, bool setting)
        external
        onlyOwner
    {
        allowedContracts[address_] = setting;
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
        if (avvenireCitizensData.getTraitChangeRequest(tokenId)) {
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
        avvenireCitizensData.setTraitChangeRequest(trait.tokenId, changeUpdate);
    }

    /**
     * @notice getter function for trait data
     * @param tokenId the trait's id
     */
    function getTrait(uint256 tokenId) external view returns (Trait memory) {
        return avvenireCitizensData.getTrait(tokenId);
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

    /**
     * @notice Requests a change for a token
     * @param tokenId allows the user to request a change using their token id
     */
    function requestChange(uint256 tokenId) external payable callerIsAllowed {
        // check if you can even request changes at the moment
        require(avvenireCitizensData.getMutabilityMode(), "Tokens immutable");

        // check if the token exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();

        // check that this is the rightful token owner
        require(ownerOf(tokenId) == tx.origin, "Not owner");

        // check if the token has already been requested to change
        if (avvenireCitizensData.getTraitChangeRequest(tokenId)) revert ChangeAlreadyRequested();

        _requestChange(tokenId); // call the internal function
    }

    function _requestChange(uint256 tokenId) internal {
        // set the token as requested to change (don't change the URI, it's a waste of gas --> will be done once in when the admin sets the token uri)

        // ** Decided to get rid of this revert statement ** 
        // if (msg.value < getChangeCost()) revert InsufficcientFunds();
        avvenireCitizensData.setTraitChangeRequest(tokenId, true);
        emit ChangeRequested(tokenId, msg.sender, tx.origin);
    }

    
    /**
     * @notice This overrides the token transfers to check some conditions
     * @param from indicates the previous address
     * @param to indicates the new address
     * @param startTokenId indicates the first token id
     * @param quantity shows how many tokens have been minted
     */
    function _beforeTokenTransfers(
        address from,
        address to,
        uint256 startTokenId,
        uint256 quantity
    ) internal override {
        // token id end counter
        uint256 endTokenId = startTokenId + quantity;

        // iterate over all the tokens
        for (
            uint256 tokenId = startTokenId;
            tokenId < endTokenId;
            tokenId += 1
        ) {
            // the tokens SHOULD NOT be awaiting a change (you don't want the user to get surprised)
            if (! (avvenireCitizensData.getTradeBeforeChange()) ) {
                require(!avvenireCitizensData.getTraitChangeRequest(tokenId), "Change requested");
            }

            // if this is a trait, it must be free to be transferred
            if (avvenireCitizensData.getTrait(tokenId).exists) {
                require(
                    avvenireCitizensData.getTrait(tokenId).free, "Trait non-transferrable");
            }

        } // end of loop
    }

        /**
     * @notice This overrides the after token transfers function to create structs and request changes if they are traits
     * @param from indicates the previous address
     * @param to indicates the new address
     * @param startTokenId indicates the first token id
     * @param quantity shows how many tokens have been minted
     */
    function _afterTokenTransfers(
        address from,
        address to,
        uint256 startTokenId,
        uint256 quantity
    ) internal override {
        // token id end counter
        uint256 endTokenId = startTokenId + quantity;

        // iterate over all the tokens
        for (
            uint256 tokenId = startTokenId;
            tokenId < endTokenId;
            tokenId += 1
        ) {
            // check if the token exists in the citizen or trait mapping
            if (!avvenireCitizensData.getTrait(tokenId).exists) {
                    // create a new trait if the citizen mint is inactive, and there is no trait mapping to the token id
                    // no way to know the trait type on token transferm so just set it to null
                    // create a new trait and put it in the mapping --> just set the token id, that it exists and that it is free
                    Trait memory _trait = Trait({
                        tokenId: tokenId,
                        uri: "",
                        free: true,
                        exists: true,
                        sex: Sex.NULL,
                        traitType: TraitType.NULL,
                        originCitizenId: 0 // must set the origin citizen to null, as we have no data
                    });

                    avvenireCitizensData.setTrait(_trait);

                    // everytime a new trait is created, a change must be requested, as there is no data bound to it yet
                    _requestChange(tokenId);
            }

        } // end of for loop
    }

        /**
     * @notice internal function to make traits transferrable (used when binding traits)
     * checks that a trait exists (makes user unable to set a default to a default)
     * @param traitId for locating the trait
     * @param exists for if the trait exists
     */
    function makeTraitTransferable(uint256 traitId, bool exists) external callerIsAllowed {
        // only execute if the trait exists (want to account for default case)
        // if the trait doesn't exist yet, you want to mint all of them at once
        if ((exists) && (traitId != 0)) {
            // set the ownership to the transaction origin
            _ownerships[traitId].addr = tx.origin;

            // set the trait to free (should be tradable and combinable)
            avvenireCitizensData.setTraitFreedom(traitId, true);

            emit TraitTransferrable(traitId);
        }

    }

    /**
     * @notice internal function to make traits non-transferrable
     * checks that a trait exists (makes user unable to set a default to a default)
     * @param traitId to indicate which trait to change
     */
    function makeTraitNonTransferrable(uint256 traitId) external callerIsAllowed {
        require(avvenireCitizensData.getTrait(traitId).exists, "This trait does not exist");

        // set the ownership to null
        _ownerships[traitId].addr = address(this);

        // set the trait to not free (should not be tradable or combinable any longer)
        avvenireCitizensData.setTraitFreedom(traitId, false);

        emit TraitNonTransferrable(traitId);
    }


    }