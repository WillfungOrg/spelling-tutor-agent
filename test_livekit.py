import asyncio
from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    url = os.getenv('LIVEKIT_URL')
    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')
    
    print(f"Testing connection to: {url}")
    
    try:
        lkapi = api.LiveKitAPI(url, api_key, api_secret)
        # Create proper list request
        list_request = api.ListRoomsRequest()
        rooms = await lkapi.room.list_rooms(list_request)
        print(f"✅ Connected successfully! Found {len(rooms.rooms)} rooms")
        
        # Clean up
        await lkapi.aclose()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

asyncio.run(test_connection())
