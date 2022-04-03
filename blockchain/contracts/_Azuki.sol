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

// ERC721AOwnersExplicit already inherits from ERC721A
// Since it is an abstract contract do I need to make Azuki inherit both?
contract Azuki is Ownable, ERC721A, ERC721AOwnersExplicit, ReentrancyGuard {
    uint256 public immutable maxPerAddressDuringMint; // constant for later assignment>?t
    uint256 public immutable amountForDevs; // Specifiy amount minted for Devs
    uint256 public immutable amountForAuctionAndDev; // this name should change to just amountForAuction

    // collectionSize and maxBatchSize removed from ERC721A -- Need to add here
    uint256 public immutable collectionSize;
    uint256 public immutable maxBatchSize;

    struct SaleConfig {
        uint32 auctionSaleStartTime;
        uint32 publicSaleStartTime;
        uint64 mintlistPrice;
        uint64 publicPrice;
        uint32 publicSaleKey;
    }

    SaleConfig public saleConfig; // use the struct as a constant (why make it public?)
    // struct is made public so frontend can query the the current price

    // Whitelist mapping (address => amount they can mint)
    mapping(address => uint256) public allowlist;

    /**
     * @notice Constructor calls on ERC721A constructor and sets the previously defined global variables
     * @param maxBatchSize_ designated maxBatchSize
     * @param collectionSize_ used to make sure auction is <= collectionSize_
     * @param amountForDevs_ assigned to amountForDevs
     * @param amountForAuctionAndDev_ specifies total amount to auction
     */
    constructor(
        uint256 maxBatchSize_,
        uint256 collectionSize_,
        uint256 amountForAuctionAndDev_,
        uint256 amountForDevs_
    ) ERC721A("Avvenire", "AVVENIRE") {
        maxPerAddressDuringMint = maxBatchSize_;
        amountForAuctionAndDev = amountForAuctionAndDev_; // set the amount on constructing the contract
        amountForDevs = amountForDevs_;
        // Initialized manually because ERC721A contract was updated
        collectionSize = collectionSize_;
        maxBatchSize = maxBatchSize_;

        require(
            amountForAuctionAndDev_ <= collectionSize_, // make sure that the collection can handle the size of the auction
            "larger collection size needed"
        );
    }

    /**
      @notice Modifier to make sure that the caller is a user and not another contract 
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
        // set the number to mint to the user within this auction
        uint256 _saleStartTime = uint256(saleConfig.auctionSaleStartTime); // get the start time out of the configuration/struct
        require(
            _saleStartTime != 0 && block.timestamp >= _saleStartTime, // the auction can start at a particular time --> this allows the contract to be deployed ahead of time and activated later
            "sale has not started yet"
        );
        require(
            totalSupply() + quantity <= amountForAuctionAndDev, // supply left and quantity minted is less than the limit
            "not enough remaining reserved for auction to support desired mint amount"
        );
        require(
            numberMinted(msg.sender) + quantity <= maxPerAddressDuringMint, // make sure they are not trying to mint too many --> note: this is going to need to be different in our case as the whitelisted users have different mint amounts
            // the way the whiteList is set below, you can set different mint amounts to a given address - Daniel
            "can not mint this many"
        );
        uint256 totalCost = getAuctionPrice(_saleStartTime) * quantity; // total amount of ETH needed for the transaction
        _safeMint(msg.sender, quantity); // mint this amount to the sender
        refundIfOver(totalCost); // make sure to refund the excess
    }

    /**
     * @notice function to mint for allow list
     */
    // We should change the implementation so user can mint more than 1
    // seperate function to mint if the user is on the whitelist
    function allowlistMint() external payable callerIsUser {
        // this should take a quantity argument to allow whitelists to get more
        uint256 price = uint256(saleConfig.mintlistPrice);
        require(price != 0, "allowlist sale has not begun yet");
        require(allowlist[msg.sender] > 0, "not eligible for allowlist mint"); // this also checks the decrement
        // need a require statement to make sure that quantity is less than the limit for each user
        require(totalSupply() + 1 <= collectionSize, "reached max supply"); // need to change this 1 to the quantity
        allowlist[msg.sender]--; // need to decrement by more than 1
        _safeMint(msg.sender, 1); // we should change this to allow for multiple
        refundIfOver(price); // make sure to refund the excess
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
            publicSaleKey == callerPublicSaleKey, // wouldn't this be publicly available because the struct is public?
            // likely; any variable is technically public on the blockchain.  private just means it can't be used by other contracts
            // publicSaleKey is likely the password used to be able to mint??? Unsure to be honest
            "called with incorrect public sale key"
        );

        require(
            isPublicSaleOn(publicPrice, publicSaleKey, publicSaleStartTime),
            "public sale has not begun yet"
        );
        require(
            totalSupply() + quantity <= collectionSize,
            "reached max supply"
        );
        require(
            numberMinted(msg.sender) + quantity <= maxPerAddressDuringMint,
            "can not mint this many"
        );
        _safeMint(msg.sender, quantity);
        refundIfOver(publicPrice * quantity); //
    }

    /**
     * @notice private function that refunds a user if msg.value > currentPrice
     * @param price current price
     */
    function refundIfOver(uint256 price) private {
        require(msg.value >= price, "Need to send more ETH."); // not refunding anything if they didn't pay more than the floor --> what happens when the floor is reached? does the last person get anything
        // Function does not have to do with the floor -- Used if a user sends more ETH than the current price
        // Let's say the current price is .5 ETH and a user sends 1 ETH; this function refunds them the excess that they sent
        if (msg.value > price) {
            payable(msg.sender).transfer(msg.value - price); // pay the user the excess
        }
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
            publicPriceWei != 0 && // must sell for more than 0
            publicSaleKey != 0 && // must have a key that is non-zero
            block.timestamp >= publicSaleStartTime; // must be past the public start time
    }

    uint256 public constant AUCTION_START_PRICE = 1 ether; // start price
    uint256 public constant AUCTION_END_PRICE = 0.15 ether; // floor price
    uint256 public constant AUCTION_PRICE_CURVE_LENGTH = 340 minutes; // total time of the auction
    uint256 public constant AUCTION_DROP_INTERVAL = 20 minutes; // after 20 minutes, drop one time block
    uint256 public constant AUCTION_DROP_PER_STEP =
        (AUCTION_START_PRICE - AUCTION_END_PRICE) /
            (AUCTION_PRICE_CURVE_LENGTH / AUCTION_DROP_INTERVAL); // how much the auction will drop the price per unit of time

    /**
     * @notice Returns the current auction price. Uses block.timestamp to properly calculate price
     * @param _saleStartTime the starting time of the auction
     */
    function getAuctionPrice(
        uint256 _saleStartTime // get the price of the dutch auction
    ) public view returns (uint256) {
        if (block.timestamp < _saleStartTime) {
            return AUCTION_START_PRICE; // if the timestamp is less than the start of the sale, no discount
        }
        if (block.timestamp - _saleStartTime >= AUCTION_PRICE_CURVE_LENGTH) {
            return AUCTION_END_PRICE; // lower limit of the auction
        } else {
            uint256 steps = (block.timestamp - _saleStartTime) / // this is continuous, not a step function
                AUCTION_DROP_INTERVAL; // time dependent discount
            return AUCTION_START_PRICE - (steps * AUCTION_DROP_PER_STEP); // calculate the start price based on how far away from the start we are
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
     * @param numSlots the respective number of NFTs that they can mint
     */
    function seedAllowlist(
        address[] memory addresses,
        uint256[] memory numSlots
    ) external onlyOwner {
        require(
            addresses.length == numSlots.length,
            "addresses does not match numSlots length"
        );
        for (uint256 i = 0; i < addresses.length; i++) {
            allowlist[addresses[i]] = numSlots[i]; // why not just set all of them to the same number?
            // Likely wanted to give some people (maybe even themselves) the ability to mint more @ whitelist - Daniel
        }
    }

    // we should have a function to clear the allow list
    // Seems like a waste.  Extra gas -- Daniel

    // another function to remove someone from the allow list (can just set their balance to 0), as we may want to remove people from the whitelist
    // Unsure how to properly remove from mappings.  You're prob right - Daniel

    // We should get rid of this, as i don't think oscar is giving us NFTs
    // For any part of the team.  Not just for us.  We mint then transfer them to Oscar and his cofounder

    /**
     * @notice function to mint for the team; Goes to the wallet of whoever deployed the contract
     * @param quantity the quantity to mint
     */
    function devMint(uint256 quantity) external onlyOwner {
        require(
            totalSupply() + quantity <= amountForDevs,
            "too many already minted before dev mint"
        );
        require(
            quantity % maxBatchSize == 0,
            "can only mint a multiple of the maxBatchSize"
        );
        uint256 numChunks = quantity / maxBatchSize;
        for (uint256 i = 0; i < numChunks; i++) {
            _safeMint(msg.sender, maxBatchSize);
        }
    }

    // REVEAL PLACEHOLDER URI
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

    /**
     * @notice function to withdraw the money from the contract. Only callable by the owner
     */
    function withdrawMoney() external onlyOwner nonReentrant {
        // take the money out and put it in the owners wallet

        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Transfer failed."); // why check the requirement after?
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
        // check how many have been minted to this owner --> where is this data stored, in the standard?
        // _addressData mapping in the ERC721A standard; line 51 - Daniel
        return _numberMinted(owner);
    }

    /**
     * @notice takes in a tokenID and returns a TokenOwnership struct, which contains the owner's address
     * and the time they acquired the token
     * @param tokenId intuitive...
     */
    function getOwnershipData(
        uint256 tokenId // storing all the old ownership
    ) external view returns (TokenOwnership memory) {
        return _ownershipOf(tokenId); // get historic ownership
    }
}
