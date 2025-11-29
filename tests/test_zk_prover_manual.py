import asyncio
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.zk_prover import MidnightProver

async def test_midnight_prover():
    print("Testing MidnightProver...")
    
    # Test Mock Mode
    prover = MidnightProver(mock_mode=True)
    evidence = {"tag": "TEST_TAG", "data": "some data"}
    proof = await prover.prove(evidence)
    print(f"Mock Proof: {proof}")
    assert proof == "PROOF_VERIFIED_BY_MIDNIGHT_MOCK::TEST_TAG"
    
    # Test Real Mode (Fallback)
    prover_real = MidnightProver(mock_mode=False)
    proof_real = await prover_real.prove(evidence)
    print(f"Real Proof (Fallback): {proof_real}")
    assert "PROOF_FALLBACK_MOCK" in proof_real
    
    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_midnight_prover())
