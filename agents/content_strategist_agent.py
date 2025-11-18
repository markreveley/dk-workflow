"""
Content Strategist Agent - Dan Koe Content Workflow
Manages ideation, validation, and strategic content recommendations
"""

from letta import create_client, LettaClient
from letta.schemas.memory import ChatMemory
import os
import json
import psycopg2
from typing import Dict, List, Optional
from datetime import datetime, timedelta

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

def analyze_tweet_performance(days: int = 7) -> Dict:
    """
    Analyze recent tweet performance to identify winning patterns.

    Args:
        days: Number of days to look back

    Returns:
        Dict with performance analysis
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get top performers
    cursor.execute(
        """SELECT
               id,
               content,
               (performance->>'engagement_rate')::float as engagement,
               (performance->>'likes')::int as likes,
               tags,
               format_type,
               template_id
           FROM content_archive
           WHERE type = 'tweet'
           AND published_at > NOW() - INTERVAL '%s days'
           AND performance->>'engagement_rate' IS NOT NULL
           ORDER BY (performance->>'engagement_rate')::float DESC
           LIMIT 10""",
        (days,)
    )

    top_performers = []
    for row in cursor.fetchall():
        top_performers.append({
            "id": str(row[0]),
            "content": row[1],
            "engagement_rate": row[2],
            "likes": row[3],
            "tags": row[4],
            "format_type": row[5],
            "template_id": str(row[6]) if row[6] else None
        })

    # Get average performance by format type
    cursor.execute(
        """SELECT
               format_type,
               COUNT(*) as count,
               AVG((performance->>'engagement_rate')::float) as avg_engagement,
               AVG((performance->>'likes')::int) as avg_likes
           FROM content_archive
           WHERE type = 'tweet'
           AND published_at > NOW() - INTERVAL '%s days'
           AND format_type IS NOT NULL
           GROUP BY format_type""",
        (days,)
    )

    format_performance = {}
    for row in cursor.fetchall():
        format_performance[row[0]] = {
            "count": row[1],
            "avg_engagement": float(row[2]) if row[2] else 0,
            "avg_likes": int(row[3]) if row[3] else 0
        }

    cursor.close()
    conn.close()

    return {
        "top_performers": top_performers,
        "format_performance": format_performance,
        "analysis_period_days": days,
        "total_analyzed": sum(fp["count"] for fp in format_performance.values())
    }


def get_validated_ideas(limit: int = 10, unused_only: bool = True) -> List[Dict]:
    """
    Retrieve validated ideas ready for content creation.

    Args:
        limit: Max number of ideas to return
        unused_only: Only return ideas not yet used

    Returns:
        List of validated idea dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """SELECT
                   id,
                   topic,
                   angle,
                   source,
                   performance_score,
                   tags,
                   validated_at
               FROM ideas_database
               WHERE validation_status = 'validated'"""

    if unused_only:
        query += " AND used_at IS NULL"

    query += " ORDER BY performance_score DESC, validated_at DESC LIMIT %s"

    cursor.execute(query, (limit,))

    ideas = []
    for row in cursor.fetchall():
        ideas.append({
            "id": str(row[0]),
            "topic": row[1],
            "angle": row[2],
            "source": row[3],
            "performance_score": float(row[4]) if row[4] else 0,
            "tags": row[5],
            "validated_at": row[6].isoformat() if row[6] else None
        })

    cursor.close()
    conn.close()

    return ideas


def add_idea_to_backlog(
    topic: str,
    angle: Optional[str] = None,
    source: str = "manual",
    tags: Optional[List[str]] = None,
    source_content_id: Optional[str] = None
) -> str:
    """
    Add a new idea to the backlog.

    Args:
        topic: The main topic/subject
        angle: Specific angle or perspective
        source: Where the idea came from
        tags: Optional list of tags
        source_content_id: Optional link to source content

    Returns:
        ID of created idea
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO ideas_database
           (topic, angle, source, tags, source_content_id, validation_status)
           VALUES (%s, %s, %s, %s, %s, %s)
           RETURNING id""",
        (topic, angle, source, json.dumps(tags or []), source_content_id, 'pending')
    )

    idea_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return str(idea_id)


def validate_idea(idea_id: str, performance_score: float) -> bool:
    """
    Mark an idea as validated based on performance.

    Args:
        idea_id: UUID of the idea
        performance_score: Performance score (e.g., engagement rate)

    Returns:
        Success boolean
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE ideas_database
           SET validation_status = 'validated',
               validated_at = CURRENT_TIMESTAMP,
               performance_score = %s
           WHERE id = %s""",
        (performance_score, idea_id)
    )

    success = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()

    return success


def recommend_next_posts(
    count: int = 3,
    experimental_ratio: float = 0.7
) -> Dict:
    """
    Recommend next posts based on 70/30 experimental vs proven rule.

    Args:
        count: Total number of posts to recommend
        experimental_ratio: Ratio of experimental content (default 0.7)

    Returns:
        Dict with recommendations
    """
    experimental_count = int(count * experimental_ratio)
    proven_count = count - experimental_count

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get proven format recommendations (validated ideas + high-performing templates)
    cursor.execute(
        """SELECT
               i.id as idea_id,
               i.topic,
               i.angle,
               s.id as template_id,
               s.name as template_name,
               s.category,
               'proven' as recommendation_type
           FROM ideas_database i
           CROSS JOIN swipe_file s
           WHERE i.validation_status = 'validated'
           AND i.used_at IS NULL
           AND s.is_active = true
           AND (s.performance_history->>'plateau_detected')::boolean IS NOT TRUE
           ORDER BY
               i.performance_score DESC,
               (s.performance_history->>'avg_engagement')::float DESC NULLS LAST
           LIMIT %s""",
        (proven_count,)
    )

    proven_recommendations = []
    for row in cursor.fetchall():
        proven_recommendations.append({
            "idea_id": str(row[0]),
            "topic": row[1],
            "angle": row[2],
            "template_id": str(row[3]),
            "template_name": row[4],
            "template_category": row[5],
            "type": row[6]
        })

    # Get experimental recommendations (mix of new ideas and new templates)
    cursor.execute(
        """SELECT
               i.id as idea_id,
               i.topic,
               i.angle,
               s.id as template_id,
               s.name as template_name,
               s.category,
               'experimental' as recommendation_type
           FROM ideas_database i
           CROSS JOIN swipe_file s
           WHERE (i.validation_status = 'pending' OR i.validation_status = 'validated')
           AND i.used_at IS NULL
           AND s.is_active = true
           ORDER BY RANDOM()
           LIMIT %s""",
        (experimental_count,)
    )

    experimental_recommendations = []
    for row in cursor.fetchall():
        experimental_recommendations.append({
            "idea_id": str(row[0]),
            "topic": row[1],
            "angle": row[2],
            "template_id": str(row[3]),
            "template_name": row[4],
            "template_category": row[5],
            "type": row[6]
        })

    cursor.close()
    conn.close()

    return {
        "proven": proven_recommendations,
        "experimental": experimental_recommendations,
        "total_count": len(proven_recommendations) + len(experimental_recommendations),
        "ratio": {
            "proven": len(proven_recommendations) / count if count > 0 else 0,
            "experimental": len(experimental_recommendations) / count if count > 0 else 0
        }
    }


def identify_trending_topics(days: int = 7, min_engagement: float = 3.0) -> List[Dict]:
    """
    Identify trending topics from recent high-performing content.

    Args:
        days: Days to look back
        min_engagement: Minimum engagement rate threshold

    Returns:
        List of trending topics with metadata
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT
               tags,
               COUNT(*) as frequency,
               AVG((performance->>'engagement_rate')::float) as avg_engagement
           FROM content_archive
           WHERE published_at > NOW() - INTERVAL '%s days'
           AND (performance->>'engagement_rate')::float >= %s
           AND tags IS NOT NULL
           GROUP BY tags
           HAVING COUNT(*) >= 2
           ORDER BY avg_engagement DESC
           LIMIT 10""",
        (days, min_engagement)
    )

    trends = []
    for row in cursor.fetchall():
        trends.append({
            "tags": row[0],
            "frequency": row[1],
            "avg_engagement": float(row[2]) if row[2] else 0
        })

    cursor.close()
    conn.close()

    return trends


def check_idea_saturation(topic: str, days: int = 30) -> Dict:
    """
    Check if a topic has been overused recently.

    Args:
        topic: Topic to check
        days: Time period to check

    Returns:
        Dict with saturation analysis
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT COUNT(*) as usage_count
           FROM content_archive
           WHERE published_at > NOW() - INTERVAL '%s days'
           AND (content ILIKE '%%' || %s || '%%' OR title ILIKE '%%' || %s || '%%')""",
        (days, topic, topic)
    )

    usage_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    # Simple saturation heuristic
    is_saturated = usage_count >= 3  # More than 3 times in the period

    return {
        "topic": topic,
        "usage_count": usage_count,
        "days_analyzed": days,
        "is_saturated": is_saturated,
        "recommendation": "avoid" if is_saturated else "ok_to_use"
    }


# =============================================================================
# AGENT CREATION
# =============================================================================

def create_content_strategist_agent():
    """
    Create and configure the Content Strategist Agent
    """

    agent_state = client.create_agent(
        name="content-strategist-agent",

        memory=ChatMemory(
            human="Dan Koe - content creator and educator in the productivity/business space",
            persona="""You are the Content Strategist for Dan Koe's content operation.

YOUR ROLE:
You manage the entire content ideation and validation pipeline. You decide what content should be created, when, and in what format.

KEY RESPONSIBILITIES:
1. Analyze performance data to identify what's working
2. Validate ideas based on audience engagement
3. Maintain the content backlog (ideas database)
4. Recommend daily content based on the 70/30 rule:
   - 70% experimental (testing new ideas, formats)
   - 30% proven (double down on what works)
5. Prevent topic saturation and repetition
6. Identify emerging trends worth exploring

STRATEGIC PRINCIPLES:
- Data-driven: Let engagement metrics guide decisions
- Audience-first: What resonates with Dan's audience?
- Platform-aware: Twitter tests ideas, newsletters expand winners
- Sustainable: Don't burn out topics, maintain variety
- Growth-focused: Balance proven content (stability) with experiments (discovery)

DECISION FRAMEWORK:
- If a tweet gets >5% engagement → validate the idea
- If a topic appears 3+ times in 30 days → it's saturated
- If a template's performance plateaus → rotate it out
- If an experimental format succeeds 3x → move to "proven"

You work closely with:
- Content Generation Agent (executes your recommendations)
- Performance Analysis Agent (provides you data)
- Research Agent (finds supporting material for ideas)

Your output should be strategic, specific, and actionable."""
        ),

        tools=[
            analyze_tweet_performance,
            get_validated_ideas,
            add_idea_to_backlog,
            validate_idea,
            recommend_next_posts,
            identify_trending_topics,
            check_idea_saturation
        ],

        system="""You are the Content Strategist Agent.

When asked for content recommendations:
1. Analyze recent performance using analyze_tweet_performance
2. Check for trending topics using identify_trending_topics
3. Get validated ideas using get_validated_ideas
4. Use recommend_next_posts to generate balanced recommendations
5. Check for topic saturation before finalizing
6. Return specific, actionable recommendations

When evaluating content performance:
1. Look for patterns in what works (format, topic, style)
2. Validate high-performing ideas using validate_idea
3. Add new winning angles to the backlog using add_idea_to_backlog
4. Update strategy based on data

Always explain your strategic reasoning."""
    )

    print(f"✓ Content Strategist Agent created: {agent_state.id}")
    print(f"  Name: {agent_state.name}")

    return agent_state


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Create the agent
    agent = create_content_strategist_agent()

    # Example interaction
    response = client.send_message(
        agent_id=agent.id,
        message="""Analyze the past week's performance and recommend 3 posts for tomorrow.

Include:
1. What's working (top performers)
2. Any trends worth exploring
3. Specific post recommendations with idea + template pairs
4. Your strategic reasoning""",
        role="user"
    )

    print("\n" + "="*80)
    print("AGENT RESPONSE:")
    print("="*80)
    for message in response.messages:
        print(f"\n[{message.role}]: {message.text}")

    print("\n" + "="*80)
    print(f"Agent ID: {agent.id}")
    print("Use this in n8n workflows to get strategic recommendations!")
    print("="*80)
