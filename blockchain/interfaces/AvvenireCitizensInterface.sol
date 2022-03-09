// SPDX-License-Identifier: MIT

/**
 * @title Avvenire Citizens Interface
*/
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";


interface AvvenireCitizensInterface is IERC721 {
    // traits are bound to sex for fitting
    enum Sex {NULL, MALE, FEMALE}

    // make an enumerable for trait types (meant to be overridden with traits from individual project)
    enum TraitType {
        NULL,
        BACKGROUND,
        BODY,
        TATTOOS,
        EYES,
        MOUTH,
        MASKS,
        NECKLACES,
        CLOTHING,
        EARRINGS,
        HAIR,
        EFFECTS
    }

    // struct for storing all the traits
    struct Traits {
        Trait background;
        Trait body;
        Trait tattoos;
        Trait eyes;
        Trait mouth;
        Trait masks;
        Trait necklaces;
        Trait clothing;
        Trait earrings;
        Trait hair;
        Trait effects;
    }

    // struct for storing trait data for the citizen (used ONLY in the citizen struct)
    struct Trait {
        uint256 tokenId; // for mapping citizens to their token traits
        string uri; // a uri mapping to the citizen's trait (must be set)
        bool free; // stores if the trait is free from the citizen (defaults to false)
        bool exists; // checks existence (for minting vs transferring)
        Sex sex;
        TraitType traitType;
    }

    // struct for storing citizens
    struct Citizen {
        uint256 tokenId;
        string uri;
        bool exists; //  checks existence (for minting vs transferring)
        Sex sex;
        Traits traits;
    }

    function getTotalSupply() external returns (uint256);
    function requestChange(uint256) external payable;
    function setCitizenData(Citizen memory, bool) external;
    function setTraitData(Trait memory, bool) external;
    function getMutabilityMode() external view returns (bool);
    function getCitizenMintActive() external view returns (bool);
    function safeMint(address, uint256) external;
    function numberMinted(address) external returns (uint256);
    function respawnTrait(uint256) external;
}
