import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

BLOCKFROST_URL = os.getenv("BLOCKFROST_API_URL", "https://cardano-preprod.blockfrost.io/api")
BLOCKFROST_KEY = os.getenv("BLOCKFROST_API_KEY")

async def fetch_proposals():
    if not BLOCKFROST_KEY:
        print("Error: BLOCKFROST_API_KEY not found in .env")
        return

    headers = {"project_id": BLOCKFROST_KEY}
    
    print(f"Fetching proposals from {BLOCKFROST_URL}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BLOCKFROST_URL}/v0/governance/proposals?order=desc&count=1",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} {response.text}")
                return

            proposals = response.json()
            
            if proposals:
                print("RAW JSON of first item:")
                print(proposals[0])
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_proposals())
