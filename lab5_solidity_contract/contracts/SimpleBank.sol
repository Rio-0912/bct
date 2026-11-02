// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// Lab 5 - simple contract: owner-controlled vault with deposit/withdraw rules.
contract SimpleBank {
    address public owner;
    uint256 public minDeposit = 0.01 ether;     // business rule modified in Task 4
    mapping(address => uint256) public balances;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    constructor() { owner = msg.sender; }

    function deposit() external payable {
        require(msg.value >= minDeposit, "Deposit below minimum");
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool ok, ) = payable(msg.sender).call{value: amount}("");
        require(ok, "Transfer failed");
        emit Withdrawn(msg.sender, amount);
    }

    function setMinDeposit(uint256 v) external {
        require(msg.sender == owner, "Only owner");
        minDeposit = v;
    }

    function getBalance(address u) external view returns (uint256) { return balances[u]; }
}
