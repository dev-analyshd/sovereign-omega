import os
import json

try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False


class PharosClient:
    """
    All Pharos chain interactions go through this class.
    Rule 6: Keys are loaded from environment variables only. Never hardcoded.
    """

    MAINNET_RPC = "https://rpc.pharos.xyz"
    MAINNET_CHAIN = 1672

    TESTNET_RPC = "https://testnet.pharosnetwork.xyz"
    TESTNET_CHAIN = 688688

    def __init__(self):
        network = os.getenv("PHAROS_NETWORK", "testnet")

        if network == "mainnet":
            self.rpc = self.MAINNET_RPC
            self.chain_id = self.MAINNET_CHAIN
        else:
            self.rpc = self.TESTNET_RPC
            self.chain_id = self.TESTNET_CHAIN

        pk = os.getenv("AGENT_PRIVATE_KEY") or os.getenv("DEPLOYER_PRIVATE_KEY")
        if not pk:
            raise ValueError("AGENT_PRIVATE_KEY or DEPLOYER_PRIVATE_KEY not set in environment")

        if WEB3_AVAILABLE:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc))
            self.account = Account.from_key(pk)
            self.address = self.account.address
        else:
            self.w3 = None
            self.address = "0x0000000000000000000000000000000000000000"

        self.registry_address = os.getenv("PHAROS_REGISTRY")
        self.vault_address = os.getenv("PHAROS_VAULT")
        self.learner_address = os.getenv("PHAROS_LEARNER")

        self.registry = None
        self.vault = None
        self.learner = None

        if WEB3_AVAILABLE:
            self._load_contracts()

        print(f"[PHAROS] Connected to {network} (Chain ID: {self.chain_id})")
        print(f"[PHAROS] Agent address: {self.address}")

    def _load_contracts(self):
        abi_path = os.path.join(os.path.dirname(__file__), "abis")
        os.makedirs(abi_path, exist_ok=True)

        for name, addr, attr in [
            ("SovereignRegistry", self.registry_address, "registry"),
            ("SovereignVault", self.vault_address, "vault"),
            ("SovereignLearner", self.learner_address, "learner"),
        ]:
            abi_file = os.path.join(abi_path, f"{name}.json")
            if addr and os.path.exists(abi_file):
                with open(abi_file) as f:
                    abi = json.load(f)["abi"]
                contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(addr), abi=abi
                )
                setattr(self, attr, contract)

    def _build_and_send_tx(self, fn, value_wei: int = 0) -> str:
        if not WEB3_AVAILABLE or self.w3 is None:
            return "web3_unavailable"
        nonce = self.w3.eth.get_transaction_count(self.address)
        gas_price = self.w3.eth.gas_price
        tx = fn.build_transaction(
            {
                "from": self.address,
                "nonce": nonce,
                "gasPrice": gas_price,
                "value": value_wei,
                "chainId": self.chain_id,
            }
        )
        tx["gas"] = int(self.w3.eth.estimate_gas(tx) * 1.2)
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        if receipt["status"] == 0:
            raise Exception(f"Transaction failed: {tx_hash.hex()}")
        return tx_hash.hex()

    async def update_registry_moat(self, lambda_val: float, n_cycles: int, iq_val: float) -> str:
        if not self.registry:
            return "no_registry"
        fn = self.registry.functions.updateMoat(
            int(lambda_val * 1e18), n_cycles, int(iq_val * 1e18)
        )
        return self._build_and_send_tx(fn)

    async def record_silence_on_chain(self, psi: float, delta: float, reason: str) -> str:
        if not self.registry:
            return "no_registry"
        fn = self.registry.functions.recordSilence(
            int(psi * 1e18), int(delta * 1e18), reason[:200]
        )
        return self._build_and_send_tx(fn)

    async def vault_open_trade(self, trade_id: bytes, symbol: str, direction: str,
                               size_scaled: int, entry_price_scaled: int,
                               psi_scaled: int, delta_scaled: int) -> str:
        if not self.vault:
            return "no_vault"
        fn = self.vault.functions.openTrade(
            trade_id, symbol, direction, size_scaled, entry_price_scaled, psi_scaled, delta_scaled
        )
        return self._build_and_send_tx(fn)

    async def vault_close_trade(self, trade_id: bytes, exit_price_scaled: int, pnl_scaled: int) -> str:
        if not self.vault:
            return "no_vault"
        fn = self.vault.functions.closeTrade(trade_id, exit_price_scaled, pnl_scaled)
        return self._build_and_send_tx(fn)

    async def vault_record_silence(self, psi_scaled: int, delta_scaled: int) -> str:
        if not self.vault:
            return "no_vault"
        fn = self.vault.functions.recordSilencedTrade(psi_scaled, delta_scaled)
        return self._build_and_send_tx(fn)

    async def get_vault_balance(self) -> float:
        if not WEB3_AVAILABLE or self.w3 is None:
            return 0.0
        target = self.vault_address if self.vault_address else self.address
        return float(self.w3.eth.get_balance(target)) / 1e18

    async def update_domain_mastery_on_chain(self, domain: str, mastery: float, count: int) -> str:
        if not self.learner:
            return "no_learner"
        fn = self.learner.functions.updateDomainMastery(domain, int(mastery * 1e18), count)
        return self._build_and_send_tx(fn)

    async def is_connected(self) -> bool:
        if not WEB3_AVAILABLE or self.w3 is None:
            return False
        return self.w3.is_connected()
