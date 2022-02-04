// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./ERC721A.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

contract Azuki is Ownable, ERC721A, ReentrancyGuard {
  uint256 public immutable maxPerAddressDuringMint;  // constant for later assignment>?t
  uint256 public immutable amountForDevs;  // this likely needs to go... we don't want it floating around and using excess gas
  uint256 public immutable amountForAuctionAndDev;  // this name should change to just amountForAuction

  struct SaleConfig {  // a struct to store all the sale information
    uint32 auctionSaleStartTime;  //
    uint32 publicSaleStartTime;  //
    uint64 mintlistPrice;  //
    uint64 publicPrice;  // where is this set?
    uint32 publicSaleKey;  //
  }

  SaleConfig public saleConfig;  // use the struct as a constant (why make it public?)

  mapping(address => uint256) public allowlist;  // their version of a whitelist

  constructor(
    uint256 maxBatchSize_,
    uint256 collectionSize_,
    uint256 amountForAuctionAndDev_,
    uint256 amountForDevs_
  ) ERC721A("Azuki", "AZUKI", maxBatchSize_, collectionSize_) {
    maxPerAddressDuringMint = maxBatchSize_;
    amountForAuctionAndDev = amountForAuctionAndDev_;  // set the amount on constructing the contract
    amountForDevs = amountForDevs_;  // this should be deleted
    require(
      amountForAuctionAndDev_ <= collectionSize_,  // make sure that the collection can handle the size of the auction
      "larger collection size needed"
    );
  }

  modifier callerIsUser() {
    require(tx.origin == msg.sender, "The caller is another contract");  // check that a user is accessing a contract
    _;
  }

  function auctionMint(uint256 quantity) external payable callerIsUser {  // set the number to mint to the user within this auction
    uint256 _saleStartTime = uint256(saleConfig.auctionSaleStartTime);  // get the start time out of the configuration
    require(
      _saleStartTime != 0 && block.timestamp >= _saleStartTime,  // the auction can start at a particular time --> this allows the contract to be deployed ahead of time and activated later
      "sale has not started yet"
    );
    require(
      totalSupply() + quantity <= amountForAuctionAndDev,  // supply left and quantity minted is less than the limit
      "not enough remaining reserved for auction to support desired mint amount"
    );
    require(
      numberMinted(msg.sender) + quantity <= maxPerAddressDuringMint,  // make sure they are not trying to mint too many --> note: this is going to need to be different in our case as the whitelisted users have different mint amounts
      "can not mint this many"
    );
    uint256 totalCost = getAuctionPrice(_saleStartTime) * quantity;  // total amount of ETH needed for the transaction
    _safeMint(msg.sender, quantity);  // mint this amount to the sender
    refundIfOver(totalCost);  // make sure to refund the excess
  }


  // seperate function to mint if the user is on the whitelist
  function allowlistMint() external payable callerIsUser {  // this should take a quantity argument to allow whitelists to get more
    uint256 price = uint256(saleConfig.mintlistPrice);
    require(price != 0, "allowlist sale has not begun yet");
    require(allowlist[msg.sender] > 0, "not eligible for allowlist mint");  // this also checks the decrement
    // need a require statement to make sure that quantity is less than the limit for each user
    require(totalSupply() + 1 <= collectionSize, "reached max supply");  // need to change this 1 to the quantity
    allowlist[msg.sender]--;  // need to decrement by more than 1
    _safeMint(msg.sender, 1);  // we should change this to allow for multiple
    refundIfOver(price);  // make sure to refund the excess
  }

  function publicSaleMint(uint256 quantity, uint256 callerPublicSaleKey)
    external
    payable
    callerIsUser
  {
    SaleConfig memory config = saleConfig;  // create a coonfiguration to keep track of internal sale data
    uint256 publicSaleKey = uint256(config.publicSaleKey);  // log the key
    uint256 publicPrice = uint256(config.publicPrice);  // get the price configuration
    uint256 publicSaleStartTime = uint256(config.publicSaleStartTime);
    require(
      publicSaleKey == callerPublicSaleKey,  // wouldn't this be publicly available because the struct is public?
      "called with incorrect public sale key"
    );

    require(
      isPublicSaleOn(publicPrice, publicSaleKey, publicSaleStartTime),
      "public sale has not begun yet"
    );
    require(totalSupply() + quantity <= collectionSize, "reached max supply");
    require(
      numberMinted(msg.sender) + quantity <= maxPerAddressDuringMint,
      "can not mint this many"
    );
    _safeMint(msg.sender, quantity);
    refundIfOver(publicPrice * quantity);  //
  }

  function refundIfOver(uint256 price) private {
    require(msg.value >= price, "Need to send more ETH.");  // not refunding anything if they didn't pay more than the floor --> what happens when the floor is reached? does the last person get anything
    if (msg.value > price) {
      payable(msg.sender).transfer(msg.value - price);  // pay the user the excess
    }
  }

  function isPublicSaleOn(  // check if the public sale is on
    uint256 publicPriceWei,
    uint256 publicSaleKey,
    uint256 publicSaleStartTime
  ) public view returns (bool) {
    return
      publicPriceWei != 0 &&  // must sell for more than 0
      publicSaleKey != 0 &&  // must have a key that is non-zero
      block.timestamp >= publicSaleStartTime;  // must be past the public start time
  }

  uint256 public constant AUCTION_START_PRICE = 1 ether;  // start price
  uint256 public constant AUCTION_END_PRICE = 0.15 ether;  // floor price
  uint256 public constant AUCTION_PRICE_CURVE_LENGTH = 340 minutes;  // total time of the auction
  uint256 public constant AUCTION_DROP_INTERVAL = 20 minutes;  // after 20 minutes, drop one time block
  uint256 public constant AUCTION_DROP_PER_STEP =
    (AUCTION_START_PRICE - AUCTION_END_PRICE) /
      (AUCTION_PRICE_CURVE_LENGTH / AUCTION_DROP_INTERVAL);  // how much the auction will drop the price per unit of time

  function getAuctionPrice(uint256 _saleStartTime)  // get the price of the dutch auction
    public
    view
    returns (uint256)
  {
    if (block.timestamp < _saleStartTime) {
      return AUCTION_START_PRICE;  // if the timestamp is less than the start of the sale, no discount
    }
    if (block.timestamp - _saleStartTime >= AUCTION_PRICE_CURVE_LENGTH) {
      return AUCTION_END_PRICE;  // lower limit of the auction
    } else {
      uint256 steps = (block.timestamp - _saleStartTime) /  // this is continuous, not a step function
        AUCTION_DROP_INTERVAL;  // time dependent discount
      return AUCTION_START_PRICE - (steps * AUCTION_DROP_PER_STEP);  // calculate the start price based on how far away from the start we are
    }
  }

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

  function setAuctionSaleStartTime(uint32 timestamp) external onlyOwner {  // set the start time
    saleConfig.auctionSaleStartTime = timestamp;
  }

  function setPublicSaleKey(uint32 key) external onlyOwner {  // set the special key (not viewable to the public)
    saleConfig.publicSaleKey = key;
  }

  function seedAllowlist(address[] memory addresses, uint256[] memory numSlots)
    external
    onlyOwner
  {
    require(
      addresses.length == numSlots.length,
      "addresses does not match numSlots length"
    );
    for (uint256 i = 0; i < addresses.length; i++) {
      allowlist[addresses[i]] = numSlots[i];  // why not just set all of them to the same number?
    }
  }

  // we should have a function to clear the allow list

  // another function to remove someone from the allow list (can just set their balance to 0), as we may want to remove people from the whitelist

  // we should get rid of this, as i don't think oscar is giving us NFTs
    // if he did, we would have to sacrifice some comp
  // For marketing etc.
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

  // // metadata URI
  string private _baseTokenURI;

  function _baseURI() internal view virtual override returns (string memory) {
    return _baseTokenURI;
  }

  function setBaseURI(string calldata baseURI) external onlyOwner {
    _baseTokenURI = baseURI;
  }

  function withdrawMoney() external onlyOwner nonReentrant {  // take the money out and put it in the owners wallet
    // we will need to add 2 wallets for us to receive money also

    (bool success, ) = msg.sender.call{value: address(this).balance}("");
    require(success, "Transfer failed.");  // why check the requirement after?
  }

  function setOwnersExplicit(uint256 quantity) external onlyOwner nonReentrant {  // why have this?
    _setOwnersExplicit(quantity);
  }

  function numberMinted(address owner) public view returns (uint256) {  // check how many have been minted to this owner --> where is this data stored, in the standard?
    return _numberMinted(owner);
  }

  function getOwnershipData(uint256 tokenId)  // storing all the old ownership
    external
    view
    returns (TokenOwnership memory)
  {
    return ownershipOf(tokenId);  // get historic ownership
  }
}

/*
NOTES
*/
