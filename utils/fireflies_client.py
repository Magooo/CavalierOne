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
        import re

        def to_bullet_list(val):
            """
            Convert a Fireflies field to a markdown bullet list.
            Handles lists, and also detects concatenated strings where each
            topic starts with an emoji — splits them into separate bullets.
            """
            if not val:
                return ""
            if isinstance(val, list):
                return "\n".join(f"- {str(item).strip()}" for item in val if item)
            text = str(val).strip()
            # Fireflies often returns highlights as one long string like:
            # "📊 **Topic A** text. 🤝 **Topic B** text."
            # Split at sentence-end followed by whitespace + emoji
            parts = re.split(r'(?<=[.!?])\s+(?=\S*[\U0001F100-\U0001FFFF])', text)
            if len(parts) > 1:
                return "\n".join(f"- {p.strip()}" for p in parts if p.strip())
            # Might also be newline-separated already
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if len(lines) > 1:
                return "\n".join(f"- {l}" if not l.startswith("-") else l for l in lines)
            return text  # single block — return as-is

        def to_str(val):
            """Plain string conversion for non-list fields like overview."""
            if not val:
                return ""
            if isinstance(val, list):
                return "\n\n".join(str(item).strip() for item in val if item)
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

        # Bullet highlights — split into individual bullets by emoji boundary
        highlights = to_bullet_list(summary.get("shorthand_bullet") or summary.get("bullet_gist"))
        if highlights:
            lines.append("## Meeting Highlights")
            lines.append(highlights)
            lines.append("")

        # Keywords — format as bullet list
        keywords = to_bullet_list(summary.get("keywords"))
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

        # Action items — format as bullet list
        action_items = to_bullet_list(summary.get("action_items"))
        if action_items:
            lines.append("## Action Items")
            lines.append(action_items)
            lines.append("")


        if len(lines) <= 4:
            lines.append("_Fireflies has not yet generated a summary for this meeting._")
            lines.append("_The AI summary is usually ready 10–15 minutes after the meeting ends._")

        return "\n".join(lines)


