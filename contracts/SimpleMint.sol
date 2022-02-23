pragma solidity ^0.8.0;

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
    uint256 price = 0.01;  // set a price to 0.01 ETH to allow easy testing
    string _baseTokenURI;

    // make a constructor (doesn't need to do much)
    constructor(baseURI) ERC721A("SimpleMint", "SM") {
        // set the folder base uri
        _baseTokenURI = baseURI;

    }

    // make a functiont to mint nfts to an address
    function mintNFTs(uint256 quantity) external payable callerIsUser {
        // mint the nfts
        _safeMint(msg.sender, quantity);
    }

    /**
     * @notice returns the baseURI; used in TokenURI
     */
    function _baseURI() internal view virtual override returns (string memory) {
        return _baseTokenURI;
    }
}
