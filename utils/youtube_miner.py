import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_channel_videos(channel_id, limit=5):
    """
    Fetches the latest videos from a YouTube channel.
    Args:
        channel_id (str): The YouTube Channel ID (e.g., UC...)
        limit (int): Number of videos to retrieve.
    Returns:
        list: List of dicts with video_id and title (title might be missing depending on scrapetube).
    """
    print(f"Fetching videos for channel: {channel_id}")
    videos = []
    try:
        # Get videos using scrapetube
        video_generator = scrapetube.get_channel(channel_id)
        
        count = 0
        for video in video_generator:
            if count >= limit:
                break
            
            video_data = {
                'video_id': video['videoId'],
                'title': video.get('title', {}).get('runs', [{}])[0].get('text', 'Unknown Title'),
                'url': f"https://www.youtube.com/watch?v={video['videoId']}"
            }
            videos.append(video_data)
            count += 1
            
    except Exception as e:
        print(f"Error fetching channel videos: {e}")
        
    return videos

def get_video_transcript(video_id):
    """
    Retrieves the transcript for a given video ID.
    Returns:
        str: The full transcript text, or None if not available.
    """
    try:
        # 2026-01-21: Environment uses non-standard API requiring instantiation
        api = YouTubeTranscriptApi()
        transcript_obj = api.fetch(video_id)
        
        # Manually extract text from Snippets since formatter might not match
        # Object structure seen in debug: FetchedTranscript(snippets=[FetchedTranscriptSnippet(text="...")])
        full_text = " ".join([s.text for s in transcript_obj.snippets])
        return full_text

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"Could not get transcript for {video_id}: {e}")
        return error_msg
