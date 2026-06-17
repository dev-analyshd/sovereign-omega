// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * SOVEREIGN-Ω Trading Vault
 * Pharos Chain (Chain ID: 1672 / 688688)
 * Holds trading capital. Agent can only trade when coherent (Psi >= Delta).
 * All trades are recorded on-chain. All positions are verifiable.
 */
contract SovereignVault {

    address public owner;
    address public agentOperator;
    address public registryContract;

    uint256 public totalDeposited;
    uint256 public totalPnL;
    uint256 public totalTrades;
    uint256 public winningTrades;

    // Maximum single trade: 2% of vault — Rule 7
    uint256 public constant MAX_POSITION_BPS = 200;

    struct Trade {
        bytes32 tradeId;
        string  symbol;
        string  direction;
        uint256 entryPrice;
        uint256 size;
        uint256 psiAtEntry;
        uint256 timestamp;
        bool    closed;
        int256  pnl;
    }

    mapping(bytes32 => Trade) public trades;
    bytes32[] public tradeIds;

    event Deposit(address indexed depositor, uint256 amount);
    event Withdraw(address indexed recipient, uint256 amount);
    event TradeOpened(bytes32 indexed tradeId, string symbol, string direction, uint256 size, uint256 psiScaled);
    event TradeClosed(bytes32 indexed tradeId, int256 pnl, uint256 exitPrice);
    event SilenceBlockedTrade(uint256 psiScaled, uint256 deltaScaled);

    modifier onlyOperator() {
        require(msg.sender == agentOperator || msg.sender == owner, "Not authorized");
        _;
    }

    constructor(address _agentOperator, address _registryContract) {
        owner = msg.sender;
        agentOperator = _agentOperator;
        registryContract = _registryContract;
    }

    receive() external payable {
        totalDeposited += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function openTrade(
        bytes32 tradeId,
        string calldata symbol,
        string calldata direction,
        uint256 sizeScaled,
        uint256 entryPriceScaled,
        uint256 psiScaled,
        uint256 deltaScaled
    ) external onlyOperator {
        // On-chain coherence gate — Rule 3: no override
        require(psiScaled >= deltaScaled, "SILENCE: Psi < Delta. Trade blocked by coherence gate.");

        // Position size check — Rule 7
        uint256 maxSize = (address(this).balance * MAX_POSITION_BPS) / 10000;
        require(sizeScaled <= maxSize * 1e18, "Position exceeds 2% vault limit");

        trades[tradeId] = Trade({
            tradeId:    tradeId,
            symbol:     symbol,
            direction:  direction,
            entryPrice: entryPriceScaled,
            size:       sizeScaled,
            psiAtEntry: psiScaled,
            timestamp:  block.timestamp,
            closed:     false,
            pnl:        0
        });

        tradeIds.push(tradeId);
        totalTrades += 1;

        emit TradeOpened(tradeId, symbol, direction, sizeScaled, psiScaled);
    }

    function closeTrade(
        bytes32 tradeId,
        uint256 exitPriceScaled,
        int256 pnlScaled
    ) external onlyOperator {
        Trade storage t = trades[tradeId];
        require(!t.closed, "Already closed");

        t.closed = true;
        t.pnl = pnlScaled;

        if (pnlScaled > 0) {
            winningTrades += 1;
            totalPnL += uint256(pnlScaled);
        }

        emit TradeClosed(tradeId, pnlScaled, exitPriceScaled);
    }

    function recordSilencedTrade(
        uint256 psiScaled,
        uint256 deltaScaled
    ) external onlyOperator {
        emit SilenceBlockedTrade(psiScaled, deltaScaled);
    }

    function withdraw(uint256 amount) external {
        require(msg.sender == owner, "Only owner");
        require(address(this).balance >= amount, "Insufficient balance");
        payable(owner).transfer(amount);
        emit Withdraw(owner, amount);
    }

    function getVaultStats() external view returns (
        uint256 balance,
        uint256 deposited,
        uint256 totalTradesCount,
        uint256 wins,
        uint256 totalPnLValue
    ) {
        return (address(this).balance, totalDeposited, totalTrades, winningTrades, totalPnL);
    }
}
