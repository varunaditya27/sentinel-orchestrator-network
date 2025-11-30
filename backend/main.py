from fastapi import FastAPI, WebSocket, BackgroundTasks, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from fpdf import FPDF
from message_bus import MessageBus
from agents import SentinelAgent, OracleAgent
from agents.specialists import (
    BlockScanner, StakeAnalyzer, VoteDoctor,
    MempoolSniffer, ReplayDetector
)
from agents.governance import (
    ProposalFetcher, PolicyAnalyzer, 
    SentimentAnalyzer, GovernanceOrchestrator,
    TreasuryGuardian
)
import uuid
import logging
import json
import base64
from datetime import datetime
import asyncio

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Sentinel Orchestrator Network (SON)",
    description="Blockchain security scanning with Sentinel & Oracle agents + Governance Analysis",
    version="2.0.0"
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MessageBus
message_bus = MessageBus()

# =============================================================================
# CORE AGENTS (Sentinel & Oracle)
# =============================================================================

# Initialize Agents
sentinel = SentinelAgent(enable_llm=True, enable_hydra=True)
oracle = OracleAgent(enable_llm=True)

# In-memory store for scan results (for reports/proofs)
results_store: Dict[str, Any] = {}

# Connect agents to each other
sentinel.set_oracle(oracle)

# Register core agents with MessageBus
message_bus.register_agent("did:masumi:sentinel_01", sentinel.get_public_key_b64())
message_bus.register_agent("did:masumi:oracle_01", oracle.get_public_key_b64())

logger.info("✅ Core agents initialized: Sentinel & Oracle")

# =============================================================================
# SPECIALIST AGENTS (Run in parallel within Oracle)
# =============================================================================
# Note: Specialist agents are instantiated within Oracle.process()
# They don't need separate registration unless running as independent microservices

specialist_agents = {
    "BlockScanner": BlockScanner,
    "StakeAnalyzer": StakeAnalyzer,
    "VoteDoctor": VoteDoctor,
    "MempoolSniffer": MempoolSniffer,
    "ReplayDetector": ReplayDetector,
}
logger.info(f"✅ Specialist agents available: {list(specialist_agents.keys())}")

# =============================================================================
# GOVERNANCE AGENTS
# =============================================================================

governance_orchestrator = GovernanceOrchestrator()
proposal_fetcher = ProposalFetcher()
policy_analyzer = PolicyAnalyzer()
sentiment_analyzer = SentimentAnalyzer()
treasury_guardian = TreasuryGuardian(enable_llm=True)

# Register governance agents with MessageBus
message_bus.register_agent("did:masumi:governance_orchestrator_01", 
                          governance_orchestrator.get_public_key_b64() if hasattr(governance_orchestrator, 'get_public_key_b64') else "")
logger.info("✅ Governance agents initialized: Orchestrator, ProposalFetcher, PolicyAnalyzer, SentimentAnalyzer")

# =============================================================================
# AGENT REGISTRY
# =============================================================================

agent_registry = {
    "core": {
        "sentinel": sentinel,
        "oracle": oracle,
    },
    "specialists": specialist_agents,
    "governance": {
        "governance_orchestrator": governance_orchestrator,
        "proposal_fetcher": proposal_fetcher,
        "policy_analyzer": policy_analyzer,
        "sentiment_analyzer": sentiment_analyzer,
        "treasury_guardian": treasury_guardian,
    }
}

logger.info(f"✅ Total agents registered: {len(message_bus.get_registered_agents())} in MessageBus")


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ScanRequest(BaseModel):
    """Request model for policy/transaction scan"""
    policy_id: Optional[str] = None
    tx_cbor: Optional[str] = None
    user_tip: int = 0  # User's node block height
    
    class Config:
        example = {
            "policy_id": "a" * 56,
            "user_tip": 1000
        }


class ScanResponse(BaseModel):
    """Response model for scan results"""
    task_id: str
    status: str
    policy_id: Optional[str] = None
    verdict: Optional[str] = None
    risk_score: Optional[int] = None
    reason: Optional[str] = None
    timestamp: Optional[str] = None


# =============================================================================
# BACKGROUND TASK: SENTINEL AGENT SCAN
# =============================================================================

async def run_sentinel_scan(policy_id: str, user_tip: int, task_id: str):
    """
    Run the Sentinel agent scan in background.
    Publishes results to MessageBus for WebSocket clients.
    """
    try:
        # Wait for client to connect via WebSocket
        await asyncio.sleep(1.0)
        
        logger.info(f"[{task_id}] Starting Sentinel scan for policy: {policy_id[:16]}...")
        
        # Prepare scan request for Sentinel agent
        scan_request = {
            "policy_id": policy_id,
            "user_tip": user_tip,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Run Sentinel agent
        result = await sentinel.process(scan_request)
        
        # Store result for report/proof retrieval
        results_store[task_id] = result
        
        # Build response envelope for MessageBus
        response_envelope = {
            "from_did": "did:masumi:sentinel_01",
            "payload": {
                "task_id": task_id,
                "policy_id": policy_id,
                "verdict": result.get("verdict"),
                "risk_score": result.get("risk_score"),
                "reason": result.get("reason"),
                "compliance": result.get("compliance"),
                "oracle_result": result.get("oracle_result"),
                "evidence_hash": result.get("evidence_hash"),
                "timestamp": result.get("timestamp"),
                "status": "completed"
            }
        }
        
        # Sign the envelope
        signed_envelope = sentinel._sign_envelope(response_envelope)
        
        # Publish to MessageBus
        await message_bus.publish(signed_envelope)
        
        logger.info(f"[{task_id}] Scan completed. Verdict: {result.get('verdict')}")
        
    except Exception as e:
        logger.error(f"[{task_id}] Scan failed: {str(e)}")
        
        # Publish error envelope
        error_envelope = {
            "from_did": "did:masumi:sentinel_01",
            "payload": {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        signed_error = sentinel._sign_envelope(error_envelope)
        await message_bus.publish(signed_error)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "Sentinel Orchestrator Network (SON)",
        "agents": {
            "sentinel": "Agent A - Orchestrator & Compliance Checker",
            "oracle": "Agent B - Blockchain Verifier & Fork Detection"
        }
    }


@app.post("/api/v1/scan", response_model=ScanResponse)
async def scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Submit a policy/transaction for security scanning.
    
    Returns a task_id that can be used to listen for results via WebSocket.
    """
    # Validate input
    if not request.policy_id and not request.tx_cbor:
        raise HTTPException(
            status_code=400,
            detail="Either policy_id or tx_cbor must be provided"
        )
    
    task_id = str(uuid.uuid4())
    
    logger.info(f"[{task_id}] Received scan request - policy: {request.policy_id or 'N/A'}")
    
    # Trigger Sentinel agent in background
    background_tasks.add_task(
        run_sentinel_scan,
        request.policy_id or request.tx_cbor,
        request.user_tip,
        task_id
    )
    
    return ScanResponse(
        task_id=task_id,
        status="processing",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

@app.get("/api/v1/report/{task_id}")
async def get_audit_report(task_id: str):
    """Generate and return a detailed audit report in PDF format."""
    if task_id not in results_store:
        raise HTTPException(status_code=404, detail="Task ID not found")
    
    result = results_store[task_id]
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Sentinel Orchestrator Network - Audit Report", ln=1, align="C")
    pdf.ln(10)
    
    # Metadata
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Report ID: AUDIT-{task_id[:8].upper()}", ln=1)
    pdf.cell(200, 10, txt=f"Timestamp: {datetime.utcnow().isoformat()}Z", ln=1)
    pdf.cell(200, 10, txt=f"Verdict: {result.get('verdict')}", ln=1)
    pdf.cell(200, 10, txt=f"Risk Score: {result.get('risk_score')}", ln=1)
    pdf.ln(10)
    
    # Details
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Analysis Details", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Reason: {result.get('reason')}")
    pdf.ln(5)
    
    pdf.cell(200, 10, txt=f"Policy ID: {result.get('policy_id')}", ln=1)
    pdf.cell(200, 10, txt=f"Hydra Verification: Enabled", ln=1)
    
    # Footer
    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, txt="Signed by: did:masumi:sentinel_01", ln=1, align="R")
    
    # Output
    # In fpdf2, output() returns bytearray by default if no name provided
    pdf_bytes = bytes(pdf.output())
    
    logger.info(f"Generated PDF report for {task_id}: {len(pdf_bytes)} bytes")
    
    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=AUDIT-{task_id[:8]}.pdf"
    })

@app.get("/api/v1/proof/{task_id}")
async def get_cryptographic_proof(task_id: str):
    """Return cryptographic proofs and signatures for the scan."""
    if task_id not in results_store:
        raise HTTPException(status_code=404, detail="Task ID not found")
    
    result = results_store[task_id]
    
    # Construct proof object
    proof = {
        "proof_id": f"PROOF-{task_id[:8].upper()}",
        "task_id": task_id,
        "verdict": result.get("verdict"),
        "signatures": [
            {
                "agent": "Sentinel Agent",
                "did": "did:masumi:sentinel_01",
                "signature": "base64_encoded_signature_placeholder", # In real app, this would be the actual sig
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            {
                "agent": "Hydra Head",
                "did": "did:masumi:hydra_head_01",
                "signature": "base64_encoded_signature_placeholder",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        ],
        "merkle_root": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", # Mock Merkle root
        "zk_proof": "0x..." # Mock ZK proof
    }
    return proof


@app.get("/api/v1/system/status")
async def get_system_status():
    """Return real-time status of the agent network."""
    # Check Hydra connection
    hydra_status = "Active" if sentinel.hydra_node and sentinel.hydra_node.client and sentinel.hydra_node.client.connection else "Offline"
    
    return {
        "sentinel": "Active",
        "oracle": "Standby", # Oracle is always standby in this demo until called
        "hydra": hydra_status,
        "midnight": "Offline", # Midnight is mocked for now
        "network_uptime": "99.9%",
        "active_agents": 3
    }

@app.get("/api/v1/scans/history")
async def get_scan_history():
    """Return recent scan history."""
    history = []
    for task_id, result in results_store.items():
        history.append({
            "task_id": task_id,
            "policy_id": result.get("policy_id"),
            "verdict": result.get("verdict"),
            "timestamp": result.get("timestamp"),
            "risk_score": result.get("risk_score")
        })
    # Sort by timestamp desc
    return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)

@app.get("/api/v1/agents/info")
async def agents_info():
    """Get information about all registered agents"""
    return {
        "core_agents": {
            "sentinel": {
                "did": "did:masumi:sentinel_01",
                "role": "orchestrator",
                "public_key": sentinel.get_public_key_b64()[:20] + "...",
                "status": "active",
                "description": "Primary orchestrator and protocol compliance checker"
            },
            "oracle": {
                "did": "did:masumi:oracle_01",
                "role": "blockchain_verifier",
                "public_key": oracle.get_public_key_b64()[:20] + "...",
                "status": "active",
                "description": "Blockchain verifier with specialist coordination",
                "specialists": list(oracle.specialists.keys()) if hasattr(oracle, 'specialists') else []
            }
        },
        "specialist_agents": {
            name: {
                "class": name,
                "role": "specialist",
                "status": "available",
                "description": f"{name} specialist agent"
            }
            for name in specialist_agents.keys()
        },
        "governance_agents": {
            "governance_orchestrator": {
                "role": "governance_coordinator",
                "status": "active",
                "description": "Coordinates governance analysis across all proposals"
            },
            "proposal_fetcher": {
                "role": "data_retriever",
                "status": "active",
                "description": "Fetches governance proposals from IPFS"
            },
            "policy_analyzer": {
                "role": "constitutional_analyzer",
                "status": "active",
                "description": "Analyzes constitutional compliance of proposals"
            },
            "sentiment_analyzer": {
                "role": "sentiment_analyzer",
                "status": "active",
                "description": "Analyzes community sentiment from on-chain votes"
            }
        },
        "total_agents": len(message_bus.get_registered_agents()),
        "registered_dids": message_bus.get_registered_agents()
    }


@app.get("/api/v1/agents/health")
async def agents_health():
    """Get health status of all agents"""
    health_status = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message_bus": "healthy",
        "agents": {}
    }
    
    # Core agents
    health_status["agents"]["sentinel"] = {
        "status": "healthy",
        "type": "core"
    }
    health_status["agents"]["oracle"] = {
        "status": "healthy",
        "type": "core"
    }
    
    # Specialist agents
    for name in specialist_agents.keys():
        health_status["agents"][name.lower()] = {
            "status": "healthy",
            "type": "specialist"
        }
    
    # Governance agents
    health_status["agents"]["governance_orchestrator"] = {
        "status": "healthy",
        "type": "governance"
    }
    health_status["agents"]["proposal_fetcher"] = {
        "status": "healthy",
        "type": "governance"
    }
    health_status["agents"]["policy_analyzer"] = {
        "status": "healthy",
        "type": "governance"
    }
    health_status["agents"]["sentiment_analyzer"] = {
        "status": "healthy",
        "type": "governance"
    }
    
    return health_status


@app.get("/api/v1/agents/list")
async def agents_list():
    """Get list of all available agents by category"""
    return {
        "core_agents": {
            "sentinel": "Sentinel Agent - Orchestrator & Compliance Checker",
            "oracle": "Oracle Agent - Blockchain Verifier"
        },
        "specialist_agents": {
            name: f"{name} - Specialist Agent"
            for name in specialist_agents.keys()
        },
        "governance_agents": {
            "governance_orchestrator": "Governance Orchestrator - Coordinates governance analysis",
            "proposal_fetcher": "Proposal Fetcher - Retrieves proposals from IPFS",
            "policy_analyzer": "Policy Analyzer - Checks constitutional compliance",
            "sentiment_analyzer": "Sentiment Analyzer - Analyzes community sentiment"
        },
        "summary": {
            "total_core_agents": 2,
            "total_specialist_agents": len(specialist_agents),
            "total_governance_agents": 4,
            "total_agents": 2 + len(specialist_agents) + 4
        }
    }


@app.get("/api/v1/specialist/{specialist_name}")
async def get_specialist_info(specialist_name: str):
    """Get information about a specific specialist agent"""
    specialist_key = specialist_name.title().replace("_", "")
    
    if specialist_key not in specialist_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Specialist '{specialist_name}' not found. Available: {list(specialist_agents.keys())}"
        )
    
    agent_class = specialist_agents[specialist_key]
    return {
        "name": specialist_name,
        "class": specialist_key,
        "status": "active",
        "description": f"{specialist_name} specialist analyzes blockchain data",
        "available": True
    }


@app.post("/api/v1/specialist/{specialist_name}/query")
async def query_specialist(specialist_name: str, request: Dict[str, Any]):
    """Query a specific specialist agent for analysis"""
    specialist_key = specialist_name.title().replace("_", "")
    
    if specialist_key not in specialist_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Specialist '{specialist_name}' not found"
        )
    
    try:
        agent_class = specialist_agents[specialist_key]
        # Instantiate the specialist and run process
        agent_instance = agent_class()
        result = agent_instance.process(request.get("data", ""))
        
        return {
            "specialist": specialist_name,
            "query": request,
            "result": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "completed"
        }
    except Exception as e:
        logging.error(f"Error querying specialist {specialist_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/governance")
async def governance_status():
    """Get governance analysis system status"""
    return {
        "status": "operational",
        "agents": {
            "governance_orchestrator": {
                "status": "active",
                "role": "coordinator",
                "description": "Coordinates governance analysis"
            },
            "proposal_fetcher": {
                "status": "active",
                "role": "data_retriever",
                "description": "Fetches proposals from IPFS"
            },
            "policy_analyzer": {
                "status": "active",
                "role": "compliance_checker",
                "description": "Checks constitutional compliance"
            },
            "sentiment_analyzer": {
                "status": "active",
                "role": "sentiment_analyzer",
                "description": "Analyzes community sentiment"
            }
        },
        "last_analysis": None,
        "active_analyses": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/api/v1/governance/analyze")
async def analyze_governance(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Submit governance proposals for analysis.
    Coordinates ProposalFetcher, PolicyAnalyzer, and SentimentAnalyzer.
    """
    task_id = str(uuid.uuid4())
    
    try:
        # Fetch proposals if not provided
        if "proposals" not in request:
            fetch_result = proposal_fetcher.process({})
            proposals = fetch_result.get("proposals", [])
        else:
            proposals = request.get("proposals", [])
        
        # Analyze policy compliance
        policy_result = policy_analyzer.process(proposals)
        
        # Analyze sentiment
        sentiment_result = sentiment_analyzer.process(proposals)
        
        # Orchestrate final analysis
        orchestration_result = governance_orchestrator.process({
            "proposals": proposals,
            "policy_analysis": policy_result,
            "sentiment_analysis": sentiment_result
        })
        
        return {
            "task_id": task_id,
            "status": "completed",
            "proposals_analyzed": len(proposals),
            "policy_analysis": policy_result,
            "sentiment_analysis": sentiment_result,
            "orchestration": orchestration_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logging.error(f"Error in governance analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/governance/proposal-check")
async def check_proposal(request: Dict[str, Any]):
    """Check a specific proposal for constitutional compliance"""
    try:
        proposal = request.get("proposal", {})
        
        # Check policy compliance
        policy_result = policy_analyzer.process([proposal])
        
        # Analyze sentiment
        sentiment_result = sentiment_analyzer.process([proposal])
        
        return {
            "proposal_id": proposal.get("id"),
            "policy_compliance": policy_result,
            "sentiment": sentiment_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logging.error(f"Error checking proposal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# TREASURY GUARDIAN ENDPOINTS
# =============================================================================

@app.post("/api/v1/treasury/analyze")
async def analyze_treasury_proposal(request: Dict[str, Any]):
    """
    Analyze a treasury withdrawal proposal for anomalies.
    """
    try:
        result = await treasury_guardian.process(request)
        return result
    except Exception as e:
        logging.error(f"Error in treasury analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/treasury/risk/current")
async def get_current_treasury_risk():
    """
    Get the current treasury risk report (daily summary).
    """
    # For MVP, we generate a fresh report based on a mock "current state"
    # In production, this would return the latest cached daily report
    try:
        # Mocking a "current" proposal for the report
        mock_proposal = {
            "proposal_id": "gov_action_" + str(uuid.uuid4())[:8],
            "amount": 50_000_000_000_000, # 50M ADA
            "proposer_id": "stake_test1...",
            "metadata": {
                "title": "Ecosystem Growth Fund",
                "abstract": "We want 50M ADA to grow the ecosystem.",
                "rationale": "Trust us."
            }
        }
        result = await treasury_guardian.process(mock_proposal)
        return {
            "date": datetime.utcnow().date().isoformat(),
            "epoch": 450, # Mock epoch
            "treasury_balance_ada": 1_500_000_000,
            "active_proposals": 1,
            "high_risk_proposals": 1 if result["risk_score"] > 50 else 0,
            "latest_analysis": result
        }
    except Exception as e:
        logging.error(f"Error getting treasury risk: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WEBSOCKET ENDPOINT FOR REAL-TIME RESULTS
# =============================================================================

@app.websocket("/ws/scan/{task_id}")
async def websocket_scan(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint to receive real-time scan results.
    
    Clients connect with: ws://localhost:8000/ws/scan/{task_id}
    Server publishes results when Sentinel completes the scan.
    """
    await message_bus.connect(websocket)
    logger.info(f"Client connected to scan results: {task_id}")
    
    try:
        while True:
            # Keep connection open and receive messages
            data = await websocket.receive_text()
            logger.debug(f"Received from client [{task_id}]: {data}")
            
    except Exception as e:
        logger.info(f"WebSocket closed for task {task_id}: {str(e)}")
    finally:
        message_bus.disconnect(websocket)


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    General WebSocket endpoint for agent activity logs.
    Broadcasts all agent events.
    """
    await message_bus.connect(websocket)
    logger.info("Client connected to activity logs")
    
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        logger.info(f"WebSocket closed: {str(e)}")
    finally:
        message_bus.disconnect(websocket)
