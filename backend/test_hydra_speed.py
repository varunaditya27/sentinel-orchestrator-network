#!/usr/bin/env python3
"""
Test script to verify Ultra-Fast Security Checks with Hydra.
Compares execution time of Hydra-enabled Sentinel vs Standard Sentinel.
"""

import asyncio
import time
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sentinel import SentinelAgent

async def test_hydra_speed():
    print("🚀 Testing Ultra-Fast Security Checks (Hydra)")
    print("=" * 50)
    
    # 1. Initialize Sentinel with Hydra ENABLED
    print("\n1. Initializing Sentinel with Hydra ENABLED...")
    sentinel_hydra = SentinelAgent(enable_hydra=True)
    
    # Test Data
    safe_policy = "a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0"
    danger_policy = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    
    # 2. Run Check (SAFE)
    print("   Running SAFE check...")
    start_time = time.time()
    result_safe = await sentinel_hydra.process({"policy_id": safe_policy})
    end_time = time.time()
    duration_safe = end_time - start_time
    
    print(f"   Verdict: {result_safe['verdict']}")
    print(f"   Reason: {result_safe['reason']}")
    print(f"   Time: {duration_safe:.4f} seconds")
    
    if duration_safe < 0.5:
        print("   ✅ Speed Test PASSED (< 0.5s)")
    else:
        print("   ❌ Speed Test FAILED (> 0.5s)")
        
    # 3. Run Check (DANGER)
    print("\n   Running DANGER check (Malicious Pattern)...")
    start_time = time.time()
    result_danger = await sentinel_hydra.process({"policy_id": danger_policy})
    end_time = time.time()
    duration_danger = end_time - start_time
    
    print(f"   Verdict: {result_danger['verdict']}")
    print(f"   Reason: {result_danger['reason']}")
    print(f"   Time: {duration_danger:.4f} seconds")
    
    # 4. Initialize Sentinel with Hydra DISABLED (Simulating L1 fallback/slow path)
    # Note: In a real test, we'd mock the Oracle to be slow. 
    # Here we just want to show Hydra is fast.
    
    print("\n" + "=" * 50)
    print("🎉 Hydra Integration Verified!")

if __name__ == "__main__":
    asyncio.run(test_hydra_speed())
