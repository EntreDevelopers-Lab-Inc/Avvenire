// SPDX-License-Identifier: MIT

/**
 *@title Azuki ERC721 Contract
 */
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chiru-labs/contracts/ERC721A.sol";
// _setOwnersExplicit( ) moved from the ERC721A contract to an extension
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
    uint256 public immutable maxPerAddressDuringAuction; // constant for later assignment>?t
    uint256 public immutable maxPerAddressDuringWhiteList;

    uint256 public immutable amountForTeam; // Amount of NFTs for team
    uint256 public immutable amountForAuctionAndTeam; // Amount of NFTs for the team and auction
    uint256 public immutable collectionSize; // Total collection size
    //uint256 public immutable maxBatchPublic;
    // uint256 public immutable maxBatchWhiteList;

    address immutable devAddress;
    uint256 immutable paymentToDevs;

    struct SaleConfig {
        uint32 auctionSaleStartTime; //
        uint32 publicSaleStartTime; //
        uint64 mintlistPrice; //
        uint64 publicPrice; // where is this set?
        uint32 publicSaleKey; //
    }

    SaleConfig public saleConfig; // use the struct as a constant (why make it public?)
    // struct is made public so frontend can query

    // Whitelist mapping (address => amount they can mint)
    mapping(address => uint256) public allowlist;

    //Do I need to keep public?
    // Private or internal?
    mapping(address => uint256) private totalPaid;

    /**
     * @notice Constructor calls on ERC721A constructor and sets the previously defined global variables
     * @param maxPerAddressDuringAuction_ the number for the max batch size and max # of NFTs per address during the auction
     * @param maxPerAddressDuringWhiteList_ the number for the max batch size and max # of NFTs per address during the whiteList
     * @param collectionSize_ the number of NFTs in the collection
     * @param amountForTeam_ the number of NFTs for the team
     * @param amountForAuctionAndTeam_ specifies total amount to auction + the total amount for the team
     * @param devAddress_ address of devs
     * @param paymentToDevs_ payment to devs
     */
    constructor(
        uint256 maxPerAddressDuringAuction_,
        uint256 maxPerAddressDuringWhiteList_,
        uint256 collectionSize_,
        uint256 amountForAuctionAndTeam_,
        uint256 amountForTeam_,
        address devAddress_,
        uint256 paymentToDevs_
    ) ERC721A("Avvenire", "AVVENIRE") {
        maxPerAddressDuringAuction = maxPerAddressDuringAuction_;
        maxPerAddressDuringWhiteList = maxPerAddressDuringWhiteList_;

        amountForAuctionAndTeam = amountForAuctionAndTeam_;
        amountForTeam = amountForTeam_;
        collectionSize = collectionSize_;

        // Likely do not need these max batch variables
        // maxBatchPublic = maxBatchPublic_;
        // maxBatchWhiteList = maxBatchWhiteList_;

        // Assign dev address and payment
        devAddress = devAddress_;
        paymentToDevs = paymentToDevs_;

        require(
            amountForAuctionAndTeam_ <= collectionSize_, // make sure that the collection can handle the size of the auction
            "larger collection size needed"
        );
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
        // the auction can start at a particular time --> this allows the contract to be deployed ahead of time and activated later

        require(
            _saleStartTime != 0 && block.timestamp >= _saleStartTime,
            "sale has not started yet"
        );
        require(
            totalSupply() + quantity <= amountForAuctionAndTeam,
            "not enough remaining reserved for auction to support desired mint amount"
        );
        require(
            numberMinted(msg.sender) + quantity <= maxPerAddressDuringAuction, // make sure they are not trying to mint too many --> note: this is going to need to be different in our case as the whitelisted users have different mint amounts
            "can not mint this many"
        );
        uint256 totalCost = getAuctionPrice() * quantity; // total amount of ETH needed for the transaction
        _safeMint(msg.sender, quantity); // mint this amount to the sender
        refundIfOver(totalCost); // make sure to refund the excess

        //Add to totalPaid
        totalPaid[msg.sender] = totalPaid[msg.sender] + totalCost;
    }

    /**
     * @notice function to mint for allow list
     * @param quantity amount to mint for whitelisted users
     */
    function whiteListMint(uint256 quantity) external payable callerIsUser {
        // Sets the price to the mintlistPrice, which was set by endAuctionAndSetupNonAuctionSaleInfo(...)
        uint256 price = uint256(saleConfig.mintlistPrice);

        require(price != 0, "Allowlist sale has not begun yet");

        require(allowlist[msg.sender] > 0, "not eligible for allowlist mint"); // this also checks the decrement
        // need a require statement to make sure that quantity is less than the limit for each user
        require(
            totalSupply() + quantity <= collectionSize,
            "Reached max supply"
        );
        require(
            numberMinted(msg.sender) + quantity <= maxPerAddressDuringWhiteList,
            "Can not mint this many"
        );

        allowlist[msg.sender] = allowlist[msg.sender] - quantity;

        _safeMint(msg.sender, quantity);

        // Give a 30% discount compared to the dutch auction
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
            // we can just set our struct to internal...
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

        // Is there a cap for the maxPerAddress during the mint?

        // require(
        //     numberMinted(msg.sender) + quantity <= maxPerAddressDuringMint,
        //     "can not mint this many"
        // );
        _safeMint(msg.sender, quantity);

        uint256 totalCost = publicPrice * quantity;
        refundIfOver(totalCost);
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
     * NOT IDEAL IMPLEMENTATION
     * Have to wait for all users to call refund() before being able to withdraw funds
     * PROBLEM: there is no way to iterate through a mapping
     * SUSCEPTIBLE TO HACKS
     */
    function refundMe() external {
        uint256 endingPrice = saleConfig.publicPrice;
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
    function refund(address toRefund) external onlyOwner {
        uint256 endingPrice = saleConfig.publicPrice;
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
            publicPriceWei != 0 && // must sell for more than 0
            publicSaleKey != 0 && // must have a key that is non-zero
            block.timestamp >= publicSaleStartTime; // must be past the public start time
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
            return AUCTION_START_PRICE; // if the timestamp is less than the start of the sale, no discount
        }
        if (block.timestamp - _saleStartTime >= AUCTION_PRICE_CURVE_LENGTH) {
            return AUCTION_END_PRICE; // lower limit of the auction
        } else {
            uint256 steps = (block.timestamp - _saleStartTime) /
                AUCTION_DROP_INTERVAL;
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

    /**
     * @notice function to withdraw the money from the contract. Only callable by the owner
     */
    function withdrawMoney() external onlyOwner nonReentrant {
        // Pay devs
        (bool sent, ) = devAddress.call{value: paymentToDevs}("");
        require(sent, "dev transfer failed");
        // Withdraw rest of the contract
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "team transfer failed."); // why check the requirement after?
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
     * @notice Returns a struct, which contains a token owner's address and the time they acquired the token
     * @param tokenId the tokenID
     */
    function getOwnershipData(
        uint256 tokenId // storing all the old ownership
    ) external view returns (TokenOwnership memory) {
        return ownershipOf(tokenId); // get historic ownership
    }
}

/*
NOTES
*/
