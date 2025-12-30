"""JIRA API service for fetching and analyzing tickets."""

import os
import base64
from typing import Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


class JiraService:
    """Service for interacting with JIRA API."""

    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL", "")
        email = os.getenv("JIRA_EMAIL", "")
        api_token = os.getenv("JIRA_API_TOKEN", "")

        if not all([self.base_url, email, api_token]):
            raise ValueError(
                "JIRA configuration missing. Set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN"
            )

        # Create base64 encoded auth
        auth_string = f"{email}:{api_token}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()

        self.headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def fetch_ticket(self, ticket_id: str) -> dict[str, Any]:
        """Fetch a single JIRA ticket by ID or key."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/issue/{ticket_id}",
                    headers=self.headers,
                    params={"expand": "renderedFields"},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_msg = e.response.json().get("errorMessages", [])
                raise ValueError(f"Failed to fetch ticket {ticket_id}: {error_msg}")
            except Exception as e:
                raise ValueError(f"Error fetching ticket: {str(e)}")

    async def search_tickets(self, jql: str, max_results: int = 10) -> dict[str, Any]:
        """Search JIRA tickets using JQL."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/search",
                    headers=self.headers,
                    params={
                        "jql": jql,
                        "maxResults": max_results,
                        "fields": "summary,status,issuetype,priority,assignee,created",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                raise ValueError(f"Failed to search tickets: {str(e)}")

    async def get_ticket_comments(self, ticket_id: str) -> list[dict[str, Any]]:
        """Get comments for a ticket."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/issue/{ticket_id}/comment",
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("comments", [])
            except Exception as e:
                raise ValueError(f"Failed to fetch comments: {str(e)}")

    async def get_ticket_with_discussions(self, ticket_id: str) -> dict[str, Any]:
        """Fetch a ticket along with its discussions/comments."""
        # Fetch the main ticket
        ticket = await self.fetch_ticket(ticket_id)
        
        # Fetch comments/discussions
        try:
            comments = await self.get_ticket_comments(ticket_id)
            ticket["discussions"] = comments
            ticket["discussion_summary"] = self._summarize_discussions(comments)
        except Exception as e:
            # If fetching comments fails, continue with empty discussions
            ticket["discussions"] = []
            ticket["discussion_summary"] = ""
            
        return ticket
    
    def _summarize_discussions(self, comments: list[dict[str, Any]]) -> str:
        """Extract and summarize key information from discussions."""
        if not comments:
            return ""
        
        discussion_points = []
        for comment in comments:
            body = comment.get("body", "")
            author = comment.get("author", {}).get("displayName", "Unknown")
            
            # Handle JIRA's Atlassian Document Format (ADF)
            if isinstance(body, dict):
                text = self._extract_text_from_adf(body)
            else:
                text = str(body)
            
            if text.strip():
                discussion_points.append(f"{author}: {text.strip()}")
        
        return "\n\n".join(discussion_points)
    
    def _extract_text_from_adf(self, adf_content: dict) -> str:
        """Extract text from JIRA's Atlassian Document Format."""
        text_parts = []
        
        def extract_from_node(node: dict):
            if isinstance(node, dict):
                # Check if node has text
                if "text" in node:
                    text_parts.append(node["text"])
                
                # Process content array
                if "content" in node and isinstance(node["content"], list):
                    for child in node["content"]:
                        extract_from_node(child)
        
        extract_from_node(adf_content)
        return " ".join(text_parts)

    def extract_acceptance_criteria(self, description: str) -> list[str]:
        """Extract acceptance criteria from ticket description."""
        import re

        criteria = []

        # Patterns for acceptance criteria
        patterns = [
            r"acceptance criteria:?\s*([\s\S]*?)(?=\n\n|$)",
            r"^AC:?\s*([\s\S]*?)(?=\n\n|$)",
            r"^given[:\s]+(.*?)$",
            r"^when[:\s]+(.*?)$",
            r"^then[:\s]+(.*?)$",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                text = match.group(1) if match.lastindex else match.group(0)
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                criteria.extend(lines)

        return list(set(criteria))  # Remove duplicates
