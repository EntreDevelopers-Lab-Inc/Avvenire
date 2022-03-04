// SPDX-License-Identifier: MIT

/**
 *@title Azuki ERC721 Contract
 */
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chiru-labs/contracts/ERC721A.sol";
import "@chiru-labs/contracts/extensions/ERC721AOwnersExplicit.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

// ERC721AOwnersExplicit already inherits from ERC721A
// Since it is an abstract contract do I need to make Azuki inherit both?
contract AvvenireTestV2 is
    Ownable,
    ERC721A,
    ERC721AOwnersExplicit,
    ReentrancyGuard
{
    using Strings for uint256;

    // Immutable keyword removed for brownies test
    uint256 public maxPerAddressDuringAuction;
    uint256 public maxPerAddressDuringWhiteList;
    uint256 public amountForTeam;
    uint256 public amountForAuctionAndTeam;
    uint256 public collectionSize;
    uint256 public currentAmountForSale;

    address devAddress;
    uint256 paymentToDevs;

    address adjusterAddress;

    struct SaleConfig {
        uint32 auctionSaleStartTime;
        uint32 publicSaleStartTime;
        uint64 mintlistPrice;
        uint64 publicPrice;
        uint32 publicSaleKey;
    }

    SaleConfig public saleConfig;

    // Whitelist mapping (address => amount they can mint)
    mapping(address => uint256) public allowlist;

    //Do I need to keep public?
    mapping(address => uint256) public totalPaid;

    /**
     * @notice Constructor calls on ERC721A constructor and sets the previously defined global variables
     * @param maxPerAddressDuringAuction_ the number for the max batch size and max # of NFTs per address during the auction
     * @param maxPerAddressDuringWhiteList_ the number for the max batch size and max # of NFTs per address during the whiteList
     * @param currentAmountForSale_ the current amount for sale
     * @param collectionSize_ the number of NFTs in the collection
     * @param amountForTeam_ the number of NFTs for the team
     * @param amountForAuctionAndTeam_ specifies total amount to auction + the total amount for the team
     * @param devAddress_ address of devs
     */
    constructor(
        uint256 maxPerAddressDuringAuction_,
        uint256 maxPerAddressDuringWhiteList_,
        uint256 currentAmountForSale_,
        uint256 collectionSize_,
        uint256 amountForAuctionAndTeam_,
        uint256 amountForTeam_,
        address devAddress_
    ) ERC721A("Avvenire", "AVVENIRE") {
        maxPerAddressDuringAuction = maxPerAddressDuringAuction_;
        maxPerAddressDuringWhiteList = maxPerAddressDuringWhiteList_;

        amountForAuctionAndTeam = amountForAuctionAndTeam_;
        amountForTeam = amountForTeam_;
        currentAmountForSale = currentAmountForSale_;
        collectionSize = collectionSize_;

        // Likely do not need these max batch variables
        // maxBatchPublic = maxBatchPublic_;
        // maxBatchWhiteList = maxBatchWhiteList_;

        // Assign dev address and payment
        devAddress = devAddress_;

        require(
            amountForAuctionAndTeam_ <= collectionSize_, // make sure that the collection can handle the size of the auction
            "larger collection size needed"
        );
    }

    function _incrementPhase(uint256 amountToAuction, uint256 amountToSell)
        internal
    {
        _endAuctionAndPublicSale();

        // Makes sure that you can't auction more than you plan to sell
        require(
            amountToAuction <= amountToSell,
            "Cannot auction more than you plan to sell"
        );

        // Increase the amount to auction by the currentAmountForSale + the new amount to auction in the next phase
        amountForAuctionAndTeam = amountToAuction + currentAmountForSale;
        // Make sure this new amount is less than the collection size
        require(
            amountForAuctionAndTeam <= collectionSize,
            "You cannot auction this many"
        );

        // Increase the currentAmountForSale by the amountToSell
        currentAmountForSale = currentAmountForSale + amountToSell;

        // Makes sure that the currentAmountForSale can never be greater than the collectionSize
        require(
            currentAmountForSale <= collectionSize,
            "Cannot sell more than the collection size"
        );
    }

    function incrementPhase(uint256 amountToAuction_, uint256 amountToSell_)
        external
        onlyOwner
    {
        _incrementPhase(amountToAuction_, amountToSell_);
    }

    function sellRemainder(uint256 amountToAuction) external onlyOwner {
        _incrementPhase(amountToAuction, collectionSize);
    }

    function _endAuctionAndPublicSale() internal {
        saleConfig.auctionSaleStartTime = 0;
        saleConfig.publicSaleStartTime = 0;
        saleConfig.mintlistPrice = 0;
        saleConfig.publicPrice = 0;
        saleConfig.publicSaleKey = 0;
    }

    function endAuctionAndPublicSale() external onlyOwner {
        _endAuctionAndPublicSale();
    }

    /**
      Modifier to make sure that the caller is a user and not another contract 
     */
    modifier callerIsUser() {
        require(tx.origin == msg.sender, "The caller is another contract"); // check that a user is accessing a contract
        _;
    }

    /**
     * @notice function used to mint during the auction
     * @param quantity quantity to mint
     */
    function auctionMint(uint256 quantity) external payable callerIsUser {
        uint256 _saleStartTime = uint256(saleConfig.auctionSaleStartTime);

        require(
            _saleStartTime != 0 && block.timestamp >= _saleStartTime,
            "sale has not started yet"
        );
        require(
            totalSupply() + quantity <= amountForAuctionAndTeam,
            "not enough remaining reserved for auction to support desired mint amount"
        );
        require(
            numberMinted(msg.sender) + quantity <= maxPerAddressDuringAuction,
            "can not mint this many"
        );
        uint256 totalCost = getAuctionPrice() * quantity;
        _safeMint(msg.sender, quantity);
        refundIfOver(totalCost); // make sure to refund the excess

        totalPaid[msg.sender] = totalPaid[msg.sender] + totalCost;
    }

    /**
     * @notice function to mint for allow list
     * @param quantity amount to mint for whitelisted users
     */
    function whiteListMint(uint256 quantity) external payable callerIsUser {
        uint256 price = uint256(saleConfig.mintlistPrice);

        require(price != 0, "Allowlist sale has not begun yet");
        require(allowlist[msg.sender] > 0, "not eligible for allowlist mint");

        require(
            totalSupply() + quantity <= currentAmountForSale,
            "Reached max supply"
        );
        require(quantity <= allowlist[msg.sender], "Can not mint this many");

        allowlist[msg.sender] = allowlist[msg.sender] - quantity;

        _safeMint(msg.sender, quantity);

        uint256 totalCost = quantity * price;

        refundIfOver(totalCost);
    }

    /**
     * @notice mint function for the public sale
     * @param quantity quantity to mint
     * @param callerPublicSaleKey the key for the public sale
     */
    function publicSaleMint(uint256 quantity, uint256 callerPublicSaleKey)
        external
        payable
        callerIsUser
    {
        SaleConfig memory config = saleConfig; // create a coonfiguration to keep track of internal sale data
        uint256 publicSaleKey = uint256(config.publicSaleKey); // log the key
        uint256 publicPrice = uint256(config.publicPrice); // get the price configuration
        uint256 publicSaleStartTime = uint256(config.publicSaleStartTime);
        require(
            publicSaleKey == callerPublicSaleKey,
            // publicSaleKey is likely the password used to be able to mint???
            "called with incorrect public sale key"
        );

        require(
            isPublicSaleOn(publicPrice, publicSaleKey, publicSaleStartTime),
            "public sale has not begun yet"
        );
        require(
            totalSupply() + quantity <= currentAmountForSale,
            "reached max supply"
        );

        _safeMint(msg.sender, quantity);

        uint256 totalCost = publicPrice * quantity;
        refundIfOver(totalCost);
    }

    /**
     * @notice private function that refunds a user if msg.value > currentPrice
     * @param price current price
     */
    function refundIfOver(uint256 price) private {
        require(msg.value >= price, "Need to send more ETH.");
        if (msg.value > price) {
            payable(msg.sender).transfer(msg.value - price);
        }
    }

    /**
     * NOT IDEAL IMPLEMENTATION
     * Have to wait for all users to call refund() before being able to withdraw funds
     * PROBLEM: there is no way to iterate through a mapping
     * SUSCEPTIBLE TO HACKS
     */
    function refundMe() external callerIsUser nonReentrant {
        uint256 endingPrice = saleConfig.publicPrice;
        require(endingPrice > 0, "public price not set yet");

        uint256 actualCost = endingPrice * numberMinted(msg.sender);
        int256 reimbursement = int256(totalPaid[msg.sender]) -
            int256(actualCost);
        require(reimbursement > 0, "You are not eligible for a refund");

        (bool success, ) = msg.sender.call{value: uint256(reimbursement)}("");
        require(success, "Refund failed");

        totalPaid[msg.sender] = 0;
    }

    /**
     * @notice function to refund user on the price they paid
     * @param toRefund the address to refund
     */
    function refund(address toRefund) external onlyOwner nonReentrant {
        uint256 endingPrice = saleConfig.publicPrice;
        require(endingPrice > 0, "public price not set yet");

        uint256 actualCost = endingPrice * numberMinted(toRefund);
        int256 reimbursement = int256(totalPaid[toRefund]) - int256(actualCost);
        require(reimbursement > 0, "Not eligible for a refund");

        (bool success, ) = toRefund.call{value: uint256(reimbursement)}("");
        require(success, "Refund failed");

        totalPaid[toRefund] = 0;
    }

    /**
     * @notice function that returns a boolean indicating whtether the public sale is enabled
     * @param publicPriceWei must sell for more than 0
     * @param publicSaleKey must have a key that is non-zero
     * @param publicSaleStartTime  must be past the public start time
     */
    function isPublicSaleOn(
        // check if the public sale is on
        uint256 publicPriceWei,
        uint256 publicSaleKey,
        uint256 publicSaleStartTime
    ) public view returns (bool) {
        return
            publicPriceWei != 0 &&
            publicSaleKey != 0 &&
            block.timestamp >= publicSaleStartTime;
    }

    uint256 public constant AUCTION_START_PRICE = 1 ether; // start price
    uint256 public constant AUCTION_END_PRICE = 0.2 ether; // floor price
    uint256 public constant AUCTION_PRICE_CURVE_LENGTH = 60 minutes; // total time of the auction
    uint256 public constant AUCTION_DROP_INTERVAL = 7.5 minutes;
    // Should be 0.1 ether with the current setup...
    uint256 public constant AUCTION_DROP_PER_STEP =
        (AUCTION_START_PRICE - AUCTION_END_PRICE) /
            (AUCTION_PRICE_CURVE_LENGTH / AUCTION_DROP_INTERVAL); // how much the auction will drop the price per unit of time

    /**
     * @notice Returns the current auction price. Uses block.timestamp to properly calculate price
     */
    function getAuctionPrice() public view returns (uint256) {
        uint256 _saleStartTime = uint256(saleConfig.auctionSaleStartTime);
        require(_saleStartTime != 0, "auction has not started");
        if (block.timestamp < _saleStartTime) {
            return AUCTION_START_PRICE;
        }
        if (block.timestamp - _saleStartTime >= AUCTION_PRICE_CURVE_LENGTH) {
            return AUCTION_END_PRICE;
        } else {
            uint256 steps = (block.timestamp - _saleStartTime) /
                AUCTION_DROP_INTERVAL;
            return AUCTION_START_PRICE - (steps * AUCTION_DROP_PER_STEP);
        }
    }

    /**
     * @notice function to set up the saleConfig variable
     * @param mintlistPriceWei the mintlist price in WEI
     * @param publicPriceWei the public sale price
     * @param publicSaleStartTime the start time of the sale
     */
    function endAuctionAndSetupNonAuctionSaleInfo(
        uint64 mintlistPriceWei,
        uint64 publicPriceWei,
        uint32 publicSaleStartTime
    ) external onlyOwner {
        saleConfig = SaleConfig(
            0,
            publicSaleStartTime,
            mintlistPriceWei,
            publicPriceWei,
            saleConfig.publicSaleKey
        );
    }

    /**
     * @notice Sets the auction's starting time
     * @param timestamp the starting time
     */
    function setAuctionSaleStartTime(uint32 timestamp) external onlyOwner {
        // set the start time
        saleConfig.auctionSaleStartTime = timestamp;
    }

    /**
     * @notice sets the public sale key
     */
    function setPublicSaleKey(uint32 key) external onlyOwner {
        // set the special key (not viewable to the public)
        saleConfig.publicSaleKey = key;
    }

    /**
     * @notice sets the whitelist w/ the respective amount of number of NFTs that each address can mint
     * Requires that the addresses[] and numSlots[] are the same length
     * @param addresses the whitelist addresses
     */
    function seedWhitelist(address[] memory addresses) external onlyOwner {
        for (uint256 i = 0; i < addresses.length; i++) {
            allowlist[addresses[i]] = maxPerAddressDuringWhiteList;
        }
    }

    /**
     * @notice Removes a user from the whitelist
     * @param toRemove the public address of the user
     */
    function removeFromWhitelist(address toRemove) external onlyOwner {
        require(allowlist[toRemove] > 0, "User already minted");
        allowlist[toRemove] = 0;
    }

    /**
     * @notice function to mint for the team
     */
    function teamMint() external onlyOwner {
        require(totalSupply() == 0, "NFTs already minted");
        _safeMint(msg.sender, amountForTeam);
    }

    // function teamMint(uint256 quantity) external onlyOwner {
    //     require(
    //         totalSupply() + quantity <= amountForTeam,
    //         "too many already minted or quantity exceeds amountForTeam"
    //     );
    //     _safeMint(msg.sender, quantity);
    // }

    string private _baseTokenURI;

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

    // URIQueryForNonexistentToken is error defined in ERC721A
    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory)
    {
        require(_exists(tokenId), "URI query for nonexistent token");

        string memory baseURI = _baseURI();
        return
            bytes(baseURI).length != 0
                ? string(abi.encodePacked(baseURI, tokenId.toString()))
                : "";
    }

    /**
     * @notice function to withdraw the money from the contract. Only callable by the owner
     */
    function withdrawMoney() external onlyOwner nonReentrant {
        // Pay devs
        uint256 _payment = 2 ether + (address(this).balance / 20);

        (bool sent, ) = devAddress.call{value: _payment}("");
        require(sent, "dev transfer failed");

        // Withdraw rest of the contract
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "team transfer failed.");
    }

    /**
     * @notice gets rid of the loops used in the ownerOf function in the ERC721A standard
     * @param quantity the number of tokens that you want to eliminate the loops for
     */
    function setOwnersExplicit(uint256 quantity)
        external
        onlyOwner
        nonReentrant
    {
        _setOwnersExplicit(quantity);
    }

    /**
     * @notice returns the number minted from specified address
     * @param owner an address of an owner in the NFT collection
     */
    function numberMinted(address owner) public view returns (uint256) {
        return _numberMinted(owner);
    }

    /**
     * @notice Returns a struct, which contains a token owner's address and the time they acquired the token
     * @param tokenId the tokenID
     */
    function getOwnershipData(uint256 tokenId)
        external
        view
        returns (TokenOwnership memory)
    {
        return ownershipOf(tokenId);
    }
}

/*
NOTES
*/
