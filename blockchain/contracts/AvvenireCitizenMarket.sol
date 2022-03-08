// SPDX-License-Identifier: MIT

/**
 * @title Avvenire Citizen Trait Management Contract
*/
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract AvvenireCitizenTraitManagement is
    Ownable
{
    // store the avvenire contract
    Avvenire public avvenire;

    /**
     * @notice a function to check the mergability of different traits
    */
    function checkMergability() public view returns(bool)
    {
        // check if the avvenire contract is even mutable
        if (!avvenire.getMutabilityMode())
        {
            return false;
        }
        // if the character mint is active, traits cannot be merged, market must be suspended
        else if (avvenire.getCharacterMintActive())
        {
            return false;
        }

        // if it gets here, just return true (it passedall the checks)
        return true;
    }

    /**
     * @notice a function to combine the token's parts
     * this must be payable in order to request changes to each individual component
    */
    function combine() external payable
    {

    }

    /**
     * @notice a function to set the avvenire contract address (only from owner)
    */
    function setAvvenireContractAddress(address contractAddress) external onlyOwner
    {
        avvenire = Avvenire(contractAddress);
    }

}


// connect the Avvenire Contract interface
interface Avvenire {
    function getMutabilityMode() external view returns (bool);
    function getCharacterMintActive() external view returns (bool);
}
