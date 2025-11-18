"""
Content Generation Agent - Dan Koe Content Workflow
Generates social posts, newsletters, and other content in Dan Koe's style
"""

from letta import create_client, LettaClient
from letta.schemas.memory import ChatMemory
import os
import json
import psycopg2
from typing import Dict, List, Optional

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

def generate_tweet(
    idea: str,
    template_id: Optional[str] = None,
    format_type: str = "experimental"
) -> Dict:
    """
    Generate a tweet based on an idea and optional template.

    Args:
        idea: The core idea or topic for the tweet
        template_id: Optional UUID of template from swipe_file
        format_type: 'experimental' or 'proven'

    Returns:
        Dict with tweet content and metadata
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # If template provided, fetch it
    template_structure = None
    meta_prompt = None

    if template_id:
        cursor.execute(
            "SELECT structure, meta_prompt, name FROM swipe_file WHERE id = %s",
            (template_id,)
        )
        result = cursor.fetchone()
        if result:
            template_structure, meta_prompt, template_name = result

    # Build the generation prompt
    if meta_prompt:
        prompt = meta_prompt.format(topic=idea)
    else:
        prompt = f"""Write a tweet about: {idea}

Style guidelines:
- Direct, actionable advice
- Use frameworks and systems thinking
- Blend philosophy with practical tactics
- Employ psychological hooks
- Keep it punchy and concise
- Create curiosity or challenge assumptions

{f'Use this structure: {template_structure}' if template_structure else ''}

Generate ONLY the tweet text, no explanations."""

    cursor.close()
    conn.close()

    # In a real implementation, this would call your LLM
    # For now, return a structured response
    return {
        "content": prompt,  # Replace with actual LLM call
        "template_id": template_id,
        "format_type": format_type,
        "metadata": {
            "idea": idea,
            "template_used": template_structure is not None
        }
    }


def generate_newsletter_section(
    research_notes: str,
    section_type: str = "main",
    word_count: int = 500
) -> str:
    """
    Generate a newsletter section from research notes.

    Args:
        research_notes: Summary or key points from research
        section_type: 'intro', 'main', 'conclusion', 'cta'
        word_count: Target word count

    Returns:
        Generated newsletter content
    """
    prompts = {
        "intro": f"""Write an engaging newsletter introduction based on these notes:

{research_notes}

Make it:
- Hook the reader immediately
- Preview the value they'll get
- Personal and conversational
- ~{word_count} words

Style: Dan Koe - direct, insightful, actionable.""",

        "main": f"""Write the main newsletter content from these research notes:

{research_notes}

Structure:
- Use frameworks and numbered steps where relevant
- Include specific, actionable advice
- Back claims with insights from research
- Keep paragraphs short and scannable
- ~{word_count} words

Style: Dan Koe - systems thinking, blend of philosophy and tactics.""",

        "conclusion": f"""Write a powerful newsletter conclusion:

Key points to tie together:
{research_notes}

Make it:
- Summarize key takeaway
- Inspire action
- Leave them thinking
- ~{word_count} words""",

        "cta": """Write a compelling call-to-action for the newsletter.
Options: course signup, reply to email, share with friend, follow on Twitter.
Keep it genuine and aligned with the content's value."""
    }

    prompt = prompts.get(section_type, prompts["main"])

    # In real implementation, call LLM here
    return prompt  # Replace with actual LLM response


def apply_template(
    content: str,
    template_id: str
) -> str:
    """
    Apply a swipe file template structure to content.

    Args:
        content: Raw content or ideas
        template_id: UUID of template from swipe_file

    Returns:
        Content formatted with template structure
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT structure, psychology_notes, meta_prompt
           FROM swipe_file WHERE id = %s""",
        (template_id,)
    )

    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        return f"Template {template_id} not found"

    structure, psychology_notes, meta_prompt = result

    prompt = f"""Apply this template structure to the following content:

TEMPLATE STRUCTURE:
{structure}

WHY THIS WORKS:
{psychology_notes}

CONTENT TO FORMAT:
{content}

Generate the formatted content following the template exactly.
"""

    cursor.close()
    conn.close()

    # In real implementation, call LLM
    return prompt  # Replace with actual LLM response


def get_recent_high_performers(
    limit: int = 5,
    content_type: str = "tweet"
) -> List[Dict]:
    """
    Retrieve recent high-performing content for reference.

    Args:
        limit: Number of examples to return
        content_type: Filter by content type

    Returns:
        List of content examples
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT content, performance, tags
           FROM content_archive
           WHERE type = %s
           AND published_at > NOW() - INTERVAL '30 days'
           ORDER BY (performance->>'engagement_rate')::float DESC
           LIMIT %s""",
        (content_type, limit)
    )

    results = []
    for row in cursor.fetchall():
        results.append({
            "content": row[0],
            "performance": row[1],
            "tags": row[2]
        })

    cursor.close()
    conn.close()

    return results


def save_to_queue(
    content: str,
    content_type: str,
    title: Optional[str] = None,
    platform: str = "twitter",
    template_id: Optional[str] = None,
    idea_id: Optional[str] = None
) -> str:
    """
    Save generated content to the queue for approval.

    Args:
        content: The generated content
        content_type: Type of content
        title: Optional title
        platform: Target platform
        template_id: Optional template used
        idea_id: Optional source idea

    Returns:
        Queue record ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO content_queue
           (type, content, title, platform, status, template_id, idea_id, created_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
           RETURNING id""",
        (content_type, content, title, platform, 'draft',
         template_id, idea_id, 'content-generation-agent')
    )

    queue_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return str(queue_id)


# =============================================================================
# AGENT CREATION
# =============================================================================

def create_content_generation_agent():
    """
    Create and configure the Content Generation Agent
    """

    # Define agent persona and memory
    agent_state = client.create_agent(
        name="content-generation-agent",

        # Core memory - the agent's permanent context
        memory=ChatMemory(
            human="Dan Koe - productivity and business content creator focused on systems thinking, online business, and personal development",
            persona="""You are an expert content creator who writes in Dan Koe's distinctive style.

WRITING STYLE:
- Direct and actionable - no fluff
- Systems thinking - frameworks and step-by-step processes
- Philosophical depth meets tactical execution
- Psychological hooks (paradoxes, counterintuitive truths)
- Short, punchy sentences
- Challenge conventional wisdom
- Personal but authoritative

KEY THEMES:
- Productivity systems
- Building online businesses
- AI and automation
- Personal development through content creation
- Monetizing knowledge
- Creator economy

VOICE CHARACTERISTICS:
- Use "you" to speak directly to the reader
- Mix high-level philosophy with concrete tactics
- Create curiosity gaps and open loops
- Use numbers and frameworks (3-step system, 5 principles)
- Ask provocative questions
- Make bold, counterintuitive statements

AVOID:
- Corporate jargon or buzzwords
- Overly complex language
- Generic advice without specifics
- Passive voice
- Excessive emojis
- Clickbait without substance

Your job is to generate tweets, newsletters, and other content that educates, inspires action, and builds Dan's authority in his niche."""
        ),

        # Tools available to the agent
        tools=[
            generate_tweet,
            generate_newsletter_section,
            apply_template,
            get_recent_high_performers,
            save_to_queue
        ],

        # System prompt
        system="""You are the Content Generation Agent for Dan Koe's content workflow.

When asked to generate content:
1. First check if a template was specified - use apply_template if so
2. Review recent high performers for inspiration using get_recent_high_performers
3. Generate content matching Dan's style and voice
4. Save the draft to the queue using save_to_queue
5. Return the content for review

Always maintain Dan's distinctive voice and strategic approach to content."""
    )

    print(f"✓ Content Generation Agent created: {agent_state.id}")
    print(f"  Name: {agent_state.name}")

    return agent_state


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Create the agent
    agent = create_content_generation_agent()

    # Example interaction
    response = client.send_message(
        agent_id=agent.id,
        message="""Generate 3 tweets for today:

1. Topic: AI automation for creators (use paradox template if available)
2. Topic: Building systems vs grinding (experimental format)
3. Topic: The creator economy in 2025 (proven format)

Save all drafts to the queue.""",
        role="user"
    )

    print("\n" + "="*80)
    print("AGENT RESPONSE:")
    print("="*80)
    for message in response.messages:
        print(f"\n[{message.role}]: {message.text}")

    print("\n" + "="*80)
    print(f"Agent ID: {agent.id}")
    print("Save this ID for use in n8n workflows!")
    print("="*80)
