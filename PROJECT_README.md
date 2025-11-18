# Dan Koe AI Content Workflow

**Automated content creation system using n8n orchestration + Letta AI agents**

Transform Dan Koe's manual content workflow into a self-improving, AI-powered content engine that learns from performance data and scales content production while maintaining quality and authenticity.

---

## 📋 Overview

This project implements Dan Koe's complete content workflow as described in [his YouTube video](https://www.youtube.com/watch?v=HhspudqFSvU), using:

- **n8n**: Workflow orchestration and platform integrations
- **Letta**: Stateful AI agents with memory and learning capabilities
- **PostgreSQL/Airtable**: Content database and performance tracking

### What This System Does

1. **Daily Content Creation**: Generates 2-3 social media posts automatically
2. **Weekly Newsletter Production**: Researches, drafts, and repurposes newsletters
3. **Content Multiplication**: Creates 60+ derivative assets from one newsletter
4. **Performance Learning**: Continuously improves based on engagement data
5. **Idea Validation**: Automatically validates winning ideas for expansion
6. **Research Synthesis**: Transforms 6+ hours of videos into 1000-word briefs

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────┐
│     CONTENT PLATFORMS                    │
│  Twitter | YouTube | Newsletter | Blog  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        n8n ORCHESTRATION                 │
│  • Daily Content Pipeline                │
│  • Newsletter Production                 │
│  • Content Multiplier                    │
│  • Performance Tracking                  │
│  • Idea Validation                       │
│  • Research Ingestion                    │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        LETTA AI AGENTS                   │
│  • Content Strategist (ideas & planning) │
│  • Research Agent (summarization)        │
│  • Content Generator (writing)           │
│  • Repurposing Agent (derivatives)       │
│  • Performance Analyst (learning)        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        DATA LAYER                        │
│  Ideas | Content | Research | Metrics   │
└─────────────────────────────────────────┘
```

### Key Features

- **Stateful Intelligence**: Agents remember brand voice, performance history, and successful patterns
- **70/30 Strategy**: Auto-balances 70% experimental content with 30% proven formats
- **Feedback Loops**: Performance data continuously improves agent decisions
- **Human-in-the-Loop**: Strategic review gates prevent full automation where needed
- **Platform Aware**: Twitter validates ideas → Newsletter expands winners → YouTube scripts

---

## 📁 Project Structure

```
dk-workflow/
├── README.md                    # Dan Koe's original workflow description
├── ARCHITECTURE.md              # Complete system architecture
├── IMPLEMENTATION_GUIDE.md      # Step-by-step implementation guide
├── SETUP.md                     # Quick setup instructions
├── PROJECT_README.md            # This file
│
├── agents/                      # Letta agent implementations
│   ├── content_generation_agent.py
│   ├── content_strategist_agent.py
│   └── research_synthesis_agent.py
│
├── database/                    # Database schemas
│   ├── schema.sql              # PostgreSQL schema
│   └── airtable-schema.md      # Airtable alternative
│
├── workflows/                   # n8n workflow templates
│   └── daily-content-creation.json
│
├── config/                      # Configuration files
│   └── .env.example            # Environment template
│
├── scripts/                     # Setup and utility scripts
│   └── setup.sh                # Automated setup script
│
└── requirements.txt             # Python dependencies
```

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd dk-workflow

# Run automated setup
./scripts/setup.sh
```

The setup script will:
- Install dependencies
- Set up database
- Create Letta agents
- Configure n8n
- Test connections

**For detailed setup instructions, see [SETUP.md](./SETUP.md)**

### 2. Configure Environment

Edit `config/.env` with your API keys:
- Twitter/X API credentials
- LLM provider (Claude, GPT-4, or Gemini)
- Email platform (ConvertKit, Beehiiv, etc.)
- Slack webhooks for notifications
- Database credentials

### 3. Import Workflows

1. Open n8n at http://localhost:5678
2. Import workflows from `workflows/` directory
3. Configure credentials in n8n
4. Activate workflows

### 4. Test

Run the Daily Content Creation workflow manually to verify everything works.

---

## 📊 Expected Results

### Efficiency Gains

| Task | Before | After | Time Saved |
|------|--------|-------|------------|
| Research | 6+ hours | 30 minutes | ~5.5 hours |
| Newsletter Writing | 4 hours | 2 hours | 2 hours |
| Daily Posts | 60 minutes | 15 minutes | 45 minutes |
| Repurposing | 2 hours | 5 min (review) | ~2 hours |
| **Weekly Total** | **~20 hours** | **~4 hours** | **16 hours** |

### Quality Metrics

- **Engagement Rate**: Maintained or improved (data-driven approach)
- **Brand Voice Consistency**: 95%+ (agent memory ensures consistency)
- **Content Velocity**: 3x increase in output
- **Idea Validation Rate**: Track percentage of tested ideas that perform

---

## 🔧 Core Workflows

### 1. Daily Content Creation

**Trigger**: 6 AM daily

**Process**:
1. Strategist Agent analyzes last week's performance
2. Recommends 3 posts (2 experimental, 1 proven)
3. Content Agent generates posts
4. Human review via Slack
5. Auto-publish to Twitter

**Output**: 2-3 high-quality posts published daily

---

### 2. Weekly Newsletter

**Trigger**: Monday 8 AM

**Process**:
1. Strategist identifies validated topic from Twitter
2. Research Agent processes source materials (videos, articles)
3. Generates 1000-word actionable summary
4. Content Agent drafts newsletter
5. Human review and edit
6. Publish + trigger multiplier workflow

**Output**: One newsletter + 60+ derivative assets

---

### 3. Content Multiplier

**Trigger**: Newsletter publication

**Process**:
1. Extract newsletter content
2. Generate 20-30 YouTube titles
3. Create 15 "deep post" elements
4. Produce 60 new content ideas
5. Save all to content bank

**Output**: Content bank populated for weeks

---

### 4. Performance Tracking

**Trigger**: 11 PM daily

**Process**:
1. Collect metrics from all platforms
2. Update agent memories with performance data
3. Validate high-performing ideas
4. Flag plateauing templates
5. Generate daily insights report

**Output**: Continuously improving system

---

## 📖 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Complete system design with all agents and workflows
- **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)**: Phase-by-phase implementation instructions
- **[SETUP.md](./SETUP.md)**: Quick start setup guide
- **[README.md](./README.md)**: Dan Koe's original workflow description

---

## 🎯 Use Cases

This system works for:

- **Content Creators**: Scale content production 3-10x
- **Solopreneurs**: Automate marketing while maintaining authenticity
- **Newsletter Writers**: Research and draft workflows
- **Course Creators**: Repurpose content across formats
- **Agencies**: Template for client content systems

---

## 🔐 Security & Privacy

- All API keys stored in environment variables
- Database credentials never committed to git
- Optional: Self-host all components for complete data control
- Agent memory can be cleared/reset at any time
- Human review gates prevent unwanted auto-posting

---

## 💰 Cost Estimation

### Monthly Costs (approximate)

- **LLM API** (Claude/GPT-4): $50-200/month depending on volume
- **n8n**: Free (self-hosted) or $20-100/month (cloud)
- **Letta**: Free (open source)
- **Database**: $0 (local) to $25/month (managed)
- **Platform APIs**: Mostly free tier
- **Total**: $50-325/month

**ROI**: 16 hours/week saved @ $100/hr = $6,400/month value

---

## 🛣️ Roadmap

### Phase 1: MVP (Current)
- [x] Core agents (Strategist, Generator, Research)
- [x] Daily content pipeline
- [x] Database schemas
- [x] Setup automation

### Phase 2: Enhancement
- [ ] Newsletter production workflow
- [ ] Content multiplier workflow
- [ ] Performance analysis agent
- [ ] Repurposing agent

### Phase 3: Advanced
- [ ] Visual content generation
- [ ] Video editing automation
- [ ] Multi-author collaboration
- [ ] A/B testing framework

### Phase 4: Intelligence
- [ ] Fine-tuned models on your content
- [ ] Predictive analytics
- [ ] Self-improving prompts
- [ ] Advanced pattern recognition

---

## 🤝 Contributing

This is a template system. To adapt for your own use:

1. **Customize Agent Personas**: Edit brand voice in `agents/*.py`
2. **Adjust Workflows**: Modify n8n workflows for your platforms
3. **Update Templates**: Add your swipe file templates to database
4. **Configure Ratios**: Adjust experimental/proven ratio in `.env`

---

## 📝 License

MIT License - Use freely, attribution appreciated.

---

## 🙏 Credits

- **Original Workflow**: [Dan Koe](https://www.youtube.com/watch?v=HhspudqFSvU)
- **n8n**: Workflow automation platform
- **Letta**: Stateful AI agent framework
- **Architecture & Implementation**: This project

---

## 📞 Support

- **Documentation**: See files above
- **Issues**: Open a GitHub issue
- **Questions**: Check SETUP.md and IMPLEMENTATION_GUIDE.md

---

**Built to help creators scale without losing their voice.** 🚀

Transform hours of manual work into minutes of strategic review while maintaining quality, authenticity, and continuous improvement through data-driven learning.
