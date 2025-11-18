-- Dan Koe Content Workflow Database Schema
-- PostgreSQL Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- IDEAS DATABASE
-- ============================================================================
CREATE TABLE IF NOT EXISTS ideas_database (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic VARCHAR(500) NOT NULL,
    angle TEXT,
    source VARCHAR(50) CHECK (source IN ('twitter', 'youtube', 'manual', 'research')),
    validation_status VARCHAR(20) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'used', 'rejected')),
    performance_score DECIMAL(5,2) DEFAULT 0.0,
    source_content_id VARCHAR(255), -- Link to original tweet/video
    notes TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    related_content_ids JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP WITH TIME ZONE,
    used_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ideas_validation_status ON ideas_database(validation_status);
CREATE INDEX idx_ideas_performance_score ON ideas_database(performance_score DESC);
CREATE INDEX idx_ideas_created_at ON ideas_database(created_at DESC);
CREATE INDEX idx_ideas_tags ON ideas_database USING GIN(tags);

-- ============================================================================
-- CONTENT ARCHIVE
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_archive (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL CHECK (type IN ('newsletter', 'tweet', 'youtube', 'blog', 'linkedin', 'deep_post')),
    title VARCHAR(500),
    content TEXT NOT NULL,
    summary TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    platform_id VARCHAR(255), -- External ID from platform (tweet ID, etc.)
    platform_url TEXT,
    performance JSONB DEFAULT '{}'::jsonb, -- {views, likes, shares, engagement_rate, etc.}
    format_type VARCHAR(20) CHECK (format_type IN ('experimental', 'proven', 'hybrid')),
    template_id UUID, -- Reference to swipe_file
    derived_from UUID, -- Reference to parent content
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_content_type ON content_archive(type);
CREATE INDEX idx_content_published_at ON content_archive(published_at DESC);
CREATE INDEX idx_content_format_type ON content_archive(format_type);
CREATE INDEX idx_content_tags ON content_archive USING GIN(tags);
CREATE INDEX idx_content_performance ON content_archive USING GIN(performance);

-- ============================================================================
-- SWIPE FILE (Templates & Patterns)
-- ============================================================================
CREATE TABLE IF NOT EXISTS swipe_file (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    structure TEXT NOT NULL, -- The template structure/pattern
    psychology_notes TEXT, -- Why this works (hooks, frameworks, etc.)
    example_content_ids JSONB DEFAULT '[]'::jsonb, -- Array of content_archive IDs
    category VARCHAR(100), -- e.g., 'paradox', 'framework', 'story', 'question'
    platform VARCHAR(50), -- Which platform this works best on
    performance_history JSONB DEFAULT '{}'::jsonb, -- {avg_engagement, use_count, last_used, plateau_detected}
    meta_prompt TEXT, -- The prompt used to apply this template
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_swipe_category ON swipe_file(category);
CREATE INDEX idx_swipe_platform ON swipe_file(platform);
CREATE INDEX idx_swipe_is_active ON swipe_file(is_active);

-- ============================================================================
-- RESEARCH NOTES
-- ============================================================================
CREATE TABLE IF NOT EXISTS research_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    source_type VARCHAR(50) CHECK (source_type IN ('youtube', 'article', 'book', 'podcast', 'paper', 'other')),
    source_url TEXT,
    source_metadata JSONB DEFAULT '{}'::jsonb, -- {author, duration, publish_date, etc.}
    original_content TEXT, -- Full transcript or original text
    summary TEXT NOT NULL, -- AI-generated summary
    key_insights JSONB DEFAULT '[]'::jsonb, -- Array of key takeaways
    quotes JSONB DEFAULT '[]'::jsonb, -- Notable quotes
    related_topics JSONB DEFAULT '[]'::jsonb,
    comparison_notes TEXT, -- How this compares to existing knowledge
    actionable_items JSONB DEFAULT '[]'::jsonb,
    used_in_content_ids JSONB DEFAULT '[]'::jsonb, -- Which content pieces used this research
    tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_research_source_type ON research_notes(source_type);
CREATE INDEX idx_research_created_at ON research_notes(created_at DESC);
CREATE INDEX idx_research_tags ON research_notes USING GIN(tags);

-- ============================================================================
-- AGENT MEMORY STORE
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    memory_type VARCHAR(50) CHECK (memory_type IN ('core', 'archival', 'recall', 'config')),
    memory_key VARCHAR(255),
    memory_content JSONB NOT NULL,
    embedding VECTOR(1536), -- For vector search (if using pgvector)
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_memory_agent_id ON agent_memory(agent_id);
CREATE INDEX idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX idx_agent_memory_key ON agent_memory(agent_name, memory_key);

-- ============================================================================
-- PERFORMANCE METRICS (Time-series data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_archive(id) ON DELETE CASCADE,
    metric_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,4),
    follower_growth INTEGER DEFAULT 0,
    custom_metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_content_id ON performance_metrics(content_id);
CREATE INDEX idx_metrics_timestamp ON performance_metrics(metric_timestamp DESC);

-- ============================================================================
-- CONTENT QUEUE (Scheduled/Draft content)
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    title VARCHAR(500),
    platform VARCHAR(50),
    scheduled_for TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'scheduled', 'published', 'failed', 'rejected')),
    idea_id UUID REFERENCES ideas_database(id),
    template_id UUID REFERENCES swipe_file(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    approval_notes TEXT,
    created_by VARCHAR(100) DEFAULT 'system', -- 'system' or agent name
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_queue_status ON content_queue(status);
CREATE INDEX idx_queue_scheduled_for ON content_queue(scheduled_for);
CREATE INDEX idx_queue_platform ON content_queue(platform);

-- ============================================================================
-- WORKFLOW EXECUTIONS (Audit log)
-- ============================================================================
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_name VARCHAR(255) NOT NULL,
    execution_id VARCHAR(255), -- n8n execution ID
    status VARCHAR(50) CHECK (status IN ('running', 'success', 'failed', 'cancelled')),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_executions_workflow ON workflow_executions(workflow_name);
CREATE INDEX idx_executions_status ON workflow_executions(status);
CREATE INDEX idx_executions_start_time ON workflow_executions(start_time DESC);

-- ============================================================================
-- AGENT INTERACTIONS (Conversational log)
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(100), -- e.g., 'content_generation', 'research', 'analysis'
    input_message TEXT NOT NULL,
    output_message TEXT,
    tools_used JSONB DEFAULT '[]'::jsonb,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    duration_seconds DECIMAL(10,3),
    status VARCHAR(50),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interactions_agent_id ON agent_interactions(agent_id);
CREATE INDEX idx_interactions_type ON agent_interactions(interaction_type);
CREATE INDEX idx_interactions_created_at ON agent_interactions(created_at DESC);

-- ============================================================================
-- TRIGGERS for updated_at timestamps
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ideas_updated_at BEFORE UPDATE ON ideas_database
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON content_archive
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_swipe_updated_at BEFORE UPDATE ON swipe_file
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_research_updated_at BEFORE UPDATE ON research_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_memory_updated_at BEFORE UPDATE ON agent_memory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_queue_updated_at BEFORE UPDATE ON content_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS for common queries
-- ============================================================================

-- View: Top performing content by type
CREATE OR REPLACE VIEW top_performing_content AS
SELECT
    type,
    title,
    content,
    published_at,
    (performance->>'engagement_rate')::float as engagement_rate,
    (performance->>'views')::int as views,
    (performance->>'likes')::int as likes,
    format_type,
    tags
FROM content_archive
WHERE published_at IS NOT NULL
ORDER BY (performance->>'engagement_rate')::float DESC NULLS LAST;

-- View: Validated ideas ready to use
CREATE OR REPLACE VIEW ready_ideas AS
SELECT
    id,
    topic,
    angle,
    source,
    performance_score,
    tags,
    created_at
FROM ideas_database
WHERE validation_status = 'validated'
ORDER BY performance_score DESC, created_at DESC;

-- View: Active templates by performance
CREATE OR REPLACE VIEW active_templates AS
SELECT
    id,
    name,
    category,
    platform,
    (performance_history->>'avg_engagement')::float as avg_engagement,
    (performance_history->>'use_count')::int as use_count,
    (performance_history->>'plateau_detected')::boolean as plateau_detected,
    is_active
FROM swipe_file
WHERE is_active = true
ORDER BY (performance_history->>'avg_engagement')::float DESC NULLS LAST;

-- View: Recent workflow performance
CREATE OR REPLACE VIEW recent_workflow_stats AS
SELECT
    workflow_name,
    COUNT(*) as total_runs,
    COUNT(*) FILTER (WHERE status = 'success') as successful_runs,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_runs,
    AVG(duration_seconds) as avg_duration_seconds,
    MAX(start_time) as last_run
FROM workflow_executions
WHERE start_time > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY workflow_name
ORDER BY last_run DESC;

-- ============================================================================
-- SEED DATA (Optional starter templates)
-- ============================================================================

-- Insert sample swipe file templates
INSERT INTO swipe_file (name, description, structure, psychology_notes, category, platform, meta_prompt) VALUES
(
    'Paradox Hook',
    'Start with a counterintuitive statement that challenges conventional wisdom',
    'The paradox of [TOPIC]: The less you [ACTION A], the more you [RESULT B]. [EXPLANATION]',
    'Paradoxes create cognitive dissonance and curiosity. They force the reader to stop and think, increasing engagement.',
    'paradox',
    'twitter',
    'Create a paradox-based post about {topic}. Structure: Start with "The paradox of [topic]:" then present a counterintuitive truth. Keep it punchy and thought-provoking.'
),
(
    'Framework/System',
    'Present a simple numbered framework or system',
    'The [NUMBER]-step [SYSTEM NAME] for [DESIRED OUTCOME]:\n\n1. [STEP 1]\n2. [STEP 2]\n3. [STEP 3]\n\nMost people skip step [X]. Don't.',
    'Frameworks provide mental models and actionable structure. The numbered format makes it scannable and shareable.',
    'framework',
    'twitter',
    'Create a framework post about {topic}. Present 3-5 steps in a system. End with insight about which step people commonly miss.'
),
(
    'Personal Story Arc',
    'Share a personal transformation with lesson',
    '[TIME] ago, I [PAST STATE].\n\nToday, I [CURRENT STATE].\n\nWhat changed:\n[KEY INSIGHT/LESSON]',
    'Personal stories create relatability and social proof. The before/after structure shows transformation is possible.',
    'story',
    'twitter',
    'Create a personal story post about {topic}. Use before/after structure and end with the key lesson learned.'
),
(
    'Question Thread Starter',
    'Provocative question that opens a thread',
    'Why do [MOST PEOPLE] [COMMON BEHAVIOR] when [OPPOSITE APPROACH] gets [BETTER RESULT]?\n\nA thread on [TOPIC]:',
    'Questions engage the reader's curiosity and prime them to keep reading for the answer.',
    'question',
    'twitter',
    'Create a provocative question about {topic} that challenges common behavior. Set up a thread format.'
);

-- ============================================================================
-- FUNCTIONS for common operations
-- ============================================================================

-- Function: Mark idea as validated
CREATE OR REPLACE FUNCTION validate_idea(idea_uuid UUID, score DECIMAL)
RETURNS VOID AS $$
BEGIN
    UPDATE ideas_database
    SET validation_status = 'validated',
        validated_at = CURRENT_TIMESTAMP,
        performance_score = score
    WHERE id = idea_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function: Get next content recommendations
CREATE OR REPLACE FUNCTION get_content_recommendations(
    experimental_count INT DEFAULT 2,
    proven_count INT DEFAULT 1
)
RETURNS TABLE (
    idea_id UUID,
    idea_topic VARCHAR,
    idea_angle TEXT,
    template_id UUID,
    template_name VARCHAR,
    recommendation_type VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    -- Proven content (high-performing templates with validated ideas)
    (
        SELECT
            i.id,
            i.topic,
            i.angle,
            s.id,
            s.name,
            'proven'::VARCHAR as recommendation_type
        FROM ideas_database i
        CROSS JOIN swipe_file s
        WHERE i.validation_status = 'validated'
        AND s.is_active = true
        AND (s.performance_history->>'plateau_detected')::boolean = false
        ORDER BY
            i.performance_score DESC,
            (s.performance_history->>'avg_engagement')::float DESC
        LIMIT proven_count
    )
    UNION ALL
    -- Experimental content (new templates or unvalidated ideas)
    (
        SELECT
            i.id,
            i.topic,
            i.angle,
            s.id,
            s.name,
            'experimental'::VARCHAR as recommendation_type
        FROM ideas_database i
        CROSS JOIN swipe_file s
        WHERE i.validation_status = 'pending'
        AND s.is_active = true
        ORDER BY RANDOM()
        LIMIT experimental_count
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS (Adjust based on your user setup)
-- ============================================================================
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_user;
