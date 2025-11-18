#!/bin/bash

# Dan Koe Content Workflow - Setup Script
# This script sets up the entire workflow infrastructure

set -e  # Exit on error

echo "=========================================="
echo "Dan Koe Content Workflow - Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if .env exists
if [ ! -f "config/.env" ]; then
    print_info "Creating .env file from template..."
    cp config/.env.example config/.env
    print_success ".env file created"
    print_info "Please edit config/.env with your API keys before continuing"
    read -p "Press enter when you've configured your .env file..."
fi

# Load environment variables
export $(cat config/.env | grep -v '^#' | xargs)

echo ""
echo "Step 1: Installing Python dependencies"
echo "----------------------------------------"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

python3 -m pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

echo ""
echo "Step 2: Database Setup"
echo "----------------------------------------"

read -p "Are you using PostgreSQL (p) or Airtable (a)? [p/a]: " db_choice

if [ "$db_choice" = "p" ] || [ "$db_choice" = "P" ]; then
    print_info "Setting up PostgreSQL database..."

    # Check if PostgreSQL is installed
    if ! command -v psql &> /dev/null; then
        print_error "PostgreSQL is not installed. Installing via Docker..."

        docker run --name content-workflow-db \
            -e POSTGRES_PASSWORD=$DB_PASSWORD \
            -e POSTGRES_DB=$DB_NAME \
            -p 5432:5432 \
            -d postgres:16

        sleep 5  # Wait for postgres to start
    fi

    # Run schema
    print_info "Creating database schema..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/schema.sql
    print_success "Database schema created"

elif [ "$db_choice" = "a" ] || [ "$db_choice" = "A" ]; then
    print_info "Using Airtable - please ensure you've set up your base"
    print_info "Follow instructions in database/airtable-schema.md"
    print_success "Airtable configuration noted"
else
    print_error "Invalid choice. Please run the script again."
    exit 1
fi

echo ""
echo "Step 3: Letta Setup"
echo "----------------------------------------"

if ! command -v letta &> /dev/null; then
    print_info "Letta is not installed. Installing..."
    pip install letta
fi

print_info "Configuring Letta..."
letta configure

print_info "Starting Letta server..."
letta server &
LETTA_PID=$!
sleep 5

print_success "Letta server started (PID: $LETTA_PID)"

echo ""
echo "Step 4: Creating Letta Agents"
echo "----------------------------------------"

print_info "Creating Content Generation Agent..."
AGENT1_OUTPUT=$(python3 agents/content_generation_agent.py)
AGENT1_ID=$(echo "$AGENT1_OUTPUT" | grep "Agent ID:" | awk '{print $3}')
print_success "Content Generation Agent created: $AGENT1_ID"

print_info "Creating Content Strategist Agent..."
AGENT2_OUTPUT=$(python3 agents/content_strategist_agent.py)
AGENT2_ID=$(echo "$AGENT2_OUTPUT" | grep "Agent ID:" | awk '{print $3}')
print_success "Content Strategist Agent created: $AGENT2_ID"

print_info "Creating Research & Synthesis Agent..."
AGENT3_OUTPUT=$(python3 agents/research_synthesis_agent.py)
AGENT3_ID=$(echo "$AGENT3_OUTPUT" | grep "Agent ID:" | awk '{print $3}')
print_success "Research & Synthesis Agent created: $AGENT3_ID"

# Update .env with agent IDs
print_info "Updating .env with agent IDs..."
sed -i.bak "s/AGENT_CONTENT_GENERATION_ID=.*/AGENT_CONTENT_GENERATION_ID=$AGENT1_ID/" config/.env
sed -i.bak "s/AGENT_CONTENT_STRATEGIST_ID=.*/AGENT_CONTENT_STRATEGIST_ID=$AGENT2_ID/" config/.env
sed -i.bak "s/AGENT_RESEARCH_SYNTHESIS_ID=.*/AGENT_RESEARCH_SYNTHESIS_ID=$AGENT3_ID/" config/.env
print_success "Agent IDs saved to .env"

echo ""
echo "Step 5: n8n Setup"
echo "----------------------------------------"

read -p "Do you want to start n8n now? [y/n]: " start_n8n

if [ "$start_n8n" = "y" ] || [ "$start_n8n" = "Y" ]; then
    if command -v n8n &> /dev/null; then
        print_info "Starting n8n..."
        n8n start &
        N8N_PID=$!
        sleep 5
        print_success "n8n started (PID: $N8N_PID)"
        print_info "Access n8n at: http://localhost:5678"
    else
        print_info "n8n not found. Installing via Docker..."
        docker run -it --rm \
            --name n8n \
            -p 5678:5678 \
            -v ~/.n8n:/home/node/.n8n \
            -e N8N_BASIC_AUTH_ACTIVE=true \
            -e N8N_BASIC_AUTH_USER=$N8N_BASIC_AUTH_USER \
            -e N8N_BASIC_AUTH_PASSWORD=$N8N_BASIC_AUTH_PASSWORD \
            n8nio/n8n &
        N8N_PID=$!
        sleep 10
        print_success "n8n Docker container started"
        print_info "Access n8n at: http://localhost:5678"
    fi

    print_info "Import workflows from the workflows/ directory"
    print_info "1. Go to http://localhost:5678"
    print_info "2. Click 'Import from File'"
    print_info "3. Select workflows/daily-content-creation.json"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
print_success "All components have been set up successfully!"
echo ""
echo "Next Steps:"
echo "1. Configure your API credentials in n8n"
echo "2. Import workflows from workflows/ directory"
echo "3. Test the Daily Content Creation workflow"
echo "4. Set up Slack notifications"
echo "5. Review and customize agent prompts"
echo ""
echo "Resources:"
echo "- Architecture: ARCHITECTURE.md"
echo "- Implementation Guide: IMPLEMENTATION_GUIDE.md"
echo "- Database Schema: database/schema.sql"
echo ""
echo "Running Services:"
[ ! -z "$LETTA_PID" ] && echo "- Letta Server (PID: $LETTA_PID) - http://localhost:8283"
[ ! -z "$N8N_PID" ] && echo "- n8n (PID: $N8N_PID) - http://localhost:5678"
echo ""
print_info "To stop services: kill $LETTA_PID $N8N_PID"
echo "=========================================="
