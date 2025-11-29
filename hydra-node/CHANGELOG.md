# Changelog

All notable changes to the Hydra Settlement Layer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-29 - Member4 Release

### Added
- **Complete Hydra settlement layer** - Standalone implementation with no external dependencies
- **CBOR metadata generation** - ForkShield L1 Capsule NFT structure with policy ID 674
- **ED25519 signature verification** - PyNaCl-based cryptographic validation
- **Agent signature aggregation** - Sentinel, Oracle, and Midnight agent signatures
- **Idempotency key computation** - SHA256 hash-based deterministic keys
- **CLI interface** - All required commands: --open, --commit, --attach-proof, --finalize, --cbor-only
- **REST API server** - HTTP endpoints for integration
- **State persistence** - JSON-based local storage in ./state/
- **Docker containerization** - Complete deployment setup
- **Comprehensive testing** - Unit tests and acceptance tests
- **CI/CD pipeline** - GitHub Actions workflow
- **Security measures** - Private key protection and gitignore rules
- **Documentation** - Complete setup and integration guides

### Features
- **Offline operation** - No Cardano node or Hydra devnet required
- **Deterministic results** - Same inputs produce same outputs
- **Demo mode** - --skip-sig-check flag for testing
- **Event-driven architecture** - Structured JSON events with timestamps
- **Production ready** - Architecturally prepared for real Hydra integration

### Technical Details
- Python 3.10+ with type hints
- Dependencies: requests, cbor2, PyNaCl, flask, python-dateutil
- CBOR structure: CIP-25 NFT metadata with ForkShield capsule
- Signature format: base64-encoded ED25519 signatures
- State format: JSON files with session and order metadata

### Security
- Private keys moved to separate ignored file
- Git hooks prevent committing sensitive data
- CI checks for private key leaks
- Production warnings for demo flags

### Testing
- Unit tests for core functionality
- Integration tests for settlement flow
- Docker build verification
- State persistence validation
- Acceptance test automation

### Documentation
- Complete README with setup instructions
- API endpoint documentation
- Integration guide for teammates
- Security and production notes
- Troubleshooting section
