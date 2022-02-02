// SPDX-License-Identifier: MIT
// Creators: TokyoDan

/// @title Avvenire NFT Collection
/// @author TokyoDan

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "erc721a/contracts/ERC721A.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "erc721a/contracts/extensions/ERC721AOwnersExplicit.sol";

contract Avvenire is ERC721A, Ownable, ERC721AOwnersExplicit {
    /**
     * Initialized instead assigning in constructor. Optimizes on gas
     * Max supply eventually needs to be set to 10000...
     */
    uint256 immutable maxSupply = 30;
    uint256 immutable maxBatch = 10;
    uint256 immutable pricePerToken = 0.1 ether;

    uint8 immutable whiteListMax = 2;
    bool isWhiteListActive;
    bool isMintActive;

    // mapping for whitelist. (address => # of NFTs can mint)
    mapping(address => uint8) private _whiteList;

    constructor(string memory name_, string memory symbol_)
        ERC721A(name_, symbol_)
        Ownable()
    {}

    function enableWhiteList() external onlyOwner {
        isWhiteListActive = true;
    }

    function enableMint() external onlyOwner {
        isMintActive = true;
    }

    function numberMinted(address owner) public view returns (uint256) {
        return _numberMinted(owner);
    }

    function baseURI() public view returns (string memory) {
        return _baseURI();
    }

    /**
     * Overriding _baseURI() found in the ERC721A contract
     * Base URI for computing {tokenURI}. If set, the resulting URI for
     */
    function _baseURI() internal view override returns (string memory) {
        return
            "https://ipfs.io/ipfs/QmUizisYNzj824jNxuiPTQ1ykBSEjmkp42wMZ7DVFvfZiK/";
    }

    function exists(uint256 tokenId) public view returns (bool) {
        return _exists(tokenId);
    }

    /**
     * Modifier to guarantee that mint quantity cannot exceed the max supply
     * @param quantity the number of tokens to be minted
     */
    modifier properMint(uint256 quantity) {
        require(
            quantity <= (maxSupply - currentIndex),
            "Mint quantity will exceed max supply"
        );
        require(quantity <= maxBatch, "Mint quantity exceeds max batch");
        require(msg.value >= pricePerToken * quantity);
        _;
    }

    /**
     * See ERC721A
     * @param to address that receives the mint
     * @param quantity quantity that should be minted
     */
    function safeMint(address to, uint256 quantity)
        public
        payable
        properMint(quantity)
    {
        require(isMintActive, "Minting is not active");
        //sendValue(owner,msg.value);
        _safeMint(to, quantity);
    }

    /**
     * See ERC721A
     * @param to address that receives the mint
     * @param quantity quantity that should be minted
     * @param _data additional data
     */
    function safeMint(
        address to,
        uint256 quantity,
        bytes memory _data
    ) public payable properMint(quantity) {
        require(isMintActive, "Minting is not active");
        _safeMint(to, quantity, _data);
    }

    /**
     * whiteList numMinted needs to be seperated from AddressData.numberMinted
     */
    function setWhiteList(address[] calldata addresses, uint8 numAllowedToMint)
        external
        onlyOwner
    {
        for (uint256 i = 0; i < addresses.length; i++) {
            _whiteList[addresses[i]] = numAllowedToMint;
        }
    }

    function whiteListMint(uint8 quantity)
        external
        payable
        properMint(quantity)
    {
        uint256 ts = totalSupply();

        require(isWhiteListActive, "White list is not active");
        require(
            quantity <= _whiteList[msg.sender],
            "Exceeded whitelist max available to purchase"
        );

        _whiteList[msg.sender] -= quantity;
        for (uint256 i = 0; i < quantity; i++) {
            _safeMint(msg.sender, ts + i);
        }
    }

    /**
     * See ERC721AOwnersExplicit.sol and ERC721A.sol
     * function _setOwnersExplicit() adds addresses to blank spots in _addressData mapping
     * this subsequently eliminates the loops in the ownerOf() function
     * @param quantity is the number of tokens that you want to set explicit
     */
    // function setOwnersExplicit(uint256 quantity) public onlyOwner {
    //     _setOwnersExplicit(quantity);
    // }

    /**
     * Function to set all ownership as explicit
     */
    function setAllExplicit() external onlyOwner {
        //currentIndex initialized @ 0
        _setOwnersExplicit(currentIndex + 1);
    }

    //Following functionality needs to be added: Whitelist,
}
