# Airtable Schema for Dan Koe Content Workflow

This document describes the Airtable base structure as an alternative to PostgreSQL.

## Base Setup

Create a new Airtable base called **"Dan Koe Content Workflow"**

---

## Tables

### 1. Ideas Database

**Fields:**
- `ID` - Auto number (automatically generated)
- `Topic` - Single line text (required)
- `Angle` - Long text
- `Source` - Single select (Twitter, YouTube, Manual, Research)
- `Validation Status` - Single select (Pending, Validated, Used, Rejected)
- `Performance Score` - Number (decimal, 0-100)
- `Source Content ID` - Single line text
- `Notes` - Long text
- `Tags` - Multiple select
- `Related Content` - Link to Content Archive (multiple)
- `Created` - Created time
- `Validated At` - Date with time
- `Used At` - Date with time
- `Last Modified` - Last modified time

**Views:**
- All Ideas
- Validated & Ready
- Pending Validation
- Used Ideas
- By Performance Score (sorted desc)

---

### 2. Content Archive

**Fields:**
- `ID` - Auto number
- `Type` - Single select (Newsletter, Tweet, YouTube, Blog, LinkedIn, Deep Post)
- `Title` - Single line text
- `Content` - Long text (required)
- `Summary` - Long text
- `Published At` - Date with time
- `Platform ID` - Single line text
- `Platform URL` - URL
- `Views` - Number
- `Likes` - Number
- `Shares` - Number
- `Comments` - Number
- `Engagement Rate` - Percent (calculated or manual)
- `Format Type` - Single select (Experimental, Proven, Hybrid)
- `Template` - Link to Swipe File (single)
- `Derived From` - Link to Content Archive (single)
- `Tags` - Multiple select
- `Created` - Created time
- `Last Modified` - Last modified time

**Views:**
- All Content
- By Type (grouped by Type)
- Top Performers (sorted by Engagement Rate desc)
- Recent (sorted by Published At desc)
- Experimental vs Proven (grouped by Format Type)
- Newsletter Archive
- Tweet Archive

**Formulas:**
- Engagement Rate (if not auto-calculated): `(Likes + Shares + Comments) / Views * 100`

---

### 3. Swipe File

**Fields:**
- `ID` - Auto number
- `Name` - Single line text (required)
- `Description` - Long text
- `Structure` - Long text (required) - The template pattern
- `Psychology Notes` - Long text
- `Example Content` - Link to Content Archive (multiple)
- `Category` - Single select (Paradox, Framework, Story, Question, List, Other)
- `Platform` - Single select (Twitter, Newsletter, YouTube, LinkedIn, All)
- `Avg Engagement` - Number (decimal)
- `Use Count` - Number
- `Last Used` - Date with time
- `Plateau Detected` - Checkbox
- `Meta Prompt` - Long text
- `Is Active` - Checkbox (default: true)
- `Created` - Created time
- `Last Modified` - Last modified time

**Views:**
- All Templates
- Active Templates (filtered: Is Active = true)
- By Category (grouped by Category)
- By Performance (sorted by Avg Engagement desc)
- Plateaued Templates (filtered: Plateau Detected = true)
- Twitter Templates
- Newsletter Templates

---

### 4. Research Notes

**Fields:**
- `ID` - Auto number
- `Title` - Single line text (required)
- `Source Type` - Single select (YouTube, Article, Book, Podcast, Paper, Other)
- `Source URL` - URL
- `Author` - Single line text
- `Duration/Length` - Single line text
- `Publish Date` - Date
- `Original Content` - Long text (full transcript)
- `Summary` - Long text (required)
- `Key Insights` - Long text (bullet points)
- `Quotes` - Long text
- `Related Topics` - Multiple select
- `Comparison Notes` - Long text
- `Actionable Items` - Long text (checklist)
- `Used In Content` - Link to Content Archive (multiple)
- `Tags` - Multiple select
- `Created` - Created time
- `Last Modified` - Last modified time

**Views:**
- All Research
- By Source Type (grouped)
- Recent Research (sorted by Created desc)
- Unused Research (filtered: Used In Content is empty)
- By Topic (grouped by Related Topics)

---

### 5. Content Queue

**Fields:**
- `ID` - Auto number
- `Type` - Single select (Newsletter, Tweet, YouTube, Blog, LinkedIn)
- `Title` - Single line text
- `Content` - Long text (required)
- `Platform` - Single select (Twitter, YouTube, Email, Blog, LinkedIn)
- `Scheduled For` - Date with time
- `Status` - Single select (Draft, Approved, Scheduled, Published, Failed, Rejected)
- `Idea` - Link to Ideas Database (single)
- `Template` - Link to Swipe File (single)
- `Approval Notes` - Long text
- `Created By` - Single select (System, Content Strategist, Manual)
- `Created` - Created time
- `Last Modified` - Last modified time
- `Published At` - Date with time

**Views:**
- All Queued Content
- Needs Approval (filtered: Status = Draft)
- Scheduled (filtered: Status = Scheduled, sorted by Scheduled For)
- Published (filtered: Status = Published)
- Failed (filtered: Status = Failed)
- This Week (filtered: Scheduled For within this week)

**Automations:**
- When Status → Published, copy to Content Archive
- Send Slack notification when Status → Approved
- Alert if Scheduled For is past and Status ≠ Published

---

### 6. Performance Metrics (Optional - for detailed tracking)

**Fields:**
- `ID` - Auto number
- `Content` - Link to Content Archive (single, required)
- `Timestamp` - Date with time
- `Views` - Number
- `Likes` - Number
- `Shares` - Number
- `Comments` - Number
- `Clicks` - Number
- `Engagement Rate` - Percent
- `Follower Growth` - Number
- `Created` - Created time

**Views:**
- All Metrics
- By Content (grouped by Content)
- Recent (sorted by Timestamp desc)
- Daily Snapshots (grouped by Timestamp)

**Note:** This table is for time-series data if you want to track metrics over time. For simpler setups, just store latest metrics in Content Archive.

---

### 7. Workflow Executions (Audit Log)

**Fields:**
- `ID` - Auto number
- `Workflow Name` - Single select (Daily Content, Newsletter, Multiplier, etc.)
- `Execution ID` - Single line text (from n8n)
- `Status` - Single select (Running, Success, Failed, Cancelled)
- `Start Time` - Date with time (required)
- `End Time` - Date with time
- `Duration (seconds)` - Number (formula: `DATETIME_DIFF(End Time, Start Time, 'seconds')`)
- `Error Message` - Long text
- `Created` - Created time

**Views:**
- All Executions
- Recent (sorted by Start Time desc)
- Failed (filtered: Status = Failed)
- By Workflow (grouped by Workflow Name)
- Success Rate (by Workflow Name)

---

### 8. Agent Interactions (Optional - for debugging)

**Fields:**
- `ID` - Auto number
- `Agent Name` - Single select (Content Strategist, Research Agent, etc.)
- `Interaction Type` - Single select (Content Gen, Research, Analysis, etc.)
- `Input` - Long text (required)
- `Output` - Long text
- `Tools Used` - Multiple select
- `Tokens Used` - Number
- `Cost (USD)` - Currency
- `Duration (sec)` - Number (decimal)
- `Status` - Single select (Success, Failed)
- `Created` - Created time

**Views:**
- All Interactions
- Recent (sorted by Created desc)
- By Agent (grouped by Agent Name)
- Failed (filtered: Status = Failed)
- Cost Analysis (sum of Cost)

---

## Airtable Automations

Set up these automations within Airtable:

### 1. **Idea Validation Trigger**
- **When:** Record matches conditions (Content Archive)
- **Conditions:** Engagement Rate > 5% AND Type = Tweet
- **Actions:**
  1. Find matching idea in Ideas Database (by content similarity or manual link)
  2. Update Validation Status → Validated
  3. Set Performance Score = Engagement Rate
  4. Send Slack notification

### 2. **Content Publishing**
- **When:** Record matches conditions (Content Queue)
- **Conditions:** Status changed to Published
- **Actions:**
  1. Create record in Content Archive
  2. Update linked Idea → Used
  3. Update Template Use Count +1
  4. Send notification

### 3. **Review Reminder**
- **When:** Record matches conditions (Content Queue)
- **Conditions:** Status = Draft AND Created > 1 hour ago
- **Actions:**
  1. Send Slack message to #content-review
  2. Or send email notification

### 4. **Failed Workflow Alert**
- **When:** Record created (Workflow Executions)
- **Conditions:** Status = Failed
- **Actions:**
  1. Send urgent Slack alert
  2. Tag @team in notification

---

## Integration with n8n

**Airtable API in n8n:**

1. **Get API Key:**
   - Go to https://airtable.com/account
   - Generate Personal Access Token

2. **In n8n:**
   - Add Airtable credentials
   - Use "Airtable" node for operations

3. **Common Operations:**
   - `List Records` - Get ideas, content, templates
   - `Create Record` - Add new content to queue
   - `Update Record` - Mark ideas as used, update metrics
   - `Search Records` - Find specific templates or ideas

**Example n8n Airtable Node Config:**
```json
{
  "operation": "list",
  "base": "appXXXXXXXXXXXXXX",
  "table": "Ideas Database",
  "options": {
    "filterByFormula": "AND({Validation Status} = 'validated', {Used At} = BLANK())",
    "maxRecords": 5,
    "sort": [{"field": "Performance Score", "direction": "desc"}]
  }
}
```

---

## Airtable Interfaces (Dashboards)

Create these interfaces for easy management:

### 1. **Content Dashboard**
- Widget: Calendar view of Content Queue (by Scheduled For)
- Widget: List of "Needs Approval" items
- Widget: Bar chart of content by type (this week)
- Widget: Performance metrics (avg engagement by type)

### 2. **Ideas Management**
- Widget: Kanban board (columns: Pending, Validated, Used)
- Widget: List of top validated ideas
- Widget: Timeline of idea creation

### 3. **Analytics Dashboard**
- Widget: Line chart - Engagement rate over time
- Widget: Top performing content (last 30 days)
- Widget: Template performance comparison
- Widget: Workflow execution success rate

---

## Data Import

To get started quickly, import sample data:

1. **Download** the CSV templates from `/database/airtable-sample-data/`
2. **Import** to each table in Airtable
3. **Configure** relationships between tables
4. **Set up** automations

---

## Tips for Airtable Setup

1. **Use Color Coding:**
   - Status fields: Green for approved, red for failed, yellow for pending
   - Performance: Color scale on engagement rate

2. **Leverage Formulas:**
   - Auto-calculate engagement rates
   - Duration between dates
   - Status indicators

3. **Set Field Descriptions:**
   - Add descriptions to complex fields
   - Document what each field is for

4. **Create Forms:**
   - Manual idea entry form
   - Research note submission form
   - Content approval form

5. **Sync with Calendar:**
   - Sync Content Queue to Google Calendar
   - See scheduled posts in your calendar app

---

## Limitations vs PostgreSQL

**Airtable Pros:**
- Visual interface, no SQL needed
- Built-in automations
- Easy to share/collaborate
- Mobile app for on-the-go management

**Airtable Cons:**
- Record limits on free plan (1,200 per base)
- Less powerful querying
- No vector embeddings for agent memory
- API rate limits (5 requests/second)

**Recommendation:** Start with Airtable for MVP, migrate to PostgreSQL if you need:
- More than 10,000 records
- Complex queries and joins
- Vector search for AI memory
- Higher API throughput
