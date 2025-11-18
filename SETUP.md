# Setup Guide - Dan Koe Content Workflow

Quick start guide for setting up the complete n8n + Letta content workflow.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Docker** installed (optional, but recommended)
- **PostgreSQL** (or Airtable account)
- **API Keys** for:
  - Twitter/X API
  - Anthropic Claude (or OpenAI/Gemini)
  - YouTube Data API
  - Email platform (ConvertKit, Beehiiv, etc.)
  - Slack (for notifications)

---

## Quick Setup (Automated)

Run the automated setup script:

```bash
# Navigate to project directory
cd dk-workflow

# Run setup script
./scripts/setup.sh
```

The script will:
1. Install Python dependencies
2. Set up database (PostgreSQL or Airtable)
3. Configure and start Letta server
4. Create all Letta agents
5. Start n8n (optional)
6. Save agent IDs to .env file

Follow the prompts and provide your configuration choices.

---

## Manual Setup

If you prefer manual setup or the script fails:

### Step 1: Environment Configuration

```bash
# Copy environment template
cp config/.env.example config/.env

# Edit with your API keys
nano config/.env  # or use your preferred editor
```

Fill in all required API keys and credentials.

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### Step 3: Database Setup

**Option A: PostgreSQL**

```bash
# Start PostgreSQL (Docker)
docker run --name content-workflow-db \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=content_workflow \
  -p 5432:5432 \
  -d postgres:16

# Create schema
psql -h localhost -U postgres -d content_workflow -f database/schema.sql
```

**Option B: Airtable**

1. Go to airtable.com and create a new base
2. Follow instructions in `database/airtable-schema.md`
3. Get your API key from account settings
4. Update `.env` with Airtable credentials

### Step 4: Letta Setup

```bash
# Install Letta
pip install letta

# Configure Letta (choose your LLM provider)
letta configure

# Start Letta server
letta server
# Server will run on http://localhost:8283
```

### Step 5: Create Agents

In separate terminals (or use `&` to run in background):

```bash
# Create Content Generation Agent
python3 agents/content_generation_agent.py
# Note the Agent ID from output

# Create Content Strategist Agent
python3 agents/content_strategist_agent.py
# Note the Agent ID

# Create Research & Synthesis Agent
python3 agents/research_synthesis_agent.py
# Note the Agent ID
```

Update your `.env` file with the agent IDs:

```bash
AGENT_CONTENT_GENERATION_ID=agent_id_here
AGENT_CONTENT_STRATEGIST_ID=agent_id_here
AGENT_RESEARCH_SYNTHESIS_ID=agent_id_here
```

### Step 6: n8n Setup

**Option A: Docker (Recommended)**

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=yourpassword \
  n8nio/n8n
```

**Option B: npm**

```bash
npm install n8n -g
n8n start
```

Access n8n at: **http://localhost:5678**

### Step 7: Import Workflows

1. Open n8n at http://localhost:5678
2. Click **"Import from File"** or **"+"** → **"Import from File"**
3. Navigate to `workflows/` directory
4. Import `daily-content-creation.json`

### Step 8: Configure n8n Credentials

In n8n, set up credentials for:

1. **Letta API** (HTTP Header Auth)
   - Header Name: `Authorization`
   - Header Value: `Bearer YOUR_LETTA_API_KEY`

2. **Twitter/X** (OAuth 2.0)
   - Use Twitter API v2 credentials

3. **Airtable** (Token API)
   - Use your Airtable Personal Access Token

4. **Slack** (OAuth 2.0)
   - Connect your Slack workspace
   - Create channels: `#content-review` and `#alerts`

### Step 9: Test the Workflow

1. In n8n, open the "Daily Content Creation Pipeline" workflow
2. Click **"Execute Workflow"** to run manually
3. Check that:
   - Agents respond correctly
   - Slack notifications arrive
   - Content is saved to database
4. Review the output at each node

---

## Verification Checklist

After setup, verify everything is working:

- [ ] Letta server is running (http://localhost:8283)
- [ ] n8n is running (http://localhost:5678)
- [ ] Database is accessible (PostgreSQL or Airtable)
- [ ] All 3 agents created successfully
- [ ] Agent IDs saved in `.env` file
- [ ] n8n credentials configured
- [ ] Slack workspace connected
- [ ] Test workflow executes without errors

---

## Testing Individual Components

### Test Letta Agents

```python
from letta import create_client
import os

client = create_client()

# Test Content Generation Agent
response = client.send_message(
    agent_id=os.getenv("AGENT_CONTENT_GENERATION_ID"),
    message="Generate a tweet about AI automation",
    role="user"
)

print(response.messages[-1].text)
```

### Test Database Connection

**PostgreSQL:**

```bash
psql -h localhost -U postgres -d content_workflow -c "SELECT COUNT(*) FROM ideas_database;"
```

**Airtable:**

```bash
curl -X GET https://api.airtable.com/v0/YOUR_BASE_ID/Ideas%20Database \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Test n8n Workflow

1. Open workflow in n8n
2. Click "Execute Workflow"
3. Monitor execution in real-time
4. Check node outputs for errors

---

## Common Issues & Solutions

### Issue: Letta server won't start

**Solution:**
```bash
# Check if port 8283 is in use
lsof -i :8283

# Kill existing process if needed
kill -9 PID

# Restart Letta
letta server
```

### Issue: n8n can't connect to Letta

**Solution:**
- Verify Letta server is running: `curl http://localhost:8283/v1/health`
- Check firewall settings
- Ensure `LETTA_SERVER_URL` in `.env` is correct

### Issue: Database connection fails

**Solution:**
- For PostgreSQL: Check Docker container is running: `docker ps`
- Verify credentials in `.env` match database
- Test connection: `psql -h localhost -U postgres -d content_workflow`

### Issue: Agent creation fails

**Solution:**
- Ensure Letta server is running
- Check LLM API keys are valid
- Review Letta configuration: `letta configure`
- Check error logs in agent script output

### Issue: n8n workflow fails at agent node

**Solution:**
- Verify agent IDs in `.env` are correct
- Check Letta API credentials in n8n
- Test agent manually with Python script
- Review n8n execution logs

---

## Next Steps

Once setup is complete:

1. **Customize Agent Prompts**
   - Edit agent personas in `agents/*.py`
   - Adjust to match your brand voice
   - Re-create agents to apply changes

2. **Add More Workflows**
   - Newsletter Production
   - Content Multiplier
   - Performance Tracking
   - Research Ingestion

3. **Seed Initial Data**
   - Add swipe file templates to database
   - Import past content for analysis
   - Create initial ideas backlog

4. **Configure Scheduling**
   - Set up daily content schedule (6 AM)
   - Configure newsletter schedule (Mondays)
   - Set performance check schedule (11 PM)

5. **Set Up Monitoring**
   - Configure error notifications
   - Set up analytics dashboard
   - Monitor agent costs and token usage

---

## Production Deployment

For production use:

1. **Security**
   - Use environment variables, never hardcode keys
   - Enable n8n basic auth or OAuth
   - Use HTTPS for all endpoints
   - Rotate API keys regularly

2. **Reliability**
   - Set up workflow error handlers
   - Configure retry logic
   - Add health checks and monitoring
   - Back up database regularly

3. **Scaling**
   - Use production database (managed PostgreSQL)
   - Deploy Letta on dedicated server
   - Use n8n Cloud for managed hosting
   - Implement rate limiting

4. **Cost Optimization**
   - Monitor LLM API usage
   - Use caching where possible
   - Choose appropriate model sizes
   - Set budget alerts

---

## Resources

- **Architecture Overview**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Implementation Guide**: [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
- **Database Schema**: [database/schema.sql](./database/schema.sql)
- **Letta Docs**: https://docs.letta.ai/
- **n8n Docs**: https://docs.n8n.io/
- **Original Workflow**: [README.md](./README.md)

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review agent and workflow logs
3. Test components individually
4. Consult documentation links
5. Open an issue in the repository

---

**Ready to automate your content workflow!** 🚀
