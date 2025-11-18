"""
Research & Synthesis Agent - Dan Koe Content Workflow
Processes long-form content (videos, articles, books) into actionable summaries
"""

from letta import create_client, LettaClient
from letta.schemas.memory import ChatMemory
import os
import json
import psycopg2
from typing import Dict, List, Optional
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Initialize Letta client
client: LettaClient = create_client()

# Database connection
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "content_workflow"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}


def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(**DB_CONFIG)


# =============================================================================
# AGENT TOOLS
# =============================================================================

def extract_youtube_transcript(video_url: str) -> Dict:
    """
    Extract transcript from a YouTube video.

    Args:
        video_url: YouTube video URL

    Returns:
        Dict with video info and transcript
    """
    try:
        # Parse video ID from URL
        parsed_url = urlparse(video_url)
        if parsed_url.hostname == 'youtu.be':
            video_id = parsed_url.path[1:]
        else:
            video_id = parse_qs(parsed_url.query)['v'][0]

        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine transcript
        full_transcript = " ".join([entry['text'] for entry in transcript_list])

        # Get video metadata (would use YouTube API in production)
        return {
            "video_id": video_id,
            "url": video_url,
            "transcript": full_transcript,
            "duration_seconds": transcript_list[-1]['start'] if transcript_list else 0,
            "success": True
        }

    except Exception as e:
        return {
            "url": video_url,
            "error": str(e),
            "success": False
        }


def summarize_research_content(
    content: str,
    source_type: str,
    focus_areas: Optional[List[str]] = None,
    target_length: int = 1000
) -> str:
    """
    Generate a summary of research content.

    Args:
        content: Full text to summarize
        source_type: Type of source (youtube, article, book, etc.)
        focus_areas: Specific areas to focus on
        target_length: Target word count for summary

    Returns:
        Comprehensive summary
    """
    focus_instruction = ""
    if focus_areas:
        focus_instruction = f"\nFocus specifically on: {', '.join(focus_areas)}"

    prompt = f"""Summarize this {source_type} content into an actionable brief (~{target_length} words).

CONTENT:
{content[:10000]}  # Limit for context window

INSTRUCTIONS:
- Extract key frameworks, systems, and actionable insights
- Identify counterintuitive or surprising findings
- Highlight practical tactics Dan can apply
- Note any psychological principles or mental models
- Structure as: Main Idea → Key Points → Actionable Takeaways{focus_instruction}

Style: Concise, bullet-friendly, focused on utility."""

    # In real implementation, call LLM (Claude with long context window)
    # For now, return the prompt
    return prompt  # Replace with actual LLM call


def compare_with_archive(
    new_content: str,
    topic: str
) -> Dict:
    """
    Compare new research content with existing knowledge base.

    Args:
        new_content: New research summary
        topic: Topic to compare against

    Returns:
        Dict with comparison insights
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get related past research
    cursor.execute(
        """SELECT title, summary, key_insights
           FROM research_notes
           WHERE %s = ANY(related_topics) OR summary ILIKE '%%' || %s || '%%'
           ORDER BY created_at DESC
           LIMIT 5""",
        ([topic], topic)
    )

    past_research = []
    for row in cursor.fetchall():
        past_research.append({
            "title": row[0],
            "summary": row[1],
            "key_insights": row[2]
        })

    cursor.close()
    conn.close()

    # Build comparison prompt
    prompt = f"""Compare this new research with Dan's existing knowledge:

NEW RESEARCH:
{new_content}

EXISTING KNOWLEDGE:
{json.dumps(past_research, indent=2)}

ANALYSIS NEEDED:
1. What's genuinely new or different?
2. What confirms existing knowledge?
3. Any contradictions or alternative perspectives?
4. How does this expand or refine understanding?
5. Novel angles or applications?

Provide a comparison summary focusing on what's uniquely valuable."""

    # In real implementation, call LLM
    comparison_result = prompt  # Replace with LLM call

    return {
        "new_content": new_content,
        "related_past_research_count": len(past_research),
        "comparison": comparison_result
    }


def extract_key_insights(content: str, count: int = 5) -> List[str]:
    """
    Extract the most important insights from content.

    Args:
        content: Text to analyze
        count: Number of insights to extract

    Returns:
        List of key insights
    """
    prompt = f"""Extract the {count} most important, actionable insights from this content:

{content}

For each insight:
- Make it specific and actionable
- Focus on what Dan can apply to his work
- Prioritize counterintuitive or unique ideas
- Keep each insight to 1-2 sentences

Format as a JSON array of strings."""

    # In real implementation, call LLM and parse JSON
    # For now, return sample structure
    return [
        "Insight 1 placeholder",
        "Insight 2 placeholder",
        "Insight 3 placeholder"
    ]  # Replace with actual LLM call


def extract_quotes(content: str, count: int = 3) -> List[Dict]:
    """
    Extract notable quotes from content.

    Args:
        content: Text to analyze
        count: Number of quotes to extract

    Returns:
        List of quote dicts with context
    """
    prompt = f"""Extract {count} of the most impactful, quotable statements from this content:

{content}

Criteria for quotes:
- Memorable and shareable
- Encapsulates a key idea
- Could work standalone in social media
- Thought-provoking or counterintuitive

Return as JSON array with: [{{"quote": "...", "context": "why this matters"}}]"""

    # In real implementation, call LLM and parse JSON
    return [
        {"quote": "Sample quote 1", "context": "Why it matters"},
        {"quote": "Sample quote 2", "context": "Why it matters"}
    ]  # Replace with actual LLM call


def save_research_note(
    title: str,
    source_type: str,
    source_url: str,
    original_content: str,
    summary: str,
    key_insights: List[str],
    quotes: List[Dict],
    related_topics: List[str],
    comparison_notes: Optional[str] = None
) -> str:
    """
    Save research note to database.

    Args:
        title: Research note title
        source_type: Type of source
        source_url: URL to source
        original_content: Full transcript/text
        summary: AI-generated summary
        key_insights: List of key takeaways
        quotes: List of notable quotes
        related_topics: Topic tags
        comparison_notes: Comparison with existing knowledge

    Returns:
        Research note ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO research_notes
           (title, source_type, source_url, original_content, summary,
            key_insights, quotes, related_topics, comparison_notes)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
           RETURNING id""",
        (title, source_type, source_url, original_content, summary,
         json.dumps(key_insights), json.dumps(quotes),
         json.dumps(related_topics), comparison_notes)
    )

    note_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return str(note_id)


def get_research_for_topic(topic: str, limit: int = 5) -> List[Dict]:
    """
    Retrieve research notes related to a topic.

    Args:
        topic: Topic to search for
        limit: Max results to return

    Returns:
        List of research note summaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, title, summary, key_insights, source_url, created_at
           FROM research_notes
           WHERE %s = ANY(related_topics)
           OR summary ILIKE '%%' || %s || '%%'
           OR title ILIKE '%%' || %s || '%%'
           ORDER BY created_at DESC
           LIMIT %s""",
        ([topic], topic, topic, limit)
    )

    notes = []
    for row in cursor.fetchall():
        notes.append({
            "id": str(row[0]),
            "title": row[1],
            "summary": row[2],
            "key_insights": row[3],
            "source_url": row[4],
            "created_at": row[5].isoformat() if row[5] else None
        })

    cursor.close()
    conn.close()

    return notes


def generate_actionable_items(summary: str) -> List[str]:
    """
    Generate actionable items from research summary.

    Args:
        summary: Research summary text

    Returns:
        List of actionable next steps
    """
    prompt = f"""From this research summary, generate 3-5 actionable items Dan can do:

{summary}

For each action:
- Be specific and concrete
- Focus on content creation, business, or personal development
- Make it something implementable
- Consider how it applies to Dan's creator business

Format as a JSON array of action strings."""

    # In real implementation, call LLM
    return [
        "Action 1 placeholder",
        "Action 2 placeholder",
        "Action 3 placeholder"
    ]  # Replace with actual LLM call


# =============================================================================
# AGENT CREATION
# =============================================================================

def create_research_synthesis_agent():
    """
    Create and configure the Research & Synthesis Agent
    """

    agent_state = client.create_agent(
        name="research-synthesis-agent",

        memory=ChatMemory(
            human="Dan Koe - content creator who consumes lots of educational content for research",
            persona="""You are the Research & Synthesis Agent for Dan Koe.

YOUR ROLE:
Transform hours of videos, articles, and books into concise, actionable summaries that Dan can use for content creation.

KEY CAPABILITIES:
1. Extract transcripts from YouTube videos
2. Summarize long-form content (6+ hours → 1000 words)
3. Identify key frameworks, systems, and actionable insights
4. Compare new information with Dan's existing knowledge base
5. Extract quotable statements and key insights
6. Generate actionable next steps

RESEARCH FOCUS:
When processing content, prioritize:
- **Frameworks & Systems**: Numbered processes, mental models
- **Counterintuitive Ideas**: Things that challenge common wisdom
- **Practical Tactics**: Specific, implementable actions
- **Psychological Principles**: Why things work, human behavior
- **Novel Angles**: Unique perspectives on familiar topics

SYNTHESIS APPROACH:
- Don't just summarize - synthesize into actionable intelligence
- Compare new info with existing knowledge (what's new?)
- Structure output for easy content repurposing
- Focus on utility over completeness
- Extract the 20% that provides 80% of value

OUTPUT STYLE:
- Concise, scannable bullet points
- Framework-oriented (3-step process, 5 principles, etc.)
- Emphasize what's actionable
- Highlight quotable statements
- Note content opportunities (tweet ideas, newsletter angles)

You work with:
- Content Strategist (provides topics to research)
- Content Generation Agent (uses your summaries for content)

Your goal: Turn research time from hours to minutes while maintaining insight quality."""
        ),

        tools=[
            extract_youtube_transcript,
            summarize_research_content,
            compare_with_archive,
            extract_key_insights,
            extract_quotes,
            save_research_note,
            get_research_for_topic,
            generate_actionable_items
        ],

        system="""You are the Research & Synthesis Agent.

When given a research source (YouTube video, article, etc.):
1. Extract the content using extract_youtube_transcript or appropriate tool
2. Generate a summary using summarize_research_content
3. Compare with existing knowledge using compare_with_archive
4. Extract key insights using extract_key_insights
5. Pull notable quotes using extract_quotes
6. Generate actionable items using generate_actionable_items
7. Save everything using save_research_note
8. Return a structured research brief

When asked for research on a topic:
1. Use get_research_for_topic to find relevant past research
2. Synthesize findings across multiple sources
3. Highlight what's most relevant

Always focus on actionability and content application."""
    )

    print(f"✓ Research & Synthesis Agent created: {agent_state.id}")
    print(f"  Name: {agent_state.name}")

    return agent_state


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Create the agent
    agent = create_research_synthesis_agent()

    # Example interaction
    response = client.send_message(
        agent_id=agent.id,
        message="""Process this research source:

YouTube Video: https://www.youtube.com/watch?v=example
Topic: Productivity Systems
Focus on: Systems thinking, frameworks, actionable tactics

Provide:
1. 1000-word actionable summary
2. Top 5 key insights
3. Notable quotes for social media
4. Actionable items for Dan
5. Content ideas this could inspire""",
        role="user"
    )

    print("\n" + "="*80)
    print("AGENT RESPONSE:")
    print("="*80)
    for message in response.messages:
        print(f"\n[{message.role}]: {message.text}")

    print("\n" + "="*80)
    print(f"Agent ID: {agent.id}")
    print("Use this in n8n workflows for research processing!")
    print("="*80)
