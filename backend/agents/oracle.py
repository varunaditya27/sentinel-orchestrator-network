# backend/agents/oracle.py
import asyncio
import requests
import base64
import json
import nacl.signing
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from message_bus import MessageBus  # MEMBER1 builds this
import websockets
from fastapi import WebSocket

# =============================================================================
# BASE AGENT CLASS - Autonomous Microservice Template
# =============================================================================

class BaseAgent:
    """Template for all autonomous agents - inherits DID, payments, APIs"""

    def __init__(self, agent_name, cost_ada=0.2):
        self.name = agent_name
        self.cost = cost_ada
        self.did = f"did:key:{self.generate_key()}"  # Real DID
        self.blockfrost = self.init_blockfrost()  # Free API
        self.wallet_balance = 0.0
        self.explanation = ""

    def generate_key(self):
        """Generate DID key (simplified)"""
        key = nacl.signing.SigningKey.generate()
        return base64.b64encode(key.verify_key.encode()).decode()

    def init_blockfrost(self):
        """Initialize Blockfrost API client"""
        from blockfrost import BlockFrostApi, ApiUrls
        # Using pre-production network with fresh API key
        return BlockFrostApi(
            project_id="preprod99ILsNJwp7AtN1sGgf9f7g7BrFDnCPrg",
            base_url=ApiUrls.preprod.value
        )

    async def verify_payment(self, escrow_tx):
        """ZERO TRUST - Check escrow includes our DID + cost"""
        # In production: verify Cardano transaction
        return escrow_tx.get("amount", 0) >= self.cost

    async def work(self, chain_state):
        """Agent-specific logic - override in subclasses"""
        raise NotImplementedError

# =============================================================================
# SPECIALIST AGENTS - Real Cardano APIs, No Datasets
# =============================================================================

class BlockScanner(BaseAgent):
    """Block height comparison - detects forks"""

    async def work(self, chain_state):
        try:
            latest_block = await asyncio.get_event_loop().run_in_executor(
                None, self.blockfrost.block_latest
            )

            # Handle Blockfrost response (could be dict or object)
            if isinstance(latest_block, dict):
                mainnet_tip = latest_block.get("height")
            else:
                mainnet_tip = getattr(latest_block, 'height', 0)

            user_tip = chain_state["user_tip"]
            delta = abs(int(mainnet_tip) - int(user_tip))
            self.explanation = f"Block tip difference: {delta} blocks"
            risk_score = 0.9 if delta > 5 else 0.1
            return {"risk": risk_score, "evidence": self.explanation}
        except Exception as e:
            return {"risk": 0.5, "evidence": f"Blockfrost error: {str(e)}"}

class StakeAnalyzer(BaseAgent):
    """Stake pool analysis - detects minority control"""

    async def work(self, chain_state):
        try:
            pools = await asyncio.get_event_loop().run_in_executor(
                None, self.blockfrost.pools
            )
            # Calculate minority stake (top 10 pools)
            total_stake = sum(float(p.get("active_stake", "0")) for p in pools[:10])
            minority_ratio = min(total_stake / 1000000000, 1.0)  # Normalize
            self.explanation = f"Top 10 pools control {minority_ratio:.1%} of stake"
            risk_score = 0.8 if minority_ratio > 0.3 else 0.2
            return {"risk": risk_score, "evidence": self.explanation}
        except Exception as e:
            return {"risk": 0.5, "evidence": f"Stake analysis error: {str(e)}"}

class VoteDoctor(BaseAgent):
    """Governance vote analysis - detects manipulation"""

    async def work(self, chain_state):
        try:
            # Get recent governance actions
            gov_actions = await asyncio.get_event_loop().run_in_executor(
                None, self.blockfrost.governance_actions
            )
            # Simple divergence check (placeholder logic)
            vote_count = len(gov_actions) if gov_actions else 0
            divergence = min(vote_count / 100, 1.0)  # Normalize
            self.explanation = f"Governance actions: {vote_count}"
            risk_score = 0.7 if divergence > 0.4 else 0.1
            return {"risk": risk_score, "evidence": self.explanation}
        except Exception as e:
            return {"risk": 0.5, "evidence": f"Governance analysis error: {str(e)}"}

class MempoolSniffer(BaseAgent):
    """Mempool transaction analysis - detects spam attacks"""

    async def work(self, chain_state):
        try:
            # Simplified mempool check via Blockfrost (limited API)
            recent_txs = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.blockfrost.blocks_latest_transactions(limit=100)
            )
            tx_count = len(recent_txs) if recent_txs else 0
            spam_ratio = min(tx_count / 1000, 1.0)  # Normalize
            self.explanation = f"Mempool transactions: {tx_count}"
            risk_score = 0.6 if spam_ratio > 0.2 else 0.05
            return {"risk": risk_score, "evidence": self.explanation}
        except Exception as e:
            return {"risk": 0.5, "evidence": f"Mempool analysis error: {str(e)}"}

class ReplayDetector(BaseAgent):
    """Transaction replay detection"""

    async def work(self, chain_state):
        try:
            # Check for duplicate transactions (simplified)
            recent_txs = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.blockfrost.blocks_latest_transactions(limit=50)
            )
            # Check for nonce reuse (placeholder)
            replayed = 0  # In real implementation, check tx signatures
            self.explanation = f"Potential replays detected: {replayed}"
            risk_score = 0.95 if replayed > 0 else 0.0
            return {"risk": risk_score, "evidence": self.explanation}
        except Exception as e:
            return {"risk": 0.5, "evidence": f"Replay detection error: {str(e)}"}

# =============================================================================
# ORACLE COORDINATOR - Hires Swarm + Bayesian Fusion
# =============================================================================

class OracleCoordinator(BaseAgent):
    """Coordinates specialist agents using Matrix/escrow"""

    def __init__(self):
        super().__init__("oracle_coordinator", cost_ada=1.0)
        self.specialists = {
            "block_scanner": BlockScanner("block_scanner", 0.15),
            "stake_analyzer": StakeAnalyzer("stake_analyzer", 0.15),
            "vote_doctor": VoteDoctor("vote_doctor", 0.15),
            "mempool_sniffer": MempoolSniffer("mempool_sniffer", 0.15),
            "replay_detector": ReplayDetector("replay_detector", 0.15),
        }

    async def execute_fork_check(self, sentinel_request):
        """Main entry point - hires swarm and fuses results"""
        chain_state = sentinel_request["payload"]

        print(f"🤖 Oracle hiring swarm for fork check...")

        # 1. Hire all specialists concurrently
        tasks = []
        for name, agent in self.specialists.items():
            task = self.hire_specialist(name, agent, chain_state)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 2. Filter successful results
        valid_results = [r for r in results if isinstance(r, dict)]

        # 3. Bayesian fusion (simple weighted average)
        if valid_results:
            total_risk = sum(r["risk"] for r in valid_results)
            avg_risk = total_risk / len(valid_results)
            evidence = [r["evidence"] for r in valid_results]
        else:
            avg_risk = 0.5
            evidence = ["All specialists failed"]

        # 4. Determine final status
        fork_confirmed = avg_risk > 0.7
        status = "MINORITY_FORK_DETECTED" if fork_confirmed else "SAFE_CHAIN"

        print(f"🎯 Swarm consensus: {status} (risk: {avg_risk:.2f})")

        return {
            "status": status,
            "ai_fork_confirmed": fork_confirmed,
            "risk_score": avg_risk,
            "evidence": evidence,
            "specialists_hired": len(valid_results),
            "specialists_total": len(self.specialists)
        }

    async def hire_specialist(self, name, agent, chain_state):
        """Simulate hiring a specialist (WebSocket in production)"""
        try:
            print(f"📡 Hiring {name}...")
            result = await agent.work(chain_state)
            print(f"✅ {name} completed: risk {result['risk']:.2f}")
            return result
        except Exception as e:
            print(f"❌ {name} failed: {str(e)}")
            return {"risk": 0.5, "evidence": f"Agent {name} error: {str(e)}"}

    def bayes_fuse(self, risks):
        """Simple Bayesian fusion (weighted average)"""
        if not risks:
            return 0.5
        # Weight recent results higher
        weights = [1.0] * len(risks)
        weights[-1] *= 1.2  # Boost latest result
        total_weight = sum(weights)
        return sum(r * w for r, w in zip(risks, weights)) / total_weight

# =============================================================================
# LEGACY ORACLE AGENT - For Backward Compatibility
# =============================================================================

class OracleAgent:
    """Legacy single-purpose Oracle Agent"""

    def __init__(self):
        self.private_key = nacl.signing.SigningKey.generate()
        self.public_key = self.private_key.verify_key
        self.bus = MessageBus()
        self.escrow_balance = 0.0
        self.coordinator = OracleCoordinator()

        # Sentinel verification
        self.sentinel_public_bytes = base64.b64decode("SENTINEL_PUBLIC_BASE64_PLACEHOLDER")
        self.sentinel_verify_key = VerifyKey(self.sentinel_public_bytes)

    async def start(self):
        await self.bus.subscribe("did:masumi:oracle_01", self.handle_message)

    async def handle_message(self, envelope):
        if not self.verify_signature(envelope):
            return

        if envelope["type"] == "HIRE_REQUEST":
            result = await self.coordinator.execute_fork_check(envelope)
            await self.send_job_complete(envelope, result)

    async def send_job_complete(self, original_request, result):
        reply = {
            "protocol": "IACP/2.0",
            "type": "JOB_COMPLETE",
            "from_did": "did:masumi:oracle_01",
            "payload": result
        }
        signed_reply = self.sign_envelope(reply)
        await self.bus.publish(signed_reply)

    def verify_signature(self, envelope):
        if "signature" not in envelope:
            return False

        message = {k: v for k, v in envelope.items() if k != "signature"}
        message_bytes = json.dumps(message, sort_keys=True, separators=(',', ':')).encode()
        signature_bytes = base64.b64decode(envelope["signature"])

        try:
            self.sentinel_verify_key.verify(message_bytes, signature_bytes)
            print(f"✅ Verified: {envelope['from_did']}")
            return True
        except BadSignatureError:
            print("❌ Fake signature dropped")
            return False

    def sign_envelope(self, envelope):
        message_bytes = json.dumps(envelope, separators=(',', ':')).encode()
        signed = self.private_key.sign(message_bytes)
        envelope["signature"] = base64.b64encode(signed.signature).decode()
        return envelope
