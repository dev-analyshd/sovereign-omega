// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * SOVEREIGN-Ω Registry
 * Deployed on Pharos Chain (Chain ID: 1672 mainnet / 688688 testnet)
 * Records agent identity, moat state, and intelligence milestones on-chain.
 * This contract is the agent's permanent on-chain proof of operation.
 */
contract SovereignRegistry {

    address public owner;
    address public agentOperator;

    struct AgentState {
        uint256 lambdaScaled;       // Λ * 1e18 for on-chain precision
        uint256 nCycles;            // Total coherent action cycles
        uint256 nSilences;          // Total SILENCE episodes
        uint256 iqScaled;           // IQ(t) * 1e18
        uint256 lastUpdated;        // Block timestamp
        string  topDomain;          // Highest mastery domain
        bytes32 faissIndexHash;     // Hash of current FAISS index state
    }

    AgentState public state;

    event MoatUpdated(uint256 indexed lambdaBefore, uint256 indexed lambdaAfter, uint256 nCycles);
    event SilenceEmitted(uint256 psiScaled, uint256 deltaScaled, string reason);
    event IntelligenceGrowth(uint256 iqBefore, uint256 iqAfter, string domain);
    event FAISSIndexUpdated(bytes32 indexed newHash, uint256 vectorCount);

    modifier onlyOperator() {
        require(msg.sender == agentOperator || msg.sender == owner, "Not authorized");
        _;
    }

    constructor(address _agentOperator) {
        owner = msg.sender;
        agentOperator = _agentOperator;
        state.lambdaScaled = 10000000000000000; // 0.01 * 1e18 = Lambda_0
        state.lastUpdated = block.timestamp;
    }

    function updateMoat(
        uint256 newLambdaScaled,
        uint256 newNCycles,
        uint256 newIQScaled
    ) external onlyOperator {
        uint256 oldLambda = state.lambdaScaled;
        uint256 oldIQ = state.iqScaled;

        require(newLambdaScaled >= state.lambdaScaled, "Moat cannot decrease");
        require(newNCycles >= state.nCycles, "Cycle count cannot decrease");

        emit MoatUpdated(oldLambda, newLambdaScaled, newNCycles);
        if (newIQScaled > oldIQ) {
            emit IntelligenceGrowth(oldIQ, newIQScaled, state.topDomain);
        }

        state.lambdaScaled = newLambdaScaled;
        state.nCycles = newNCycles;
        state.iqScaled = newIQScaled;
        state.lastUpdated = block.timestamp;
    }

    function recordSilence(
        uint256 psiScaled,
        uint256 deltaScaled,
        string calldata reason
    ) external onlyOperator {
        state.nSilences += 1;
        emit SilenceEmitted(psiScaled, deltaScaled, reason);
    }

    function updateFAISSHash(
        bytes32 newHash,
        uint256 vectorCount
    ) external onlyOperator {
        state.faissIndexHash = newHash;
        emit FAISSIndexUpdated(newHash, vectorCount);
    }

    function setTopDomain(string calldata domain) external onlyOperator {
        state.topDomain = domain;
    }

    function setAgentOperator(address newOperator) external {
        require(msg.sender == owner, "Only owner");
        agentOperator = newOperator;
    }

    function getState() external view returns (AgentState memory) {
        return state;
    }
}
