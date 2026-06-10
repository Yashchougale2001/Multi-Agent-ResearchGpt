import asyncio
import httpx

async def test_research_flow():
    base_url = "http://localhost:8000"
    
    # Start research
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/research",
            json={"query": "What are the latest developments in quantum computing?"}
        )
        print("Start Research Response:", response.json())
        
        session_id = response.json()["session_id"]
        
        # Wait for completion (in practice, use WebSocket)
        await asyncio.sleep(30)
        
        # Get result
        result = await client.get(f"{base_url}/api/research/{session_id}")
        print("Result:", result.json())

if __name__ == "__main__":
    asyncio.run(test_research_flow())