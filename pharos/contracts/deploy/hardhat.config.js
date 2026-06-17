require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../../../.env" });

const DEPLOYER_PK = process.env.DEPLOYER_PRIVATE_KEY;
const accounts = DEPLOYER_PK ? [DEPLOYER_PK] : [];

module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: { enabled: true, runs: 200 }
    }
  },
  networks: {
    pharos_testnet: {
      url: "https://testnet.pharosnetwork.xyz",
      chainId: 688688,
      accounts,
      gasPrice: "auto",
      timeout: 60000
    },
    pharos_mainnet: {
      url: "https://rpc.pharos.xyz",
      chainId: 1672,
      accounts,
      gasPrice: "auto",
      timeout: 60000
    }
  },
  etherscan: {
    apiKey: {
      pharos_testnet: "no-key-needed",
      pharos_mainnet: "no-key-needed"
    },
    customChains: [
      {
        network: "pharos_testnet",
        chainId: 688688,
        urls: {
          apiURL: "https://testnet.pharosscan.xyz/api",
          browserURL: "https://testnet.pharosscan.xyz"
        }
      },
      {
        network: "pharos_mainnet",
        chainId: 1672,
        urls: {
          apiURL: "https://pharosscan.xyz/api",
          browserURL: "https://pharosscan.xyz"
        }
      }
    ]
  }
};
