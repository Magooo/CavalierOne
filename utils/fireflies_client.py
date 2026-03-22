import requests
from config import Config

class FirefliesClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.FIREFLIES_API_KEY
        self.url = Config.FIREFLIES_GRAPHQL_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _query(self, query, variables=None):
        if not self.api_key:
            return {"error": "Fireflies API Key not configured"}
            
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_recent_meetings(self, limit=5):
        query = """
        query Transcripts($limit: Int) {
            transcripts(limit: $limit) {
                id
                title
                dateString
                duration
                privacy
            }
        }
        """
        variables = {"limit": limit}
        data = self._query(query, variables)
        
        if "data" in data and "transcripts" in data["data"]:
            return data["data"]["transcripts"]
        return []

    def get_transcript_text(self, transcript_id):
        """
        Fetches the full transcript sentences and joins them into a single blob 
        formatted with speaker names.
        """
        query = """
        query Transcript($id: String!) {
            transcript(id: $id) {
                id
                title
                sentences {
                    speaker_name
                    text
                }
            }
        }
        """
        variables = {"id": transcript_id}
        data = self._query(query, variables)
        
        if "data" in data and "transcript" in data["data"]:
            t = data["data"]["transcript"]
            sentences = t.get("sentences", [])
            
            # Format: "Speaker: Text..."
            full_text = f"Meeting Title: {t['title']}\n\n"
            for s in sentences:
                name = s.get('speaker_name', 'Unknown')
                text = s.get('text', '')
                full_text += f"{name}: {text}\n"
            
            return full_text
        return None
