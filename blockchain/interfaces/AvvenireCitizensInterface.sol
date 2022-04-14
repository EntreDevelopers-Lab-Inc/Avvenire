// SPDX-License-Identifier: MIT

/**
 * @title Avvenire Citizens Interface
 */
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizenDataInterface.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

interface AvvenireCitizensInterface is AvvenireCitizenDataInterface, IERC721 {
    // mutability config stuct
    struct MutabilityConfig {
        bool mutabilityMode; // initially set the contract to be immutable, this will keep people from trying to use the function before it is released
        // payment information
        uint256 mutabilityCost; // the amount that it costs to make a change (initializes to 0)
        // trading information
        bool tradeBeforeChange; // initially set to false, don't want people to tokens that are pending changes
    }

    // other functions
    function getTotalSupply() external returns (uint256);

    function getChangeCost() external returns (uint256);

    function requestChange(uint256) external payable;

    function setCitizenData(Citizen memory, bool) external;

    function setTraitData(Trait memory, bool) external;

    function getMutabilityMode() external view returns (bool);

    function getCitizenMintActive() external view returns (bool);

    function bind(
        uint256,
        uint256,
        Sex,
        TraitType
    ) external;

    function safeMint(address, uint256) external;

    function numberMinted(address) external returns (uint256);

    function setOwnersExplicit(uint256) external;

    function burn(uint256) external;

    function numberBurned(address) external view returns (uint256);
}

// interface AvvenireCitizensWithMappingInterface is AvvenireCitizensInterface {
//     // public mappings that should return information
//     function tokenIdToCitizen(uint256) external view returns (Citizen memory);

//     function tokenIdToTrait(uint256) external view returns (Trait memory);

//     function mutabilityConfig() external view returns (MutabilityConfig memory);
// }

interface AvvenireCitizensMappingsInterface is AvvenireCitizenDataInterface {

    function getCitizen(uint256) external view returns (Citizen memory);

    function getTrait(uint256) external view returns (Trait memory);

    function setCitizen(Citizen memory) external; 

    function setTrait(Trait memory) external;

    function setAllowedPermission(address, bool) external;

    function setTraitFreedom(uint256, bool) external;

    function isCitizenInitialized(uint256) external view returns (bool);

    function setTokenChangeRequest(uint256, bool) external;

    function getTokenChangeRequest(uint256) external view returns(bool);
}

