// SPDX-License-Identifier: MIT

/**
 * @title AvvenireCitizens Trait Management Contract
*/
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizensInterface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AvvenireCitizenMarket is
    Ownable
{
    // store the avvenireCitizens contract
    AvvenireCitizensInterface public avvenireCitizens;

    /**
     * @notice a function to check the mergability of different traits
    */
    function checkMergability() public view returns(bool)
    {
        // check if the avvenireCitizens contract is even mutable
        if (!avvenireCitizens.getMutabilityMode())
        {
            return false;
        }
        // if the citizen mint is active, traits cannot be merged, market must be suspended
        else if (avvenireCitizens.getCitizenMintActive())
        {
            return false;
        }

        // if it gets here, just return true (it passedall the checks)
        return true;
    }

    /**
     * @notice external function spawning traits --> best utilized when minting many at once (using multiple safe mints --> good practice to send one spawn traits for all new traits, and another for respawning all the old ones)
     * This allows you to spawn traits IF the whole token is decomposed OR we need to spawn many new traits (more efficient than spawning each of the tokens individually --> can just spawn the remainder of )
     * @param tokenIds are an array of token ids that correspond to the traits that must be spawned
     */
    function _spawnTraits(uint256[] calldata tokenIds) internal {
        // make sure that we are in mutability mode --> otherwise, traits should not be spawned, as no changes should occur
        require(avvenireCitizens.getMutabilityMode(), "Traits are currently immutable.");

        // ensure that all the token Ids are 0 --> iterate over the array
        bool allNewTokens = true;
        for (uint256 i = 0; i < tokenIds.length; i += 1) {
            if (tokenIds[i] != 0) {
                // set that all the tokens are NOT new, and break the loop
                allNewTokens = false;
                break;
            }
        }

        // if they are all new tokens, mint all of them with safeMint
        if (allNewTokens) {
            avvenireCitizens.safeMint(tx.origin, tokenIds.length);
        }
        // else, each token must be chosen to be minted or respawned
        else {
            for (uint256 i = 0; i < tokenIds.length; i += 1) {
                // if the tokenId is 0, safe mint it
                if (tokenIds[i] == 0) {
                    avvenireCitizens.safeMint(tx.origin, 1);
                }
                // else, respawn the trait (will fail if the trait does not exist or is already free)
                else {
                    avvenireCitizens.respawnTrait(tokenIds[i]);
                }
            }
        }
    }

    /**
     * @notice a function to combine the token's parts
     * this must be payable in order to request changes to each individual component
    */
    function combine() external payable
    {

    }

    /**
     * @notice a function to set the avvenireCitizens contract address (only from owner)
    */
    function setAvvenireContractAddress(address contractAddress) external onlyOwner
    {
        avvenireCitizens = AvvenireCitizensInterface(contractAddress);
    }

}


