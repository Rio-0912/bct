// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract SimpleToken {
    string public name = "LabToken";
    mapping(address => uint256) public balanceOf;
    event Transfer(address indexed from, address indexed to, uint256 value);
    constructor(uint256 supply) { balanceOf[msg.sender] = supply; }
    function transfer(address to, uint256 v) external returns (bool) {
        require(balanceOf[msg.sender] >= v, "Insufficient token balance");
        balanceOf[msg.sender] -= v; balanceOf[to] += v;
        emit Transfer(msg.sender, to, v);
        return true;
    }
}
