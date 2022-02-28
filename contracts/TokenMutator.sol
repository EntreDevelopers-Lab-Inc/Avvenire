// SPDX-License-Identifier: MIT

/**
 * @title token mutating contract for ERC721A
 */
pragma solidity ^0.8.0;
import "@chiru-labs/contracts/ERC721A.sol";
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

// token mutator changes the way that an ERC721A contract interacts with tokens
contract TokenMutator is
    ERC721A,
    ERC721AOwnersExplicit
{
    // mutability information
    bool mutabilityMode = false;  // initially set the contract to be immutable, this will keep people from trying to use the function before it is released
    string loadURI;  // a URI that the NFT will be set to while waiting for changes
    uint256 public mutabilityCost;  // the amount that it costs to make a change

    // struct for storing change information
    struct ChangeRequest {
        bool changeRequested;

    }

    // mapping for tokenId to token URI (similar to the former ERC721 mapping of a tokenId to a URI directly)
    mapping(uint256 => string) public tokenIdToTokenURI;

    constructor(
        string ERC721Name_,
        string ERC721AId_,
        string loadURI_
        )
    ERC721A(ERC721Name_, ERC721AId_) {
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
     * @notice returns the baseURI; used in TokenURI
     */
    function _baseURI() internal view virtual override returns (string memory) {
        return _baseTokenURI;
    }

    /**
     * @notice sets the baseURI
     * @param baseURI the base URI
     */
    function setBaseURI(string calldata baseURI) external onlyOwner {
        _baseTokenURI = baseURI;
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

        // check if the user is the owner of the token

        // check if the token has already been requested to change

        // set te address to the loading address

        // set thte token as requested to change
    }

}
