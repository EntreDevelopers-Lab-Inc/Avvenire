// SPDX-License-Identifier: MIT
// Creators: TokyoDan

/// @title Avvenire NFT Collection
/// @author TokyoDan

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chiru-labs/contracts/ERC721A.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";

// Do I need to implement ERC721A if I already make Avvenire ERC721AOwnersExplicit?
contract Avvenire is ERC721A, Ownable, ERC721AOwnersExplicit {
    /**
     * Initialized instead assigning in constructor. Optimizes on gas
     * Max supply eventually needs to be set to 10000...
     */
    uint256 immutable maxSupply = 30;
    uint8 immutable whiteListMaxMint = 2;
    uint8 immutable maxMint = 10;
    uint256 pricePerToken = 0.1 ether;

    bool isWhiteListActive;
    bool isMintActive;

    // mapping for whitelist. (address => boolean)
    mapping(address => bool) private _whiteList;

    constructor(string memory name_, string memory symbol_)
        ERC721A(name_, symbol_)
        Ownable()
    {}

    //Enable or disable whiteList mint
    function setWhiteListStatus(bool state_) public onlyOwner {
        isWhiteListActive = state_;
    }

    //Enable or disable mint
    function setMintStatus(bool state_) public onlyOwner {
        isMintActive = state_;
    }

    // Needed??
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
        require(isMintActive, "Minting is not active");
        require(
            quantity <= (maxSupply - currentIndex),
            "Mint quantity will exceed max supply"
        );
        require(
            quantity <= maxMint - _numberMinted(msg.sender),
            "Mint quantity exceeds max number you can mint"
        );
        require(msg.value >= pricePerToken * quantity, "Not enough ETH sent");
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
        _safeMint(to, quantity, _data);
    }

    /**
     * whiteList numMinted needs to be seperated from AddressData.numberMinted
     */

    function setWhiteList(address[] calldata addresses) external onlyOwner {
        for (uint256 i = 0; i < addresses.length; i++) {
            _whiteList[addresses[i]] = true;
        }
    }

    /**
     * Function to mint during the White List phase
     * @param quantity number of tokens to mint
     */
    function whiteListMint(uint8 quantity) external payable {
        require(isWhiteListActive, "White list minting is not active");
        require(
            quantity <= maxSupply - currentIndex,
            "Mint quantity will exceed max supply"
        );
        // Takes care of 2 cases:
        // A. When quantity exceeds whiteListMaxMint
        // B. When whiteListMinter tries to mint a second time
        require(
            quantity <= whiteListMaxMint - _numberMinted(msg.sender),
            "Mint quantity exceeds max number you can mint during whitelist"
        );
        require(msg.value >= pricePerToken * quantity, "Not enough ETH sent");

        _safeMint(msg.sender, quantity);
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
        _setOwnersExplicit(currentIndex);
    }
}
