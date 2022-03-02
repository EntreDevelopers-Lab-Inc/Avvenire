// SPDX-License-Identifier: MIT

/**
 * @title token mutating contract for ERC721A
 */
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chiru-labs/contracts/ERC721A.sol";
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

error URIQueryForNonexistentToken();

// token mutator changes the way that an ERC721A contract interacts with tokens
contract TokenMutator is
    Ownable,
    ERC721A,
    ERC721AOwnersExplicit
{
    // mutability information
    bool mutabilityMode = false;  // initially set the contract to be immutable, this will keep people from trying to use the function before it is released
    string baseURI;   // a uri for minting (like a base URI), but this allows the contract owner to change it later
    string loadURI;  // a URI that the NFT will be set to while waiting for changes
    uint256 public mutabilityCost;  // the amount that it costs to make a change

    // struct for storing change information
    struct ChangeRequest {
        bool changeRequested;
    }

    // mapping for tokenId to token URI (similar to the former ERC721 mapping of a tokenId to a URI directly)
    mapping(uint256 => string) private tokenIdToTokenURI;

    // mapping of tokenId to change request for information
    mapping(uint256 => ChangeRequest) public tokenChanges;

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
    }

    /**
      Modifier to make sure that the caller is a user and not another contract
     */
    modifier callerIsUser() {
        require(tx.origin == msg.sender, "The caller is another contract"); // check that a user is accessing a contract
        _;
    }

    /**
     * @notice returns the tokenURI of a token id (overrides ERC721 function)
     * @param tokenId allows the user to request the tokenURI for a particular token id
     */
    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        // check to make sure that the tokenId exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();  // error from ERC721A

        // check if the token uri is in the mapping
        string memory uri = tokenIdToTokenURI[tokenId];

        if (bytes(uri).length == 0) // in this case, there is no uri attached to the tokenIdToTokenURI mapping, so the uri should be the mint uri + the token id
        {
            uri = string(abi.encodePacked(baseURI, Strings.toString(tokenId)));
        }

        // else, a change could be requested, in which case you should show the loading URI
        ChangeRequest memory changeData = tokenChanges[tokenId];

        // if a change has been requested, only show the loading URI
        if (changeData.changeRequested)
        {
            return loadURI;
        }

        // else, just return the uri
        return uri;
    }

    /**
     * @notice Requests a change for a token
     * Requires that a request changes is currently on
     * Requires that the user is the owner of the token requested to change
     * Requires that the token has not already requested a change
     * @param tokenId allows the user to request a change using their token id
     */
    function requestChange(uint256 tokenId) external payable callerIsUser
    {
        // check if you can even request changes at the moment
        require(mutabilityMode, "Tokens are currently immutable.");

        // check if the token exists
        if (!_exists(tokenId)) revert URIQueryForNonexistentToken();

        // check if the user is the owner of the token
        require(msg.sender == ownerOf(tokenId), "Only the owner can request a change to the token");

        // get the token's change data
        ChangeRequest memory changeData = tokenChanges[tokenId];

        // check if the token has already been requested to change
        require(!changeData.changeRequested, "A change has already been requested for this token");

        // set the token as requested to change (don't change the URI, it's a waste of gas --> will be done once in when the admin sets the token uri)
        changeData.changeRequested = true;
        tokenChanges[tokenId] = changeData;
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
     * @param baseURI_ represents the new mint uri
    */
    function setBaseURI(string calldata baseURI_) external onlyOwner
    {
        // set thte global baseURI to this new baseURI_
        baseURI = baseURI_;
    }

}
