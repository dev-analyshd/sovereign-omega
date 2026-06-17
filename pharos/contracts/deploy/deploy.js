const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = hre.network.name;

  console.log(`\n============================================`);
  console.log(` SOVEREIGN-Ω Contract Deployment`);
  console.log(` Network: ${network}`);
  console.log(`============================================`);
  console.log(`Deployer: ${deployer.address}`);

  const balance = await deployer.provider.getBalance(deployer.address);
  console.log(`Balance: ${ethers.formatEther(balance)} (native token)`);

  if (balance === 0n) {
    console.error("\nERROR: Deployer has no balance. Fund your wallet first.");
    console.log(`Faucet (testnet): https://testnet.pharosnetwork.xyz/`);
    process.exit(1);
  }

  const agentOperator = process.env.AGENT_OPERATOR_ADDRESS || deployer.address;
  console.log(`Agent Operator: ${agentOperator}\n`);

  // 1. Deploy Registry
  console.log("Deploying SovereignRegistry...");
  const Registry = await ethers.getContractFactory("SovereignRegistry");
  const registry = await Registry.deploy(agentOperator);
  await registry.waitForDeployment();
  const registryAddr = await registry.getAddress();
  console.log(`  SovereignRegistry: ${registryAddr}`);

  // 2. Deploy Vault
  console.log("Deploying SovereignVault...");
  const Vault = await ethers.getContractFactory("SovereignVault");
  const vault = await Vault.deploy(agentOperator, registryAddr);
  await vault.waitForDeployment();
  const vaultAddr = await vault.getAddress();
  console.log(`  SovereignVault:    ${vaultAddr}`);

  // 3. Deploy Learner
  console.log("Deploying SovereignLearner...");
  const Learner = await ethers.getContractFactory("SovereignLearner");
  const learner = await Learner.deploy(agentOperator);
  await learner.waitForDeployment();
  const learnerAddr = await learner.getAddress();
  console.log(`  SovereignLearner:  ${learnerAddr}`);

  console.log("\n============================================");
  console.log(" DEPLOYMENT COMPLETE");
  console.log("============================================");

  const explorerBase = network === "pharos_mainnet"
    ? "https://pharosscan.xyz/address"
    : "https://testnet.pharosscan.xyz/address";

  console.log(`\nExplorer links:`);
  console.log(`  Registry: ${explorerBase}/${registryAddr}`);
  console.log(`  Vault:    ${explorerBase}/${vaultAddr}`);
  console.log(`  Learner:  ${explorerBase}/${learnerAddr}`);

  console.log(`\nAdd to .env:`);
  console.log(`PHAROS_REGISTRY=${registryAddr}`);
  console.log(`PHAROS_VAULT=${vaultAddr}`);
  console.log(`PHAROS_LEARNER=${learnerAddr}`);

  // Write deployment output to file
  const deployOutput = {
    network,
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    registry: registryAddr,
    vault: vaultAddr,
    learner: learnerAddr,
  };

  const outDir = path.join(__dirname, "..", "..", "deployments");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(
    path.join(outDir, `${network}_latest.json`),
    JSON.stringify(deployOutput, null, 2)
  );
  console.log(`\nDeployment saved to: pharos/deployments/${network}_latest.json`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
