// SPDX-License-Identifier: MIT

/**
 * @title Testing the burn function of AvvenireCitizens 
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "../interfaces/AvvenireCitizenDataInterface.sol";

contract testAvvenireBurn {

    AvvenireCitizensInterface public citizensContract;
    AvvenireTraitsInterface public traitsContract; 

    constructor (address citizensAddress, address traitsAddress) {
        citizensContract = AvvenireCitizensInterface(citizensAddress);
        traitsContract = AvvenireTraitsInterface(traitsAddress);
    }

    function burnCitizen(uint256 tokenId) public {
        citizensContract.burn(tokenId);
    }

    function burnTrait(uint256 tokenId) public {
        traitsContract.burn(tokenId);
    }

}