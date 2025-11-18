# Implementation Guide: Dan Koe Content Workflow
## n8n + Letta Agents Setup

---

## Quick Reference

**Project Goal**: Automate Dan Koe's content creation workflow using n8n (orchestration) + Letta agents (AI intelligence)

**Time to Deploy**: 8-12 weeks (phased approach)

**Core Stack**:
- n8n (workflow automation)
- Letta (stateful AI agents)
- PostgreSQL/Airtable (data storage)
- Claude/GPT-4/Gemini (LLM providers)

---

## Phase 1: Setup (Week 1-2)

### Step 1: Install n8n

**Option A: Self-Hosted (Recommended for full control)**
```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Using npm
npm install n8n -g
n8n start
```

**Option B: n8n Cloud**
- Sign up at https://n8n.io/cloud
- Instant setup, managed hosting

### Step 2: Install Letta

```bash
# Install Letta
pip install letta

# Start Letta server
letta server

# Or use Docker
docker pull letta/letta
docker run -p 8283:8283 letta/letta
```

**Configure Letta**:
```bash
# Set up LLM provider (example: OpenAI)
letta configure

# Choose your provider:
# - OpenAI (GPT-4)
# - Anthropic (Claude)
# - Google (Gemini)
# - Local (Ollama)
```

### Step 3: Database Setup

**PostgreSQL (Recommended)**:
```bash
# Using Docker
docker run --name content-db \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=content_workflow \
  -p 5432:5432 \
  -d postgres

# Create tables
psql -U postgres -d content_workflow -f schema.sql
```

**Or use Airtable** (easier, no-code option):
1. Create Airtable base
2. Import schema from `/database/airtable-schema.json`
3. Get API key

### Step 4: API Credentials

Collect the following API keys:

- **Twitter/X API**: https://developer.twitter.com/
  - Need: API Key, API Secret, Access Token, Access Secret

- **YouTube API**: https://console.cloud.google.com/
  - Enable YouTube Data API v3
  - Create OAuth 2.0 credentials

- **Email Platform**:
  - ConvertKit: https://app.convertkit.com/account_settings/advanced_settings
  - Beehiiv: https://www.beehiiv.com/developers

- **LLM APIs**:
  - Anthropic Claude: https://console.anthropic.com/
  - OpenAI GPT-4: https://platform.openai.com/
  - Google Gemini: https://ai.google.dev/

---

## Phase 2: Build First Letta Agent (Week 3)

### Agent 1: Content Generation Agent

**Create Agent**:
```bash
# Using Letta CLI
letta create agent \
  --name content-generation-agent \
  --persona "You are a content creator specializing in writing engaging social media posts and newsletters in Dan Koe's style." \
  --human "Dan Koe - content creator focused on productivity, online business, and personal development"
```

**Python Script** (`agents/content_generation_agent.py`):
```python
from letta import create_client

client = create_client()

# Define agent
agent_state = client.create_agent(
    name="content-generation-agent",

    # Core Memory
    memory={
        "persona": """You are an expert content creator who writes in Dan Koe's style:
        - Direct, actionable advice
        - Focus on systems thinking and frameworks
        - Blend philosophy with practical tactics
        - Use psychological hooks and paradoxes
        - Concise, punchy language""",

        "human": "Dan Koe - productivity and business content creator"
    },

    # Tools the agent can use
    tools=[
        "generate_tweet",
        "generate_newsletter_section",
        "apply_template"
    ]
)

# Define custom tools
@client.tool
def generate_tweet(idea: str, format_type: str) -> str:
    """Generate a tweet based on an idea and format type."""
    # This would call your LLM with specific prompts
    pass

@client.tool
def apply_template(content: str, template_id: str) -> str:
    """Apply a swipe file template to content."""
    # Retrieve template from database and apply structure
    pass
```

**Test Agent**:
```python
# Send a message to the agent
response = client.send_message(
    agent_id=agent_state.id,
    message="Generate 3 tweets about productivity systems. Use proven formats.",
    role="user"
)

print(response.messages)
```

---

## Phase 3: Build First n8n Workflow (Week 3-4)

### Workflow: Daily Content Creation Pipeline

**Step-by-Step in n8n UI**:

1. **Add Schedule Trigger**
   - Node: Schedule Trigger
   - Settings: Cron `0 6 * * *` (6 AM daily)

2. **Call Letta Agent for Ideas**
   - Node: HTTP Request
   - Method: POST
   - URL: `http://localhost:8283/v1/agents/{agent_id}/messages`
   - Headers: `Authorization: Bearer {letta_api_key}`
   - Body:
     ```json
     {
       "message": "Generate 3 social media posts: 2 proven formats, 1 experimental",
       "role": "user"
     }
     ```

3. **Parse Agent Response**
   - Node: Code (JavaScript)
   ```javascript
   const messages = $input.item.json.messages;
   const posts = messages[messages.length - 1].content;

   // Parse posts (assuming agent returns JSON array)
   return { posts: JSON.parse(posts) };
   ```

4. **Send for Review**
   - Node: Slack
   - Channel: `#content-review`
   - Message: `New posts ready for review: {{$json.posts}}`
   - Add approve/reject buttons (Slack interactive messages)

5. **Wait for Approval**
   - Node: Webhook (Wait)
   - Configure webhook URL for Slack response

6. **Publish to Twitter**
   - Node: Twitter (or HTTP Request to Twitter API)
   - For each post:
     - Tweet Text: `{{$json.post.content}}`
     - Schedule time: `{{$json.post.scheduled_time}}`

7. **Log to Database**
   - Node: PostgreSQL / Airtable
   - Insert published content with metadata

**Save Workflow**:
- Name: "Daily Content Creation Pipeline"
- Activate workflow
- Test with manual execution first

---

## Phase 4: Connect Everything (Week 5-6)

### Integration Pattern

**n8n calls Letta agent**:
```javascript
// In n8n HTTP Request node
{
  "method": "POST",
  "url": "http://localhost:8283/v1/agents/{{$node["Get_Agent_ID"].json["agent_id"]}}/messages",
  "headers": {
    "Authorization": "Bearer YOUR_LETTA_API_KEY",
    "Content-Type": "application/json"
  },
  "body": {
    "message": "Your task description here",
    "role": "user"
  }
}
```

**Letta agent calls external API** (via tools):
```python
@client.tool
def fetch_twitter_analytics(tweet_id: str) -> dict:
    """Fetch performance metrics for a tweet."""
    import requests

    response = requests.get(
        f"https://api.twitter.com/2/tweets/{tweet_id}",
        headers={"Authorization": f"Bearer {TWITTER_API_KEY}"},
        params={"tweet.fields": "public_metrics"}
    )

    return response.json()
```

**Store in Database**:
```python
@client.tool
def save_to_content_archive(content: dict) -> str:
    """Save content to the archive database."""
    import psycopg2

    conn = psycopg2.connect(
        dbname="content_workflow",
        user="postgres",
        password="yourpassword",
        host="localhost"
    )

    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO content_archive
           (type, title, content, published_at, tags)
           VALUES (%s, %s, %s, %s, %s)""",
        (content['type'], content['title'], content['content'],
         content['published_at'], content['tags'])
    )

    conn.commit()
    return "Saved successfully"
```

---

## Phase 5: Agent Memory Management

### Core Memory (Editable Context)

**Set Brand Voice**:
```python
client.update_agent_memory(
    agent_id=agent_id,
    memory_type="core",
    memory_content={
        "brand_voice": """
        - Write with authority but remain relatable
        - Use frameworks and systems thinking
        - Blend big-picture philosophy with tactical advice
        - Keep sentences short and punchy
        - Use paradoxes to create curiosity
        """,
        "key_themes": [
            "productivity systems",
            "online business",
            "personal development",
            "AI and automation",
            "content creation"
        ]
    }
)
```

### Archival Memory (Long-term Storage)

**Add Past Content Examples**:
```python
# Add successful content to agent's archival memory
client.insert_archival_memory(
    agent_id=agent_id,
    content="[High-performing tweet]: The paradox of productivity: The less you try to do, the more you accomplish. Master the art of subtraction.",
    metadata={"type": "tweet", "engagement": 850, "format": "paradox"}
)
```

**Query Archival Memory**:
```python
# Agent can search its own archive
@client.tool
def search_past_content(query: str, limit: int = 5) -> list:
    """Search archival memory for similar past content."""
    results = client.get_archival_memory(
        agent_id=agent_id,
        query=query,
        limit=limit
    )
    return results
```

---

## Phase 6: Testing & Refinement

### Test Each Component

**1. Test Agent in Isolation**:
```python
# Test content generation
response = client.send_message(
    agent_id=content_agent_id,
    message="Generate a tweet about AI automation",
    role="user"
)

print("Agent response:", response.messages[-1].content)
```

**2. Test n8n Workflow Manually**:
- Click "Execute Workflow" in n8n
- Check each node's output
- Verify data passing between nodes

**3. Test Integration**:
- Trigger workflow
- Monitor agent logs
- Check database entries
- Verify posts appear on platforms

### Common Issues & Fixes

**Issue**: Agent responses are inconsistent
- **Fix**: Improve core memory with more specific instructions
- Add examples to archival memory

**Issue**: n8n workflow times out
- **Fix**: Increase timeout in HTTP Request nodes
- Add error handling nodes

**Issue**: Database connection fails
- **Fix**: Check credentials in n8n
- Verify database is running
- Check firewall/network settings

---

## Phase 7: Production Deployment

### Checklist Before Going Live

- [ ] All API keys are in environment variables (not hardcoded)
- [ ] Error notifications set up (Slack/Email)
- [ ] Database backups configured
- [ ] Rate limits considered (Twitter API has limits)
- [ ] Human review gates in place (don't fully automate immediately)
- [ ] Monitoring dashboard created
- [ ] Fallback workflows for failures

### Monitoring

**n8n Monitoring**:
- View execution history in n8n UI
- Set up error notifications
- Monitor execution times

**Letta Monitoring**:
```python
# Get agent's recent activity
executions = client.get_agent_messages(
    agent_id=agent_id,
    limit=50
)

# Check for errors or unusual patterns
for execution in executions:
    if execution.status == "error":
        print(f"Error: {execution.error_message}")
```

**Database Monitoring**:
```sql
-- Check content publishing rate
SELECT DATE(published_at), COUNT(*)
FROM content_archive
GROUP BY DATE(published_at)
ORDER BY DATE(published_at) DESC
LIMIT 30;

-- Monitor performance trends
SELECT type, AVG(performance->>'engagement_rate') as avg_engagement
FROM content_archive
WHERE published_at > NOW() - INTERVAL '30 days'
GROUP BY type;
```

---

## Scaling & Optimization

### As Volume Grows

**1. Optimize Letta Agent Calls**:
- Cache frequent queries
- Batch operations when possible
- Use streaming for long responses

**2. Database Optimization**:
- Add indexes on frequently queried fields
- Implement archiving strategy for old content
- Use connection pooling

**3. n8n Performance**:
- Split large workflows into smaller sub-workflows
- Use queue modes for high-volume operations
- Enable workflow-level caching

**4. Cost Management**:
- Monitor LLM API usage
- Use cheaper models for simple tasks (GPT-3.5 vs GPT-4)
- Implement local models where possible (Ollama)

---

## Example: Complete Agent Definition

**File**: `agents/content_strategist.py`

```python
from letta import create_client, tool
import os

client = create_client(base_url=os.getenv("LETTA_SERVER_URL"))

# Create Content Strategist Agent
agent = client.create_agent(
    name="content-strategist",

    memory={
        "persona": """You are a content strategist for Dan Koe. Your job is to:
        1. Manage the content ideas backlog
        2. Analyze performance data to validate ideas
        3. Recommend what content to create next
        4. Maintain the 70% experiment / 30% proven format ratio

        You have deep knowledge of Dan's brand, audience, and what performs well.""",

        "human": """Dan Koe - content creator and educator focused on:
        - Building online businesses
        - Productivity systems
        - AI and automation
        - Personal development through content creation

        Audience: Entrepreneurs, creators, knowledge workers aged 25-45"""
    },

    tools=[
        "analyze_tweet_performance",
        "get_validated_ideas",
        "add_idea_to_backlog",
        "recommend_next_posts"
    ]
)

# Define tools
@tool
def analyze_tweet_performance(days: int = 7) -> dict:
    """Analyze recent tweet performance to identify patterns."""
    # Connect to database and fetch metrics
    import psycopg2

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT content, performance->>'engagement_rate' as engagement,
               tags, format_type
        FROM content_archive
        WHERE type = 'tweet'
        AND published_at > NOW() - INTERVAL '%s days'
        ORDER BY (performance->>'engagement_rate')::float DESC
        LIMIT 10
    """, (days,))

    results = cursor.fetchall()

    return {
        "top_performers": results,
        "analysis": "Ready for agent analysis"
    }

@tool
def get_validated_ideas(limit: int = 5) -> list:
    """Retrieve validated ideas from the backlog."""
    import psycopg2

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, angle, source, performance_score
        FROM ideas_database
        WHERE validation_status = 'validated'
        AND validation_status != 'used'
        ORDER BY performance_score DESC
        LIMIT %s
    """, (limit,))

    return cursor.fetchall()

@tool
def recommend_next_posts(count: int = 3) -> dict:
    """Recommend next posts based on 70/30 rule and performance data."""

    # Logic to determine 70% experimental, 30% proven
    experimental_count = int(count * 0.7)
    proven_count = count - experimental_count

    # Get proven formats from swipe file
    # Get experimental ideas from backlog
    # Return recommendations

    return {
        "experimental": experimental_count,
        "proven": proven_count,
        "recommendations": [
            # List of recommended post ideas
        ]
    }

# Register tools with agent
client.add_tool_to_agent(agent.id, analyze_tweet_performance)
client.add_tool_to_agent(agent.id, get_validated_ideas)
client.add_tool_to_agent(agent.id, recommend_next_posts)

print(f"Content Strategist Agent created: {agent.id}")
```

---

## Next Steps

1. **Week 1-2**: Complete Phase 1 setup
2. **Week 3**: Build and test first Letta agent
3. **Week 4**: Build and test first n8n workflow
4. **Week 5-6**: Connect agents and workflows
5. **Week 7-8**: Add remaining workflows (newsletter, research, etc.)
6. **Week 9-10**: Implement learning loop and performance tracking
7. **Week 11-12**: Optimize, test, and go live

**Resources**:
- n8n Documentation: https://docs.n8n.io/
- Letta Documentation: https://docs.letta.ai/
- Dan Koe's Workflow Video: https://www.youtube.com/watch?v=HhspudqFSvU

**Support**:
- n8n Community: https://community.n8n.io/
- Letta Discord: https://discord.gg/letta
- This repo's issues for questions

---

Good luck building your AI-powered content engine! 🚀
