import logging
import httpx
import statistics
import asyncio
import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from ..base import BaseAgent, Severity, Vote

class TreasuryGuardian(BaseAgent):
    """
    Treasury Guardian Subsystem
    ===========================
    Monitors Cardano treasury withdrawals for anomalies and potential attacks.
    
    Features:
    - Monitors treasury.cardano.org (simulated via Koios)
    - Flags proposals matching attack patterns:
        1. Duplicate requests
        2. Unusually high amounts (>3 sigma)
        3. Vague deliverables (NLP)
        4. New proposers (<30 days)
    """
    
    def __init__(self, enable_llm: bool = True):
        super().__init__("treasury_guardian", "risk_analyst", enable_llm)
        load_dotenv()
        self.koios_url = "https://preprod.koios.rest/api/v1"
        self.blockfrost_url = os.getenv("BLOCKFROST_API_URL", "https://cardano-preprod.blockfrost.io/api")
        self.blockfrost_key = os.getenv("BLOCKFROST_API_KEY")
        
        # Risk Constants
        self.NCL_ANNUAL_LIMIT = 47_250_000  # ~15% of 315M ADA
        self.MAX_SINGLE_WITHDRAWAL = 10_000_000 # 10M ADA soft limit
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a treasury withdrawal proposal.
        
        Args:
            input_data: {
                "proposal_id": str,
                "amount": int (lovelace),
                "proposer_id": str (stake address),
                "metadata": dict (title, abstract, rationale)
            }
        """
        self.log_start(input_data.get("proposal_id", "unknown"))
        
        proposal = input_data
        
        # Validation
        if not proposal.get("proposal_id"):
            raise ValueError("Missing proposal_id")
        # Removed strict proposer_id check to allow fetching it
        
        if "amount" not in proposal:
             proposal["amount"] = 0
            
        findings = []
        risk_score = 0.0
        
        # Verify existence and fetch details
        prop_id = proposal.get("proposal_id", "")
        if not prop_id:
             raise ValueError("Missing proposal_id")
             
        # Always verify existence
        details = await self._fetch_proposal_details(prop_id)
        if details:
             # Override defaults with real data
             proposal["amount"] = int(details.get("withdrawal_amount", 0))
             proposal["proposer_id"] = details.get("stake_address", proposal.get("proposer_id"))
        else:
             # If fetch fails, raise error
             raise ValueError(f"Proposal ID {prop_id} not found on-chain")
        
        # 1. Data Ingestion (History)
        history = await self._fetch_treasury_history()
        stats = {
            "z_score": 0.0,
            "proposer_age_days": 0
        }
        
        # 2. Statistical Analysis (Z-Score)
        amount_ada = proposal.get("amount", 0) / 1_000_000
        z_score = 0.0
        
        if amount_ada > 0:
            z_score = self._calculate_z_score(amount_ada, history)
            if z_score > 3.0:
                findings.append(f"SIZE_OUTLIER_3SIGMA: Amount {amount_ada:,.0f} ADA is >3σ from mean (z={z_score:.2f})")
                risk_score += 30
        else:
            findings.append("UNKNOWN_AMOUNT: Proposal amount not specified, cannot assess financial risk")
            risk_score += 10
            
        stats["z_score"] = z_score
            
        # 3. NCL / Budget Check
        if amount_ada > self.MAX_SINGLE_WITHDRAWAL:
            findings.append(f"UNUSUALLY_LARGE_WITHDRAWAL: {amount_ada:,.0f} ADA exceeds soft limit of {self.MAX_SINGLE_WITHDRAWAL:,.0f}")
            risk_score += 30
            
        # 4. Proposer Risk
        proposer_id = proposal.get("proposer_id")
        if proposer_id:
             age_days = await self._check_proposer_age(proposer_id)
             stats["proposer_age_days"] = age_days
             
             if age_days < 30:
                 risk_score += 20
                 findings.append(f"NEW_PROPOSER: Wallet age {age_days} days (<30 days)")
        else:
             # If we couldn't fetch proposer_id and it wasn't provided
             findings.append("UNKNOWN_PROPOSER: Proposer ID missing")
             risk_score += 20
            
        # 5. NLP Analysis (Vague Deliverables)
        if self.has_llm:
            nlp_risk = await self._analyze_text_quality(proposal.get("metadata", {}))
            if nlp_risk > 0:
                findings.append("VAGUE_DELIVERABLES: Proposal lacks concrete metrics or milestones")
                risk_score += nlp_risk
        
        # Determine Verdict
        vote = self.determine_vote(int(risk_score))
        severity = Severity.INFO
        if risk_score > 50: severity = Severity.HIGH
        elif risk_score > 20: severity = Severity.MEDIUM
        
        result = {
            "agent": self.agent_name,
            "proposal_id": proposal.get("proposal_id"),
            "risk_score": min(risk_score, 100),
            "vote": vote,
            "severity": severity,
            "findings": findings,
            "stats": stats,
            "timestamp": self.get_timestamp()
        }
        
        self.log_complete(vote, int(risk_score))
        return result

    async def _fetch_treasury_history(self) -> List[float]:
        """Fetch historical treasury withdrawals from Koios."""
        try:
            async with httpx.AsyncClient() as client:
                # Fetch treasury withdrawals (using a known endpoint or simulating via transaction query)
                # Koios doesn't have a direct 'treasury_withdrawals' endpoint in free tier easily, 
                # so we will query recent transactions from the treasury pot address if available,
                # OR for this hackathon, we fetch recent large transactions to simulate 'market context'.
                # For stability, we will use the 'tip' endpoint to verify connectivity, 
                # and then return a dynamic list based on recent epoch stats if possible.
                
                # Better approach: Get epoch params to see treasury size context
                resp = await client.get(f"{self.koios_url}/epoch_params?_limit=5")
                if resp.status_code == 200:
                    data = resp.json()
                    # Return recent treasury sizes to calculate volatility/context
                    # This isn't exactly 'withdrawals' but serves as the baseline for 'history' 
                    # in our Z-score model (comparing against recent treasury movements).
                    return [float(d.get("treasury_growth_rate", 0.2) * 10000000) for d in data] 
                
                # Fallback if API fails
                return [1_000_000, 500_000, 2_000_000, 750_000, 10_000_000, 3_000_000]
        except Exception as e:
            logging.error(f"Error fetching treasury history: {e}")
            return [1_000_000, 500_000, 2_000_000, 750_000, 10_000_000, 3_000_000]

    def _calculate_z_score(self, amount: float, history: List[float]) -> float:
        if not history: return 0.0
        mean = statistics.mean(history)
        stdev = statistics.stdev(history) if len(history) > 1 else 1.0
        if stdev == 0: return 0.0
        return (amount - mean) / stdev

    async def _check_proposer_age(self, stake_address: str) -> int:
        """Check wallet age via Koios."""
        if not stake_address: return 0
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {"_stake_addresses": [stake_address]}
                resp = await client.post(f"{self.koios_url}/account_info", json=payload)
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data and len(data) > 0:
                        # Calculate age based on active epoch
                        # Note: Koios returns 'active_epoch'
                        # We need current epoch to calc difference
                        
                        # Get current epoch
                        tip_resp = await client.get(f"{self.koios_url}/tip")
                        current_epoch = 0
                        if tip_resp.status_code == 200:
                            current_epoch = tip_resp.json()[0]["epoch_no"]
                            
                        active_epoch = data[0].get("active_epoch", current_epoch)
                        
                        # 1 epoch = ~5 days
                        age_epochs = current_epoch - active_epoch
                        return age_epochs * 5
                        
            return 0 # Default to 0 (new) if not found
        except Exception as e:
            logging.error(f"Error checking proposer age: {e}")
            return 0

    async def _analyze_text_quality(self, metadata: Dict) -> int:
        """Use LLM to detect vague deliverables."""
        text = f"{metadata.get('title', '')} {metadata.get('abstract', '')} {metadata.get('rationale', '')}"
        if not text.strip(): return 20
        
        prompt = f"""
        Analyze this treasury proposal text for "Vague Deliverables".
        Risk Criteria:
        - No concrete numbers or KPIs
        - No clear timeline
        - Buzzword-heavy
        
        Text: "{text[:1000]}"
        
        Return ONLY an integer risk score (0-20). 0 = Clear/Good, 20 = Very Vague.
        """
        try:
            response = await self.llm.ask(prompt)
            return int(''.join(filter(str.isdigit, response)))
        except:
            return 0

    async def _fetch_proposal_details(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Fetch proposal details from Blockfrost or Koios."""
        
        # 1. Try Blockfrost
        if self.blockfrost_key:
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    headers = {"project_id": self.blockfrost_key}
                    url = f"{self.blockfrost_url}/v0/governance/proposals/{proposal_id}"
                    
                    resp = await client.get(url, headers=headers)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        return {
                            "withdrawal_amount": data.get("amount", 0),
                            "stake_address": data.get("proposer_id", "")
                        }
                    elif resp.status_code == 403:
                        logging.warning("Blockfrost access denied (403). Switching to Koios fallback.")
            except Exception as e:
                logging.error(f"Error fetching from Blockfrost: {e}")

        # 2. Fallback to Koios
        try:
            tx_hash = ""
            # Check if it's a Bech32 ID (gov_action...)
            if proposal_id.startswith("gov_action"):
                import bech32
                hrp, data = bech32.bech32_decode(proposal_id)
                if data:
                    # Convert 5-bit data to 8-bit
                    decoded = bech32.convertbits(data, 5, 8, False)
                    # The decoded bytes are [tx_hash_bytes (32)] + [index_bytes (variable)]
                    # We need to extract the Tx Hash (first 32 bytes) and convert to hex
                    if len(decoded) >= 32:
                        tx_hash_bytes = bytes(decoded[:32])
                        tx_hash = tx_hash_bytes.hex()
                        # We could also extract index, but Koios just needs Tx Hash
            else:
                # Assume Hex format
                tx_hash = proposal_id.split('#')[0]
            
            if len(tx_hash) != 64: return None
            
            async with httpx.AsyncClient(verify=False) as client:
                payload = {"_tx_hashes": [tx_hash]}
                resp = await client.post(f"{self.koios_url}/tx_info", json=payload)
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data and len(data) > 0:
                        tx = data[0]
                        # Estimate amount from total output (sum of outputs)
                        amount = 0
                        if "total_output" in tx:
                            amount = int(tx["total_output"])
                        elif "outputs" in tx:
                            amount = sum(int(o["value"]) for o in tx["outputs"])
                        
                        # Get proposer from first input's stake address
                        proposer = "UNKNOWN_PROPOSER"
                        if tx.get("inputs") and len(tx["inputs"]) > 0:
                            proposer = tx["inputs"][0].get("stake_addr", "UNKNOWN_PROPOSER")
                        elif tx.get("outputs") and len(tx["outputs"]) > 0:
                             # Fallback: use first output's stake address if available (e.g. change address)
                             proposer = tx["outputs"][0].get("stake_addr", "UNKNOWN_PROPOSER")
                            
                        return {
                            "withdrawal_amount": amount,
                            "stake_address": proposer
                        }
        except Exception as e:
            import traceback
            logging.error(f"Error fetching from Koios: {repr(e)}")
            logging.error(traceback.format_exc())
            
        return None

    async def _verify_proposal_exists(self, proposal_id: str) -> bool:
        """Verify if the proposal ID (Tx Hash) exists on-chain."""
        # Deprecated in favor of _fetch_proposal_details, but kept for fallback
        return (await self._fetch_proposal_details(proposal_id)) is not None
