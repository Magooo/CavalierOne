from utils.fireflies_client import FirefliesClient
import json

def test_fireflies():
    print("Testing Fireflies Client...")
    client = FirefliesClient()
    
    if not client.api_key:
        print("SKIPPING: No Fireflies API Key configured.")
        return

    print("Fetching recent meetings...")
    meetings = client.get_recent_meetings(limit=2)
    print(f"Found {len(meetings)} meetings.")
    
    for m in meetings:
        print(f"- {m['title']} ({m['dateString']})")
        print(f"  ID: {m['id']}")
        
        # Test Transcript Fetch
        print("  Fetching transcript text...")
        text = client.get_transcript_text(m['id'])
        if text:
            print(f"  Transcript Length: {len(text)} chars")
            print(f"  Preview: {text[:100]}...")
        else:
            print("  No transcript text found.")
            
if __name__ == "__main__":
    test_fireflies()
