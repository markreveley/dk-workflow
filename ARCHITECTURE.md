# Dan Koe Content Workflow Architecture
## Using n8n + Letta Agents

---

## System Overview

This architecture implements Dan Koe's AI-powered content creation workflow using:
- **n8n**: Workflow orchestration, scheduling, and platform integrations
- **Letta Agents**: Stateful AI agents with memory for personalized content generation

### Key Design Principles
1. **Stateful Intelligence**: Letta agents maintain context about brand voice, performance history, and personal archives
2. **Automated Validation**: Built-in feedback loops from social metrics
3. **Scalable Repurposing**: Single-source content flows to multiple platforms
4. **Learning System**: Continuous improvement from engagement data

---

## Architecture Components

### 1. Letta Agents (Stateful AI Layer)

#### Agent 1: **Content Strategist Agent**
**Purpose**: Manages ideation, validation, and strategic decisions

**Memory/State**:
- Running ideas document (validated topics, angles, concepts)
- Performance history (what worked, what didn't)
- Personal swipe file (effective post structures)
- Brand voice guidelines and writing style
- Archive of past content for reference

**Capabilities**:
- Analyze Twitter/X engagement metrics to identify winning ideas
- Parse YouTube analytics to find top-performing topics
- Compare new research material against personal archives
- Generate strategic recommendations for content direction
- Maintain and update the ideas backlog

**Tools/Functions**:
- Query social media APIs for performance data
- Access personal content archive database
- Score and prioritize ideas based on validation criteria

---

#### Agent 2: **Research & Synthesis Agent**
**Purpose**: Deep content research and summarization

**Memory/State**:
- Personal knowledge base and previous research notes
- Summary templates and formats
- Topic expertise areas and research depth preferences
- Citations and source tracking

**Capabilities**:
- Process long-form content (videos, books, articles) using LLM context windows
- Compare new information with existing knowledge base
- Generate actionable summary notes (6+ hours → 1000 words)
- Extract key insights, frameworks, and actionable takeaways
- Build research dossiers for newsletter topics

**Tools/Functions**:
- Video transcription integration (YouTube API, Gemini)
- Document parsing (PDFs, web articles)
- Knowledge base querying
- Citation management

---

#### Agent 3: **Content Generation Agent**
**Purpose**: Create first drafts across all formats

**Memory/State**:
- Writing voice patterns and style guide
- Historical successful content examples
- Format templates (newsletter, tweets, YouTube scripts)
- Psychological frameworks and storytelling arcs

**Capabilities**:
- Draft newsletter sections based on research notes
- Generate 2-3 daily social posts
- Create meta-prompts that interview for context
- Apply deconstructed post structures to new ideas
- Maintain consistency with brand voice

**Tools/Functions**:
- Access to content templates
- Integration with research notes
- Multi-format output generation

---

#### Agent 4: **Repurposing & Multiplier Agent**
**Purpose**: Transform core content into derivative assets

**Memory/State**:
- Top-performing content patterns and structures
- Platform-specific optimization rules
- Historical repurposing success rates
- Format conversion templates

**Capabilities**:
- Generate 20-30 YouTube titles from newsletter
- Extract "deep post" content (paradoxes, quotes, arcs)
- Produce 60 content ideas using best historical formats
- Adapt content for platform-specific requirements
- Create visual asset suggestions

**Tools/Functions**:
- Newsletter → YouTube title conversion
- Deep post extraction algorithms
- Content idea generation at scale
- Platform format adaptation

---

#### Agent 5: **Performance Analysis Agent**
**Purpose**: Continuous learning and optimization

**Memory/State**:
- Engagement metrics across all platforms
- A/B test results and insights
- Pattern recognition models (what drives 30% proven vs 70% experimental)
- Trend detection and plateau identification

**Capabilities**:
- Analyze post performance and identify patterns
- Deconstruct high-performing content (own and competitors)
- Generate meta-insights about structure, psychology, stylistics
- Recommend iteration strategies (double down vs experiment)
- Detect when formats are plateauing

**Tools/Functions**:
- Social media analytics integration
- Pattern recognition algorithms
- Competitive analysis tools
- Recommendation engine

---

### 2. n8n Workflows (Orchestration Layer)

#### Workflow 1: **Daily Content Creation Pipeline**

**Trigger**: Scheduled (Every morning, 6 AM)

**Steps**:
1. **Fetch Today's Ideas**
   - Query Content Strategist Agent for daily post queue
   - Pull validated ideas from backlog

2. **Generate Morning Posts**
   - Content Generation Agent creates 2-3 social posts
   - Apply 70/30 rule (experimental vs proven formats)

3. **Human Review Gate**
   - Send drafts to review interface (Slack/Email/Custom UI)
   - Wait for approval/edits

4. **Schedule & Publish**
   - Buffer/Hootsuite API integration
   - Post to Twitter/X with optimal timing

5. **Log Content**
   - Store published content in database
   - Tag with metadata (format type, experiment vs proven)

**n8n Nodes**:
- Schedule Trigger
- HTTP Request (to Letta agents)
- Slack/Email notification
- Wait for webhook (approval)
- Twitter API / Buffer API
- PostgreSQL / Airtable (content log)

---

#### Workflow 2: **Weekly Newsletter Production**

**Trigger**: Scheduled (Every Monday, 8 AM)

**Steps**:
1. **Topic Selection**
   - Content Strategist Agent analyzes last week's Twitter performance
   - Identifies validated topics or pulls from YouTube trends
   - Returns topic + angle

2. **Deep Research**
   - Research & Synthesis Agent processes source materials
   - Summarizes videos, articles, books
   - Compares with personal archive
   - Outputs 1000-word research brief

3. **Newsletter Drafting**
   - Content Generation Agent writes newsletter sections
   - Applies brand voice and storytelling frameworks

4. **Human Review & Edit**
   - Send draft to editing interface
   - Wait for final approval

5. **Publish Newsletter**
   - Send via email platform (ConvertKit, Beehiiv, etc.)
   - Publish to website/blog

6. **Trigger Repurposing**
   - Pass newsletter to Workflow 3 (Multiplier Pipeline)

**n8n Nodes**:
- Schedule Trigger
- HTTP Request to multiple Letta agents
- Wait nodes for human review
- Email platform API (ConvertKit/Beehiiv)
- Webhook trigger to next workflow

---

#### Workflow 3: **Content Multiplier Pipeline**

**Trigger**: Webhook (from Newsletter Workflow completion)

**Steps**:
1. **Receive Newsletter Content**
   - Parse newsletter text

2. **Generate Derivative Assets (Parallel)**
   - Branch 1: Repurposing Agent → 20-30 YouTube titles
   - Branch 2: Repurposing Agent → Deep post extractions
   - Branch 3: Repurposing Agent → 60 new content ideas

3. **Store in Content Bank**
   - Save titles to ideas database
   - Tag deep posts for future use
   - Queue content ideas for validation

4. **YouTube Script Preparation** (Optional)
   - If YouTube video planned, generate script outline
   - Send to review queue

**n8n Nodes**:
- Webhook Trigger
- HTTP Request to Letta agents (parallel branches)
- Airtable/Notion (content bank storage)
- Merge node to consolidate results

---

#### Workflow 4: **Performance Tracking & Learning Loop**

**Trigger**: Scheduled (Every night, 11 PM)

**Steps**:
1. **Collect Metrics**
   - Fetch engagement data from Twitter/X API
   - Pull YouTube analytics
   - Retrieve email open/click rates

2. **Update Agent Memories**
   - Send performance data to Performance Analysis Agent
   - Update Content Strategist Agent with validated ideas

3. **Generate Insights**
   - Performance Analysis Agent deconstructs top performers
   - Identifies patterns and trends

4. **Update Content Strategy**
   - Adjust 70/30 experimental ratio if needed
   - Flag plateauing formats
   - Recommend new angles to test

5. **Daily Report**
   - Send summary to Slack/Email
   - Highlight top performers and key learnings

**n8n Nodes**:
- Schedule Trigger
- Twitter/X API, YouTube API, Email platform API
- HTTP Request to Letta agents
- PostgreSQL/Airtable updates
- Slack/Email notification

---

#### Workflow 5: **Idea Validation & Swipe File Management**

**Trigger**: Continuous (Monitors Twitter in real-time)

**Steps**:
1. **Monitor Posted Content**
   - Track engagement on recent posts (first 24 hours)

2. **Performance Threshold Check**
   - If post exceeds performance threshold (e.g., 100+ likes, 20+ retweets)

3. **Validate & Promote**
   - Content Strategist Agent marks idea as validated
   - Add to newsletter topic queue
   - Add post structure to swipe file

4. **Deconstruct Winning Posts**
   - Performance Analysis Agent analyzes structure
   - Extract psychological patterns
   - Update meta-prompts

**n8n Nodes**:
- Webhook Trigger (from Twitter)
- Switch node (performance threshold)
- HTTP Request to Letta agents
- Database updates

---

#### Workflow 6: **Research Content Ingestion**

**Trigger**: Manual or webhook (when new research material available)

**Steps**:
1. **Receive Content**
   - YouTube URL, article link, or uploaded document

2. **Extract & Transcribe**
   - YouTube transcription via Gemini or Whisper
   - Article scraping
   - PDF parsing

3. **Research Processing**
   - Research & Synthesis Agent summarizes content
   - Compares with existing knowledge base
   - Generates actionable notes

4. **Store & Tag**
   - Save to research database
   - Tag with topics, themes, potential use cases

5. **Update Ideas Queue**
   - If research sparks new ideas, add to backlog

**n8n Nodes**:
- Webhook/Manual Trigger
- YouTube API / Web scraping
- HTTP Request to Letta agents
- Database storage (Notion, Airtable, PostgreSQL)

---

### 3. Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CONTENT PLATFORMS                        │
│  Twitter/X  │  YouTube  │  Newsletter  │  Blog  │  LinkedIn │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    n8n ORCHESTRATION LAYER                   │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   Daily     │  │   Weekly     │  │   Performance   │    │
│  │  Content    │  │ Newsletter   │  │    Tracking     │    │
│  │  Pipeline   │  │  Production  │  │      Loop       │    │
│  └─────────────┘  └──────────────┘  └─────────────────┘    │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │  Content    │  │     Idea     │  │    Research     │    │
│  │ Multiplier  │  │  Validation  │  │   Ingestion     │    │
│  └─────────────┘  └──────────────┘  └─────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    LETTA AGENTS LAYER                        │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Content    │  │   Research   │  │   Content    │      │
│  │  Strategist  │  │      &       │  │  Generation  │      │
│  │    Agent     │  │  Synthesis   │  │    Agent     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Repurposing  │  │ Performance  │                         │
│  │      &       │  │   Analysis   │                         │
│  │  Multiplier  │  │    Agent     │                         │
│  └──────────────┘  └──────────────┘                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Ideas     │  │   Content    │  │   Research   │      │
│  │   Database   │  │    Archive   │  │  Knowledge   │      │
│  │              │  │              │  │     Base     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Swipe File  │  │  Performance │  │    Agent     │      │
│  │  (Templates) │  │   Metrics    │  │   Memory     │      │
│  │              │  │   Database   │  │    Store     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

### 4. Data Models

#### Ideas Database
```json
{
  "id": "uuid",
  "topic": "string",
  "angle": "string",
  "source": "twitter|youtube|manual",
  "validation_status": "pending|validated|used",
  "performance_score": "number",
  "created_at": "timestamp",
  "tags": ["array"],
  "related_content_ids": ["array"]
}
```

#### Content Archive
```json
{
  "id": "uuid",
  "type": "newsletter|tweet|youtube|blog",
  "title": "string",
  "content": "text",
  "published_at": "timestamp",
  "performance": {
    "views": "number",
    "engagement_rate": "number",
    "clicks": "number",
    "shares": "number"
  },
  "format_type": "experimental|proven",
  "tags": ["array"],
  "derived_from": "content_id"
}
```

#### Swipe File (Templates)
```json
{
  "id": "uuid",
  "name": "string",
  "structure": "text",
  "psychology_notes": "text",
  "example_posts": ["array"],
  "performance_history": {
    "avg_engagement": "number",
    "use_count": "number",
    "plateau_detected": "boolean"
  },
  "meta_prompt": "text"
}
```

#### Agent Memory (Letta-specific)
```json
{
  "agent_id": "string",
  "core_memory": {
    "brand_voice": "text",
    "writing_style": "text",
    "key_themes": ["array"],
    "expertise_areas": ["array"]
  },
  "archival_memory": {
    "indexed_content": "vector_db",
    "research_notes": "text[]",
    "historical_insights": "text[]"
  },
  "recall_memory": {
    "recent_interactions": "conversation_log",
    "context_window": "text"
  }
}
```

---

### 5. Implementation Roadmap

#### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up n8n instance
- [ ] Set up Letta server
- [ ] Create database schema (PostgreSQL/Airtable)
- [ ] Configure API integrations (Twitter, YouTube, email platform)
- [ ] Build basic Content Generation Agent with brand voice

#### Phase 2: Core Workflows (Weeks 3-4)
- [ ] Implement Daily Content Creation Pipeline (n8n Workflow 1)
- [ ] Build Content Strategist Agent with ideas management
- [ ] Create content archive and swipe file databases
- [ ] Set up human review gates (Slack integration)
- [ ] Deploy and test daily posting

#### Phase 3: Research & Newsletter (Weeks 5-6)
- [ ] Build Research & Synthesis Agent
- [ ] Implement Weekly Newsletter Production workflow
- [ ] Integrate video transcription (Gemini/Whisper)
- [ ] Create Research Content Ingestion workflow
- [ ] Test newsletter generation end-to-end

#### Phase 4: Multiplier & Repurposing (Week 7)
- [ ] Build Repurposing & Multiplier Agent
- [ ] Implement Content Multiplier Pipeline
- [ ] Create derivative asset templates (YouTube titles, deep posts, ideas)
- [ ] Test multi-format content generation

#### Phase 5: Learning Loop (Week 8)
- [ ] Build Performance Analysis Agent
- [ ] Implement Performance Tracking workflow
- [ ] Create Idea Validation workflow
- [ ] Set up automated metrics collection
- [ ] Build deconstructing algorithm for winning posts

#### Phase 6: Optimization (Weeks 9-10)
- [ ] Refine agent prompts and memory structures
- [ ] Optimize workflow timing and triggers
- [ ] Implement A/B testing capabilities
- [ ] Add visual asset generation (optional)
- [ ] Build analytics dashboard

#### Phase 7: Scale & Polish (Weeks 11-12)
- [ ] Add additional platform integrations (LinkedIn, Instagram, etc.)
- [ ] Implement advanced meta-prompt generation
- [ ] Create mobile review interface
- [ ] Add voice/video input for research
- [ ] Final testing and documentation

---

### 6. Key Technical Considerations

#### Letta Agent Design

**Memory Architecture**:
- **Core Memory**: Persona, brand voice, permanent context (editable)
- **Archival Memory**: Vector database of all content, research, examples (searchable)
- **Recall Memory**: Conversation history, recent context

**Agent Communication**:
- Agents can call each other via function tools
- Example: Content Generation Agent calls Research Agent for additional context
- Shared memory space for cross-agent context

**Tools/Functions**:
- Each agent has custom tools (API calls, database queries, calculations)
- Letta agents can execute Python functions
- Integration with external APIs via HTTP requests

#### n8n Best Practices

**Error Handling**:
- Retry logic for API calls (exponential backoff)
- Fallback nodes for agent failures
- Alert notifications for critical failures

**Human-in-the-Loop**:
- Strategic review gates (not every step automated)
- Easy override and editing interfaces
- Quick approve/reject mechanisms

**Modularity**:
- Each workflow is independent
- Shared sub-workflows for common tasks
- Webhook-based communication between workflows

**Scalability**:
- Queue-based processing for high volume
- Batch operations where possible
- Caching for frequently accessed data

---

### 7. Example User Journey

**Monday Morning - Newsletter Week**:

1. **8:00 AM**: n8n triggers Newsletter Production workflow
2. Content Strategist Agent analyzes last week's Twitter data, identifies "productivity systems" as validated topic
3. Research & Synthesis Agent processes 3 YouTube videos (4 hours of content) + 2 articles, generates 1000-word research brief
4. **9:00 AM**: User receives Slack notification with research brief
5. **10:00 AM**: User reviews, adds personal notes, approves
6. Content Generation Agent drafts 2500-word newsletter in brand voice
7. **11:00 AM**: User receives draft, edits, approves
8. Newsletter publishes at 2:00 PM (scheduled)
9. Content Multiplier workflow triggered:
   - Generates 25 YouTube titles
   - Extracts 15 "deep post" elements
   - Creates 60 new content ideas
10. All assets saved to content bank, tagged and ready for use

**Daily - Morning Content**:

1. **6:00 AM**: Daily Content Pipeline triggers
2. Content Strategist pulls 3 ideas: 2 proven formats, 1 experimental
3. Content Generation Agent creates posts using meta-prompts
4. **6:15 AM**: User receives posts in Slack
5. **6:30 AM**: User approves (or quick edits)
6. Posts scheduled for 9 AM, 12 PM, 4 PM
7. Throughout day: Idea Validation workflow monitors performance
8. **11:00 PM**: Performance Tracking workflow runs, updates agent memories

**Continuous**:
- Ideas that exceed threshold automatically validated
- Winning posts deconstructed and added to swipe file
- Performance insights update strategy weekly
- 70/30 experimental ratio auto-adjusted based on growth

---

### 8. Success Metrics

**Efficiency Gains**:
- Research time: 6+ hours → 30 minutes
- Newsletter writing: 4 hours → 2 hours
- Daily posts: 60 minutes → 15 minutes
- Repurposing: 2 hours → automated (5 minute review)

**Quality Metrics**:
- Engagement rate maintained or improved
- Brand voice consistency score (agent evaluation)
- Idea validation rate (% of tested ideas that perform)
- Content reuse efficiency (derivatives per core piece)

**Growth Metrics**:
- Follower growth rate
- Newsletter subscriber growth
- Cross-platform reach expansion
- Time-to-publish velocity

---

### 9. Future Enhancements

**Advanced Features**:
- Visual content generation (AI images, thumbnails)
- Video editing automation (YouTube shorts from long-form)
- Real-time trend detection and rapid response
- Competitive intelligence (analyze competitor content)
- Voice-based content input (transcribe ideas on-the-go)
- Multi-author collaboration (team-based workflows)

**AI Improvements**:
- Fine-tuned models on personal content corpus
- Advanced pattern recognition (deep learning on engagement data)
- Predictive analytics (forecast content performance)
- Automated A/B testing across platforms
- Self-improving prompts (meta-learning from results)

---

## Getting Started

### Prerequisites
- n8n instance (self-hosted or cloud)
- Letta server (local or cloud deployment)
- API keys: Twitter/X, YouTube, email platform
- Database: PostgreSQL or Airtable
- LLM API access: Claude, GPT-4, Gemini

### Quick Start
1. Clone this repository
2. Import n8n workflow templates from `/workflows` directory
3. Deploy Letta agents from `/agents` directory
4. Configure credentials in n8n
5. Set up database connections
6. Run initial agent training with brand voice samples
7. Test individual workflows before full automation

---

## Conclusion

This architecture transforms Dan Koe's content workflow into a fully automated, AI-powered system that maintains quality while maximizing efficiency. By combining n8n's orchestration capabilities with Letta's stateful agent intelligence, the system learns, adapts, and scales with minimal manual intervention.

The key innovation is the **feedback loop**: performance data continuously improves agent decision-making, creating a self-optimizing content engine that gets better over time.
