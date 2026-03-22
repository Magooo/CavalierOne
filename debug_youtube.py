import sys

def log(msg):
    with open("debug_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

from utils.youtube_miner import get_channel_videos, get_video_transcript

CHANNEL_ID = "UCmpf1h1Nfua7AeH5W77AsQw"

# Clear log
with open("debug_log.txt", "w", encoding="utf-8") as f:
    f.write(f"Testing Miner for Channel ID: {CHANNEL_ID}\n")

# 1. Test Video Fetching
log("\n--- 1. Fetching Videos ---")
videos = get_channel_videos(CHANNEL_ID, limit=3)

if not videos:
    log("❌ No videos found. Scrapetube might be failing or ID is invalid.")
else:
    log(f"✅ Found {len(videos)} videos.")
    for v in videos:
        log(f"   - [{v['video_id']}] {v['title']}")

# 2. Test Transcript Fetching
log("\n--- 2. Fetching Transcripts ---")

try:
    import youtube_transcript_api
    from youtube_transcript_api import YouTubeTranscriptApi
    log(f"Module file: {youtube_transcript_api.__file__}")
    log(f"Class attributes: {dir(YouTubeTranscriptApi)}")
    log(f"Type of .list: {type(YouTubeTranscriptApi.list)}")
    log(f"Type of .fetch: {type(YouTubeTranscriptApi.fetch)}")
except ImportError:
    log("Could not import youtube_transcript_api.")

for v in videos:
    log(f"Attempting transcript for: {v['video_id']}")
    
    # Try Instantiation
    try:
        log("   Instantiating and calling .list()...")
        api = YouTubeTranscriptApi()
        t_list = api.list(v['video_id'])
        log(f"   Instance .list() result: {t_list}")
        
        log("   Instantiating and calling .fetch()...")
        t_fetch = api.fetch(v['video_id'])
        log(f"   Instance .fetch() result: {t_fetch}")
    except Exception as e:
        log(f"   Instance call failed: {e}")
