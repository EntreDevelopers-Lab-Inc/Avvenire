// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import './TokenMutator.sol';
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
// _setOwnersExplicit( ) moved from the ERC721A contract to an extension
import "@openzeppelin/contracts/utils/Strings.sol";

// ERC721AOwnersExplicit already inherits from ERC721A
contract SimpleMint is
    TokenMutator
{
    uint256 price = 0.01 ether;  // set a price to 0.01 ETH to allow easy testing
    uint256 collectionSize;

    // make a constructor (doesn't need to do much)
    constructor(string memory baseURI_, string memory loadURI_, uint256 collectionSize_, address devAddress_) TokenMutator("SimpleMint", "SM", baseURI_, loadURI_, devAddress_) {
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

    // function to withdraw the money
    function withdrawMoney() external onlyOwner nonReentrant {

        // Withdraw rest of the contract
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "team transfer failed.");
    }
}
