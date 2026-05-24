"""
Claude AI Service

Handles integration with Anthropic's Claude API for generating paper summaries.

Key Concepts:
- API Client: Creates instances to communicate with Claude
- Prompt Engineering: Crafting good prompts for better responses
- Error Handling: Handle API failures gracefully
"""

from anthropic import Anthropic
from app.config import settings
from typing import Optional


class AIService:
    """Service for Claude AI operations"""
    
    def __init__(self):
        """Initialize Claude client with API key"""
        if not settings.CLAUDE_API_KEY:
            raise ValueError(
                "CLAUDE_API_KEY not set in environment. "
                "Set it in .env file or environment variables."
            )
        
        self.client = Anthropic(api_key=settings.CLAUDE_API_KEY)
    
    def generate_summary(
        self, 
        paper_title: str, 
        paper_content: str,
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Generate an AI summary of a research paper.
        
        Args:
            paper_title: Title of the paper
            paper_content: Full text extracted from PDF
            max_tokens: Maximum length of summary
            
        Returns:
            Summary string or None if API call fails
            
        Example:
            summary = ai_service.generate_summary(
                "Deep Learning Advances",
                "This paper discusses...",
                max_tokens=300
            )
        """
        try:
            # Truncate content if too long (Claude has context limits)
            # Typical limit: 100K tokens (~400K characters)
            # For safety, truncate to 50K characters
            max_chars = 50000
            truncated_content = paper_content[:max_chars]
            if len(paper_content) > max_chars:
                truncated_content += "\n[... truncated due to length ...]"
            
            # Create the prompt for Claude
            prompt = self._create_summary_prompt(paper_title, truncated_content)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Use latest Claude model
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract and return the text response
            return message.content[0].text
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
    
    @staticmethod
    def _create_summary_prompt(title: str, content: str) -> str:
        """
        Create a well-structured prompt for Claude.
        
        Prompt engineering tip: Be specific about what you want!
        Poor prompt: "Summarize this"
        Good prompt: "Provide a 3-paragraph summary focusing on key findings"
        """
        return f"""Please summarize the following research paper in a clear, concise manner.

Paper Title: {title}

Paper Content:
{content}

Please provide:
1. A one-sentence overview
2. Main contributions (2-3 key points)
3. Methodology used
4. Key findings or results
5. Potential impact or applications

Format your response as a structured summary."""
    
    def generate_title_from_content(self, content: str) -> Optional[str]:
        """
        Generate a title from paper content if title is missing.
        Useful as a fallback if title extraction fails.
        """
        try:
            truncated = content[:10000]  # Use first 10k chars
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"Based on this paper content, generate a concise title (max 10 words):\n\n{truncated}"
                    }
                ]
            )
            
            return message.content[0].text.strip()
        except Exception as e:
            print(f"Error generating title: {e}")
            return None


# Create global instance
# This will fail at import if CLAUDE_API_KEY is not set
try:
    ai_service = AIService()
except ValueError as e:
    # In development/testing, we might not have the key yet
    ai_service = None
    if settings.DEBUG:
        print(f"Warning: {e}")
