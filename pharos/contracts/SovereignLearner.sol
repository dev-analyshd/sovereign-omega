// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * SOVEREIGN-Ω On-Chain Learning Ledger
 * Records intelligence milestones permanently on Pharos.
 * Every domain mastered. Every IQ growth. Immutable proof of learning.
 */
contract SovereignLearner {

    address public owner;
    address public agentOperator;

    struct DomainMastery {
        string  domain;
        uint256 masteryScaled;
        uint256 knowledgeCount;
        uint256 firstMastered;
        uint256 lastUpdated;
    }

    struct LearningMilestone {
        uint256 timestamp;
        string  milestoneType;
        string  domain;
        uint256 scoreBefore;
        uint256 scoreAfter;
    }

    mapping(string => DomainMastery) public domainMastery;
    string[] public masteredDomains;
    LearningMilestone[] public milestones;

    uint256 public totalKnowledgeItems;
    uint256 public peakIQScaled;

    event DomainMastered(string indexed domain, uint256 masteryScaled, uint256 knowledgeCount);
    event MilestoneReached(string milestoneType, string domain, uint256 scoreAfter);
    event IntelligenceRecord(uint256 iqScaled, uint256 timestamp);

    modifier onlyOperator() {
        require(msg.sender == agentOperator || msg.sender == owner, "Not authorized");
        _;
    }

    constructor(address _agentOperator) {
        owner = msg.sender;
        agentOperator = _agentOperator;
    }

    function updateDomainMastery(
        string calldata domain,
        uint256 masteryScaled,
        uint256 knowledgeCount
    ) external onlyOperator {
        DomainMastery storage dm = domainMastery[domain];
        bool wasUnmastered = dm.masteryScaled < 5e17;

        dm.domain = domain;
        dm.masteryScaled = masteryScaled;
        dm.knowledgeCount = knowledgeCount;
        dm.lastUpdated = block.timestamp;

        if (dm.firstMastered == 0) {
            dm.firstMastered = block.timestamp;
            masteredDomains.push(domain);
        }

        totalKnowledgeItems += knowledgeCount;

        if (wasUnmastered && masteryScaled >= 5e17) {
            emit DomainMastered(domain, masteryScaled, knowledgeCount);
            milestones.push(LearningMilestone({
                timestamp: block.timestamp,
                milestoneType: "domain_mastered",
                domain: domain,
                scoreBefore: dm.masteryScaled,
                scoreAfter: masteryScaled
            }));
        }
    }

    function recordIQMilestone(uint256 iqScaled) external onlyOperator {
        if (iqScaled > peakIQScaled) {
            peakIQScaled = iqScaled;
            emit IntelligenceRecord(iqScaled, block.timestamp);
        }
    }

    function getMasteredDomainsCount() external view returns (uint256) {
        return masteredDomains.length;
    }
}
