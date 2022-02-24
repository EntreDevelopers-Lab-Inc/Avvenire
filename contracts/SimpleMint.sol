// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chiru-labs/contracts/ERC721A.sol";
// _setOwnersExplicit( ) moved from the ERC721A contract to an extension
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

// ERC721AOwnersExplicit already inherits from ERC721A
// Since it is an abstract contract do I need to make Azuki inherit both?
contract SimpleMint is
    Ownable,
    ERC721A,
    ERC721AOwnersExplicit,
    ReentrancyGuard
{
    uint256 price = 0.01 ether;  // set a price to 0.01 ETH to allow easy testing
    uint256 collectionSize;
    string _baseTokenURI;

    // make a constructor (doesn't need to do much)
    constructor(string memory baseURI_, uint256 collectionSize_) ERC721A("SimpleMint", "SM") {
        // set the folder base uri
        _baseTokenURI = baseURI_;

        // set the total supply
        collectionSize = collectionSize_;

    }

    // make a function to mint nfts to an address
    function mintNFTs(uint256 quantity) external payable callerIsUser {
        // require that we haven't exceeded the total supply
        require((totalSupply() + quantity) < collectionSize, "All NFTs have already been minted");

        // require that the user has provided enough eth to pay for it
        require(msg.value > (quantity * price), "You did not send the required funds for this transaction");

        // mint the nfts
        _safeMint(msg.sender, quantity);
    }

    /**
     * @notice returns the baseURI; used in TokenURI
     */
    function _baseURI() internal view virtual override returns (string memory) {
        return _baseTokenURI;
    }

    /**
      Modifier to make sure that the caller is a user and not another contract
     */
    modifier callerIsUser() {
        require(tx.origin == msg.sender, "The caller is another contract"); // check that a user is accessing a contract
        _;
    }
}
