// SPDX-License-Identifier: MIT

/**
 * @title token mutating contract for ERC721A
 */
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chiru-labs/contracts/ERC721A.sol";
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";


error URIQueryForNonexistentToken();

// token mutator changes the way that an ERC721A contract interacts with tokens
contract TokenMutator is
    Ownable,
    ERC721A,
    ERC721AOwnersExplicit,
    ReentrancyGuard
{
    // mint information (whether or not the platform is minting characters)
    bool characterMintActive = true;  // this defaults to true, as the platform needs to mint characters before allowing tradable traits

    // mutability information
    bool mutabilityMode = false;  // initially set the contract to be immutable, this will keep people from trying to use the function before it is released
    string baseURI;   // a uri for minting (like a base URI), but this allows the contract owner to change it later
    string loadURI;  // a URI that the NFT will be set to while waiting for changes

    // payment information
    uint256 public mutabilityCost;  // the amount that it costs to make a change (initializes to 0)
    address payable receivingAddress;  // the address that collects the cost of the mutation

    // trading information
    bool tradeBeforeChange;  // initially set to false, don't want people to tokens that are pending changes

    // struct for storing change information
    // want to keep this in a struct, as it will allow other contracts to add data about the change to it
    struct ChangeRequest {
        bool changeRequested;
    }

    // struct for storing trait data for the character (used ONLY in the character struct)
    struct Trait {
        uint256 tokenId;  // for mapping characters to their token traits
        string uri;  // a uri mapping to the character's trait (must be set)
        bool empty;  // for checking if there is a trait associated
        bool free;  // stores if the trait is free from the character (defaults to false)
        bool exists;  // checks existence (for minting vs transferring)
    }

    // struct for storing characters
    struct Character {
        uint256 tokenId;
        string uri;
        Trait trait1;  // you can add as many traits as you want to this, it is just an example for how trait data should be stored within the character
        bool exists;  // checks existence (for minting vs transferring)
    }

    // mapping for tokenId to token URI (similar to the former ERC721 mapping of a tokenId to a URI directly)
    mapping(uint256 => string) private tokenIdToTokenURI;

    // mapping for tokenId to character
    mapping(uint256 => Character) public tokenIdToCharacter;

    // mapping for tokenId to trait
    mapping(uint256 => Trait) public tokenIdToTrait;

    // mapping of tokenId to change request for information --> being public allows anyone to see if the changes are requested
    mapping(uint256 => ChangeRequest) public tokenChanges;

    // mapping for allowing other contracts to interact with this one
    mapping(address => bool) public allowedContracts;

    constructor(
        string memory ERC721Name_,
        string memory ERC721AId_,
        string memory baseURI_,
        string memory loadURI_
        )
    ERC721A(ERC721Name_, ERC721AId_) {
        // set the mint URI
        baseURI = baseURI_;

        // set the load uri
        loadURI = loadURI_;

        // set the receiving address to the publisher of this contract
        receivingAddress = payable(msg.sender);

        // allow this contract to interact with itself
        allowedContracts[msg.sender] = true;
    }

    /**
      Modifier to make sure that the caller is a user and not another contract
     */
    modifier callerIsUser() {
        require(tx.origin == msg.sender, "The caller is another contract"); // check that a user is accessing a contract
        _;
    }

    /**
      Modifier to check if the contract is allowed to call this contract
    */
    modifier callerIsAllowed() {
        require(allowedContracts[msg.sender], "The caller is not allowed to interact with this contract");
        _;
    }

    /**
     * @notice returns the tokenURI of a token id (overrides ERC721 function)
     * @param tokenId allows the user to request the tokenURI for a particular token id
     */
    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        // check to make sure that the tokenId exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();  // error from ERC721A

        // if a change has been requested, only show the loading URI
        if (tokenChanges[tokenId].changeRequested)
        {
            return loadURI;
        }

        // if there is a character associated with this token, return the chacter's uri
        if (bytes(tokenIdToCharacter[tokenId].uri).length > 0)
        {
            return tokenIdToCharacter[tokenId].uri;
        }

        if (bytes(tokenIdToTrait[tokenId].uri).length > 0)
        {
            return tokenIdToTrait[tokenId].uri;
        }

        // if there is no load uri, character uri, or trait uri, just return the base
        return string(abi.encodePacked(baseURI, Strings.toString(tokenId)));
    }

    /**
     * @notice Requests a change for a token
     * @param tokenId allows the user to request a change using their token id
     */
    function requestChange(uint256 tokenId) external payable callerIsAllowed nonReentrant
    {
        // check if you can even request changes at the moment
        require(mutabilityMode, "Tokens are currently immutable.");

        // check if the token exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();

        // check if the token has already been requested to change
        require(!tokenChanges[tokenId].changeRequested, "A change has already been requested for this token");

        _requestChange(tokenId); // call the internal function
    }

    function _requestChange(uint256 tokenId) internal
    {
        // take some payment for this transaction if there is some cost set
        if (mutabilityCost > 0)
        {
            (bool success,) = receivingAddress.call{value: mutabilityCost}("");
            require(success, "Insufficient funds for token change");
        }

        // set the token as requested to change (don't change the URI, it's a waste of gas --> will be done once in when the admin sets the token uri)
        tokenChanges[tokenId].changeRequested = true;
    }

    /**
     * @notice Set the character data (id, uri, any traits). This will likely happen when combining nfts by the USER --> the URI should be set somewhere else, so the admin incurs minimal gas costs
     * @param character allows a contract to set the character's data to new information
     * @param changeUpdate sets the change data to the correct boolean (allows the option to set the changes to false after something has been updated OR keep it at true if the update isn't done)
     */
     function setCharacterData(Character memory character, bool changeUpdate) external callerIsAllowed
     {
        // set the character data
        tokenIdToCharacter[character.tokenId] = character;

        // set the token change data
        tokenChanges[character.tokenId].changeRequested = changeUpdate;
     }

     /**
     * @notice set the trait data (id, uri, any traits)
     * @param trait allows a contract to set the trait's data to new information
     * @param changeUpdate sets the change data to the correct boolean (allows the option to set the changes to false after something has been updated OR keep it at true if the update isn't done)
     */
     function setTraitData(Trait memory trait, bool changeUpdate) external callerIsAllowed
     {
        // set the trait data
        tokenIdToTrait[trait.tokenId] = trait;

        // set the token change data
        tokenChanges[trait.tokenId].changeRequested = changeUpdate;
     }

    /**
     * @notice Set the uri of a character
     * @param tokenId allows the contract to find the corresponding character
     * @param newURI is the new uri for the character's struct
    */
    function setCharacterURI(uint256 tokenId, string memory newURI) external callerIsAllowed
    {
        // check if the token id exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();

        // require that the character exists (only case where this would be trouble would be the first token would have index 0, but we can guarantee that at least one token exists)
        require(tokenIdToCharacter[tokenId].tokenId == tokenId, "There is no character that matches this tokenId");

        // set the character's uri
        tokenIdToCharacter[tokenId].uri = newURI;
    }

    /**
     * @notice Set the uri of a trait
     * @param tokenId allows the contract to find the corresponding trait
     * @param newURI is the new uri for the trait's struct
    */
    function setTraitURI(uint256 tokenId, string memory newURI) external callerIsAllowed
    {
        // check if the token id exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();

        // require that the trait exists
        require(tokenIdToTrait[tokenId].tokenId == tokenId, "There is no trait that matches this tokenId");

        // set the trait's uri
        tokenIdToTrait[tokenId].uri = newURI;
    }

    /**
     * @notice Sets the mutability of the contract (whether changes are accepted)
     * @param mutabilityMode_ allows the contract owner to change the mutability of the tokens
     */
    function setMutablityMode(bool mutabilityMode_) external onlyOwner
    {
        // set te new mutability mode to this boolean
        mutabilityMode = mutabilityMode_;
    }

    /**
     * @notice Sets the mint uri
     * @param baseURI_ represents the new base uri
    */
    function setBaseURI(string calldata baseURI_) external onlyOwner
    {
        // set thte global baseURI to this new baseURI_
        baseURI = baseURI_;
    }

    /**
     * @notice Sets the load uri
     * @param loadURI_ represents the new load uri
    */
    function setLoadURI(string calldata loadURI_) external onlyOwner
    {
        // set thte global loadURI to this new loadURI_
        loadURI = loadURI_;
    }

    /**
     * @notice Sets the mutability cost
     * @param mutabilityCost_ is the new mutability cost
     */
    function setMutabilityCost(uint256 mutabilityCost_) external onlyOwner
    {
        mutabilityCost = mutabilityCost_;
    }

    /**
     * @notice Sets the receivingAddress
     * @param receivingAddress_ is the new receiving address
     */
     function setReceivingAddress(address receivingAddress_) external onlyOwner
     {
        receivingAddress = payable(receivingAddress_);
     }

     /**
      * @notice set whether or not the token can be traded while changes are pending
      * @param setting is a boolean of the change
     */
    function setTokenTradeBeforeChange(bool setting) external onlyOwner
    {
        tradeBeforeChange = setting;
    }

    /**
     * @notice sets an address's allowed list permission (for future interaction)
     * @param address_ is the address to set the data for
     * @param setting is the boolean for the data
     */
    function setAllowedPermission(address address_, bool setting) external onlyOwner
    {
        allowedContracts[address_] = setting;
    }

    /**
     * @notice internal function to create a new character
     * @param tokenId (for binding the token id)
    */
    function createNewCharacter(uint256 tokenId) internal
    {
        // create a new character and put it in the mapping --> just set the token id and that it exists, don't set any of the traits or the URI
        tokenIdToCharacter[tokenId] = Character({
                    tokenId: tokenId,
                    uri: '',  // keep this blank to keep the user from paying excess gas before decomposition (the tokenURI function will handle for blank URIs)
                    exists: true,
                    trait1: Trait({
                        tokenId: 0,  // there will be no traits with tokenId 0, as that must be the first character (cannot have traits without minting the first character)
                        uri: '',
                        empty: false,
                        free: false,
                        exists: true
                        })
                    });
    }

    /**
     * @notice internal function to create a new trait --> this CAN be overridden if you want to include more data with each trait
     * @param tokenId (for binding the token id)
    */
    function createNewTrait(uint256 tokenId) internal
    {
        // create a new trait and put it in the mapping --> just set the token id, that it exists, that it is empty, and that it is free
        tokenIdToTrait[tokenId] = Trait({
                    tokenId: tokenId,
                    uri: '',
                    empty: false,
                    free: true,
                    exists: true
                    });

        // everytime a new trait is created, a change must be requested, as there is no data bound to it yet
        _requestChange(tokenId);
    }

    /**
     * @notice This overrides the token transfers to check some conditions
     * @param from indicates the previous address
     * @param to indicates the new address
     * @param startTokenId indicates the first token id
     * @param quantity shows how many tokens have been minted
    */
    function _beforeTokenTransfers(address from, address to, uint256 startTokenId, uint256 quantity) internal virtual override
    {
        // token id end counter
        uint256 endTokenId = startTokenId + quantity;

        // iterate over all the tokens
        for (uint256 tokenId = startTokenId; tokenId < endTokenId; tokenId += 1)
        {
            // the tokens SHOULD NOT be awaiting a change (you don't want the user to get surprised)
            if (!tradeBeforeChange)
            {
                require(!tokenChanges[tokenId].changeRequested, "A change has been requested for this/these token(s). They cannot be traded before this change is completed.");
            }

            // if this is a trait, it must be free to be transferred
            if (tokenIdToTrait[tokenId].exists)
            {
                require(tokenIdToTrait[tokenId].free);
            }
        }
    }

    /**
     * @notice This overrides the after token transfers function to create structs and request changes if they are traits
     * @param from indicates the previous address
     * @param to indicates the new address
     * @param startTokenId indicates the first token id
     * @param quantity shows how many tokens have been minted
    */
    function _afterTokenTransfers(address from, address to, uint256 startTokenId, uint256 quantity) internal virtual override
    {
        // token id end counter
        uint256 endTokenId = startTokenId + quantity;

        // THIS DOES NOT WORK
            // if it is a trait
        // iterate over all the tokens
        for (uint256 tokenId = startTokenId; tokenId < endTokenId; tokenId += 1)
        {
            // check if the token exists in the character mapping
            if ((!tokenIdToCharacter[tokenId].exists) && (!tokenIdToTrait[tokenId].exists))
            {
                // if the token id does not exist, create a new character or trait
                if (characterMintActive)
                {
                    // create a new character if the mint is active
                    createNewCharacter(tokenId);
                }
                else
                {
                    // create a new trait if the character mint is inactive, and there is no trait mapping to the token id
                    createNewTrait(tokenId);
                }
            }
        }

    }
}
