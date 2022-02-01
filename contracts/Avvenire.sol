// SPDX-License-Identifier: MIT
// Creators: TokyoDan

pragma solidity ^0.8.0;

import '../node_modules/@openzeppelin/contracts/access/Ownable.sol';
import '../node_modules/@openzeppelin/contracts/security/ReentrancyGuard.sol';
import './ERC721A.sol';
import '../node_modules/@openzeppelin/contracts/utils/Strings.sol';
import './extensions/ERC721AOwnersExplicit.sol';

contract AvvenireCollection is ERC721A, Ownable, ERC721AOwnersExplicit {
    /**
     * @dev Initialized over set in constructor. Optimizes on gas
     * Max supply eventually needs to be set to 10000...
     */
    uint256 immutable maxSupply = 30;
    uint256 immutable maxBatch = 10;
    uint256 immutable whiteList_MaxBatch = 2;
    uint256 immutable price = 0.1 ether;

    constructor(string memory name_, string memory symbol_) ERC721A(name_, symbol_) Ownable() {}

    function numberMinted(address owner) public view returns (uint256) {
        return _numberMinted(owner);
    }

    function baseURI() public view returns (string memory) {
        return _baseURI();
    }

    /**
     * @dev Overriding _baseURI() found in the ERC721A contract
     * Base URI for computing {tokenURI}. If set, the resulting URI for
     */
    function _baseURI() internal view override returns (string memory) {
        return 'https://ipfs.io/ipfs/QmXuxG21RtEbga9xk3c2ancUnQv2DppUnyEf6XzEBGd9ZP/3.jpg';
    }

    function exists(uint256 tokenId) public view returns (bool) {
        return _exists(tokenId);
    }

    /**
     * @dev Modifier to guarantee that mint quantity cannot exceed the max supply
     * currentIndex starts at 0;
     */
    modifier properMint(uint256 quantity) {
        require(quantity <= (maxSupply - currentIndex), 'Mint quantity will exceed max supply');
        require(quantity <= maxBatch, 'Mint quantity exceeds max batch');
        require(msg.value >= price);
        _;
    }

    /**
     * @dev see ERC721A. Added properMint modifier
     */
    function safeMint(address to, uint256 quantity) public payable properMint(quantity) {
        //sendValue(owner,msg.value);
        _safeMint(to, quantity);
    }

    /**
     * @dev see ERC721A. Added properMint modifier
     */
    function safeMint(
        address to,
        uint256 quantity,
        bytes memory _data
    ) public payable properMint(quantity) {
        _safeMint(to, quantity, _data);
    }

    /**
     * @dev see ERC721AOwnersExplicit.sol and ERC721A.sol
     * function _setOwnersExplicit() adds addresses to blank spots in _addressData mapping
     * this subsequently eliminates the loops in the ownerOf() function
     */
    function setOwnersExplicit(uint256 quantity) public onlyOwner {
        _setOwnersExplicit(quantity);
    }

    //Following functionality needs to be added: Whitelist,
}
