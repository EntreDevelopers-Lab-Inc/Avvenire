// SPDX-License-Identifier: MIT

/**
 * @title Avvenire Blackhole
 */
pragma solidity ^0.8.4;

contract AvvenireBlackhole {
    constructor() payable {
        selfdestruct(payable(address(this)));
    }
}