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
        Fetches the Fireflies AI-generated summary (overview, bullet highlights,
        action items) — NOT the raw word-for-word transcript.
        Returns a formatted string ready for display / light reformatting.
        """
        query = """
        query Transcript($id: String!) {
            transcript(id: $id) {
                id
                title
                dateString
                meeting_attendees {
                    displayName
                }
                summary {
                    action_items
                    overview
                    shorthand_bullet
                    bullet_gist
                    keywords
                }
            }
        }
        """
        variables = {"id": transcript_id}
        data = self._query(query, variables)

        if "data" in data and "transcript" in data["data"]:
            t = data["data"]["transcript"]
            return self._format_summary(t)

        return None

    def _format_summary(self, t):
        """
        Formats the Fireflies transcript object into a clean text block.
        Handles Fireflies returning summary fields as either strings or lists.
        """
        def to_str(val):
            """Convert a Fireflies field to a plain string regardless of type."""
            if not val:
                return ""
            if isinstance(val, list):
                return "\n".join(str(item).strip() for item in val if item)
            return str(val).strip()

        title = t.get("title", "Untitled Meeting")
        date = t.get("dateString", "")
        summary = t.get("summary") or {}
        attendees = t.get("meeting_attendees") or []

        lines = []
        lines.append(f"# {title}")
        if date:
            lines.append(f"**Date:** {date}")
        lines.append("")

        # Attendees
        if attendees:
            lines.append("## Attendees")
            for a in attendees:
                name = a.get("displayName", "Unknown")
                lines.append(f"- {name}")
            lines.append("")

        # Bullet highlights
        highlights = to_str(summary.get("shorthand_bullet") or summary.get("bullet_gist"))
        if highlights:
            lines.append("## Meeting Highlights")
            lines.append(highlights)
            lines.append("")

        # Keywords
        keywords = to_str(summary.get("keywords"))
        if keywords:
            lines.append("## Key Topics")
            lines.append(keywords)
            lines.append("")

        # Detailed overview / meeting notes
        overview = to_str(summary.get("overview"))
        if overview:
            lines.append("## Meeting Notes")
            lines.append(overview)
            lines.append("")

        # Action items
        action_items = to_str(summary.get("action_items"))
        if action_items:
            lines.append("## Action Items")
            lines.append(action_items)
            lines.append("")

        if len(lines) <= 4:
            lines.append("_Fireflies has not yet generated a summary for this meeting._")
            lines.append("_The AI summary is usually ready 10–15 minutes after the meeting ends._")

        return "\n".join(lines)


