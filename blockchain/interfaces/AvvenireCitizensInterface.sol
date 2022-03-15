// SPDX-License-Identifier: MIT

/**
 * @title Avvenire Citizens Interface
*/
pragma solidity ^0.8.4;

import "../interfaces/AvvenireCitizenDataInterface.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";


interface AvvenireCitizensInterface is AvvenireCitizenDataInterface, IERC721 {
    // other functions
    function getTotalSupply() external returns (uint256);
    function getChangeCost() external returns (uint256);
    function requestChange(uint256) external payable;
    function setCitizenData(Citizen memory, bool) external;
    function setTraitData(Trait memory, bool) external;
    function getMutabilityMode() external view returns (bool);
    function getCitizenMintActive() external view returns (bool);
    function bind(uint256, uint256, Sex, TraitType) external;
    function safeMint(address, uint256) external;
    function numberMinted(address) external returns (uint256);
}

interface AvvenireCitizensWithMappingInterface is AvvenireCitizensInterface {
    // public mappings that should return information
    function tokenIdToCitizen(uint256) view external returns (Citizen memory);
    function tokenIdToTrait(uint256) view external returns (Trait memory);
}
