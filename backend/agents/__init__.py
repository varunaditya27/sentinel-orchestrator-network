"""
=============================================================================
Sentinel Orchestrator Network (SON) - Agents Package
=============================================================================

SIMPLIFIED AGENTIC ARCHITECTURE (2-AGENT VERSION)
Based on simplified_agent_flow.txt

This package contains the AI agent modules that form the SON threat detection
system. The simplified flow uses only Sentinel and Oracle agents.

Workflow:
    User → Sentinel Agent ↔ Oracle Agent → Final Verdict

Agents:
    - sentinel.py : Agent A - Orchestrator, compliance checker, verdict issuer
    - oracle.py   : Agent B - Blockchain verifier, fork detection

Integration Points:
    - Masumi: Agent registry, micropayments, reputation
    - Blockfrost: Cardano blockchain data
    - Ed25519: Cryptographic message signing

=============================================================================
"""

# =============================================================================
# BASE CLASSES & COMMON TYPES
# =============================================================================

from .base import (
    BaseAgent,
    Vote,
    Severity,
)

# =============================================================================
# LLM CONFIGURATION (Gemini Integration)
# =============================================================================

from .llm_config import (
    AgentLLM,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LLM_ENABLED,
    init_gemini_client,
    get_gemini_model,
)

# =============================================================================
# AGENT IMPLEMENTATIONS
# =============================================================================

from .sentinel import SentinelAgent, ComplianceStatus
from .oracle import OracleAgent
from .compliance import ComplianceAgent, RiskModifier
from .consensus import ConsensusAgent, ConsensusStatus

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Base classes
    "BaseAgent",
    "Vote",
    "Severity",

    # LLM Configuration
    "AgentLLM",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "LLM_ENABLED",
    "init_gemini_client",
    "get_gemini_model",

    # Agents
    "SentinelAgent",
    "OracleAgent",
    "ComplianceAgent",
    "ConsensusAgent",

    # Enums
    "ComplianceStatus",
    "RiskModifier",
    "ConsensusStatus",
]
