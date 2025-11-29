# 🛡️ Sentinel Orchestrator Network (SON)

> The Unified Trust Engine for Cardano (Masumi + Hydra + Midnight)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Cardano Hackathon](https://img.shields.io/badge/Hackathon-Cardano%20Asia%202025-orange)](https://hackathon.cardano.org/)

**Submission for Cardano Hackathon Asia (IBW 2025)**

## 🚀 The Vision

SON is a decentralized "Bodyguard Swarm" that protects users from DeFi threats in real-time. It unifies AI-powered threat detection, decentralized oracles, and multi-agent consensus into a single, Hydra-accelerated infrastructure for Cardano.

### The User Journey

1. **Trigger:** User scans a Policy ID on the Dashboard.
2. **Swarm:** 5 Agents (Sentinel, Oracle, Compliance, ZK-Prover, Consensus) activate via **Masumi**.
3. **Privacy:** Threats verified via **Midnight ZK-Proofs** (preserving agent IP).
4. **Speed:** Consensus reached via **Hydra L2** in milliseconds.
5. **Result:** Immutable **ThreatProof Capsule** minted on Cardano L1.

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Team](#team)
- [Contributing](#contributing)
- [License](#license)

## Problem Statement

Cardano's DeFi ecosystem is rapidly scaling, but it lacks real-time threat detection and trustless oracle infrastructure. Users and protocols rely on fragmented security tools, centralized data feeds, and manual verification—leading to millions lost in exploits, oracle manipulation, and scam transactions. Events like the 2024 DeFi hacks ($1.42B stolen) showed how fragile current systems are when threat intelligence, data verification, and consensus coordination fail simultaneously.

**Existing Systems vs. SON:**

- **Reactive threat detection** → Detects fraud in mempool before execution
- **Centralized oracle feeds** → Decentralized multi-agent oracle consensus
- **No cross-verification layer** → AI agents cross-verify evidence using ML anomaly detection
- **Isolated security tools** → Unified dashboard fuses threat data, oracle feeds, and agent votes
- **Manual fraud investigation** → Auto-publishes cryptographic ThreatProof Capsules on-chain

## Solution Overview

SON is a unified, decentralized AI-agent ecosystem delivering:

- **Real-Time Threat Detection:** Sentinel Agents monitor mempool, analyze contracts, and flag scams/rugpulls.
- **Decentralized Oracle Consensus:** Oracle Agents aggregate and verify real-world data with ML-driven anomaly detection.
- **Hydra-Accelerated Multi-Agent Consensus:** Agents collaborate off-chain for sub-second decisions.
- **Self-Sustaining Agent Economy:** Masumi powers micropayments, reputation, and slashing.
- **Immutable Truth Capsules:** ThreatProof and FeedProof NFTs on Cardano L1.

## Key Features

### AI-Powered Threat Detection

- Real-time mempool monitoring and contract analysis
- ML-based scam pattern recognition
- Wallet risk scoring and token safety audits

### Decentralized Multi-Source Oracle Feeds

- Cross-verified price feeds, weather data, and market indices
- Manipulation-resistant data aggregation
- Multi-chain oracle bridge support

### Hydra-Accelerated Agent Consensus

- Sub-second off-chain collaboration
- Multi-agent dispute resolution
- Fast finality for threat verification and data feeds

### Zero-Knowledge Privacy Layer

- ZK-proofs for sensitive compliance data
- Privacy-preserving attestations
- Regulatory compliance without exposing raw information

### Self-Improving Agent Economy

- Micropayment-based incentives via Masumi
- Reputation scoring and staking
- Automated slashing for malicious agents

### Instant User Integration

- Browser wallet plugins for real-time risk alerts
- dApp SDK for consuming verified feeds
- Live dashboards with Matrix-inspired UI

## Architecture

```text
User (Wallet/dApp) → Masumi Orchestrator → Multi-Agent Cluster → Hydra Consensus → Cardano L1 Capsule
                                      ↓
                               CrewAI Workflow
                                      ↓
                         Kodosumi Runtime Sandbox
```

### Detailed Workflow

1.  **Initiation**: A user submits a transaction CBOR or Policy ID via the **Sentinel Dashboard**.
2.  **Orchestration**: The **Masumi Orchestrator** receives the request and spins up a dedicated `SentinelAgent`.
3.  **Analysis**:
    *   **Sentinel Agent**: Decompiles the transaction, checks for known scam patterns (e.g., "deadbeef"), and validates against the `policy.json` registry.
    *   **Oracle Agent**: (Optional) Cross-references external data feeds for price or identity verification.
4.  **Consensus (The Hydra Layer)**:
    *   Instead of waiting for slow L1 block confirmations, agents submit their findings to a **Hydra Head**.
    *   The **Hydra Node** validates the transaction off-chain in milliseconds.
    *   If valid, it signs a "Verdict Certificate".
5.  **Finalization**:
    *   The verdict is returned to the frontend immediately via WebSockets.
    *   A **ThreatProof Capsule** (containing the verdict and agent signatures) is minted on Cardano L1 for immutable history.
    *   An **Audit Report** (PDF) is generated for the user.

### Why Hydra? ⚡

Hydra is the backbone of SON's real-time security capability. Without it, the system would be too slow to protect users from immediate threats.

*   **Sub-Second Latency**: Hydra allows our agents to reach consensus on a threat in <1 second, compared to 20+ seconds on L1. This "pre-block" finality is crucial for stopping malicious transactions *before* they are included in a block.
*   **Zero-Cost Consensus**: Agent-to-agent communication and voting happen off-chain, avoiding L1 gas fees for every internal decision. We only pay L1 fees when minting the final ThreatProof Capsule.
*   **Scalability**: The system can handle thousands of concurrent threat scans by spinning up parallel Hydra Heads, ensuring the network never gets clogged.

### Core Components

- **Frontend:** Next.js dashboard with real-time WebSocket updates
- **Backend:** FastAPI orchestrator managing agent workflows
- **Agents:** 5 specialized Python agents (Sentinel, Oracle, Compliance, ZK-Prover, Consensus)
- **Infrastructure:** Hydra Head for consensus, Midnight for ZK-proofs
- **Blockchain:** Cardano L1 for immutable capsule registry

### Agent Architecture (5-Agent Model)

1. **Sentinel Agent:** Detection & analysis
2. **Oracle Agent:** External data verification
3. **Compliance Agent:** Regulatory risk assessment
4. **ZK-Prover Agent:** Privacy-preserving proofs
5. **Consensus Agent:** Final decision & capsule writing

## Tech Stack

### Blockchain & Consensus

- **Cardano L1:** Plutus V2 smart contracts for capsule registry
- **Hydra L2:** Ultra-fast off-chain consensus
- **Midnight:** ZK-proof engine for privacy

### AI & Agents

- **CrewAI:** Multi-agent orchestration framework
- **PyTorch + HuggingFace:** ML models for anomaly detection
- **Python:** Agent logic with Blockfrost SDK

### Backend & Infrastructure

- **FastAPI:** Python orchestrator with async support
- **Node.js + Express:** Lightweight API services
- **Docker + Kubernetes:** Containerized agent runtimes
- **Redis/NATS:** Message bus for agent communication

### Frontend & UI

- **Next.js + React:** Dashboard with real-time updates
- **TailwindCSS + shadcn/ui:** Matrix-themed UI components
- **WebSockets:** Live log streaming and status updates

### Data & Storage

- **IPFS + Pinata:** Off-chain encrypted evidence storage
- **Pinecone/Milvus:** Vector database for agent memory
- **Blockfrost/Koios:** Cardano blockchain indexing

### Monitoring & DevOps

- **Prometheus + Grafana:** System health monitoring
- **GitHub Actions:** CI/CD pipelines
- **Lucid.js + CIP-30:** Wallet integration

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Cardano wallet (Nami, Eternl, or Lace)

### 1. Clone the Repository

```bash
git clone https://github.com/varunaditya27/sentinel-orchestrator-network.git
cd sentinel-orchestrator-network
```

### 2. Backend Setup (Orchestrator + Agents)

```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure API keys
uvicorn main:app --reload
# Runs on http://localhost:8000
```

### 3. Frontend Setup (Dashboard)

```bash
cd frontend
npm install
cp .env.local.example .env.local  # Configure backend URL
npm run dev
# Runs on http://localhost:3000
```

### 4. Infrastructure Setup (Hydra + Midnight)

```bash
# Hydra Node
cd hydra-node
docker-compose up -d

# Midnight Devnet (Optional)
cd ../midnight-devnet
docker build -t midnight-devnet .
docker run -d midnight-devnet
```

### 5. Test the System

1. Open http://localhost:3000
2. Enter a Cardano Policy ID
3. Watch the real-time agent swarm in action!

## API Documentation

### Core Endpoints

#### Initiate Scan
```http
POST /api/v1/scan
Authorization: Bearer son_hackathon_token_2025
Content-Type: application/json

{
  "schema_version": "1.0",
  "policy_id": "d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf0abb9efb1c650668",
  "mock_mode": false
}
```

**Response:**
```json
{
  "task_id": "task_8821_xc",
  "status": "processing",
  "estimated_time": 5
}
```

#### WebSocket Log Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/logs/task_8821_xc');
ws.onmessage = (event) => {
  const log = JSON.parse(event.data);
  console.log(log.message);
};
```

See `docs/api_schema.json` for complete API specifications.

## Team NexBlock

- **Harshita Nagesh** - Team Leader & Architect
- **Member 2** - AI Brain (Detection Logic)
- **Member 3** - Speed Demon (Hydra Infrastructure)
- **Member 4** - Ghost (Midnight & Privacy)
- **Member 5** - Face (Frontend & UX)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/TypeScript
- Write tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Cardano Foundation for the Hackathon Asia 2025
- Masumi team for the agent framework
- Hydra team for L2 consensus technology
- Midnight team for ZK-proof capabilities

---

**Built with ❤️ for Cardano's decentralized future**

