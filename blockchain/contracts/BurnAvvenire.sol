// SPDX-License-Identifier: MIT

/**
 * @title Testing the burn function of AvvenireCitizens 
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "../interfaces/AvvenireCitizenDataInterface.sol";

contract testAvvenireBurn {

    AvvenireCitizensInterface public citizensContract;

    constructor (address contractAddress) {
        citizensContract = AvvenireCitizensInterface(contractAddress);
    }

    function burnToken(uint256 tokenId) public {
        citizensContract.burn(tokenId);
    }
}