# Suna AI - Complete Installation Guide

Suna AI is an open-source generalist AI agent that provides a comprehensive platform for AI-powered automation and assistance. This guide provides accurate, step-by-step instructions for installing and configuring Suna AI.

## 🏗️ Architecture Overview

Suna AI consists of five main components:

1. **Backend API** - Python/FastAPI service for REST endpoints, thread management, and LLM integration
2. **Backend Worker** - Python/Dramatiq worker service for handling agent tasks
3. **Frontend** - Next.js/React application providing the user interface
4. **Agent Docker** - Isolated execution environment for each agent
5. **Supabase Database** - Handles data persistence and authentication

## 📋 Prerequisites

### Required Software

Before starting, ensure you have the following installed:

- **[Docker](https://docs.docker.com/get-docker/)** - For containerized services
- **[Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started)** - For database management
- **[Git](https://git-scm.com/downloads)** - For cloning the repository
- **[Python 3.11](https://www.python.org/downloads/)** - Required for setup scripts

For manual setup, you'll also need:
- **[uv](https://docs.astral.sh/uv/)** - Python package manager
- **[Node.js & npm](https://nodejs.org/en/download/)** - For frontend development

### Required API Keys

#### Essential Services

1. **Supabase Project**
   - Create an account at [Supabase](https://supabase.com/)
   - Create a new project
   - Note: Project URL, anon key, and service role key (found in Project Settings → API)

2. **LLM Provider** (choose at least one):
   - [Anthropic](https://console.anthropic.com/) - Recommended for best performance
   - [OpenAI](https://platform.openai.com/)
   - [Groq](https://console.groq.com/)
   - [OpenRouter](https://openrouter.ai/)
   - [AWS Bedrock](https://aws.amazon.com/bedrock/)

3. **Search and Web Scraping**:
   - [Tavily](https://tavily.com/) - For enhanced search capabilities
   - [Firecrawl](https://firecrawl.dev/) - For web scraping capabilities

4. **Agent Execution**:
   - [Daytona](https://app.daytona.io/) - For secure agent execution

5. **Background Job Processing**:
   - [QStash](https://console.upstash.com/qstash) - For workflows, automated tasks, and webhook handling

#### Optional Services

- **RapidAPI** - For accessing additional API services (enables LinkedIn scraping and other tools)
- **Smithery** - For custom agents and workflows ([Get API key](https://smithery.ai/))

## 🚀 Installation Methods

### Method 1: Automated Setup (Recommended)

The easiest way to install Suna AI is using the automated setup wizard:

#### Step 1: Clone the Repository

```bash
git clone https://github.com/kortix-ai/suna.git
cd suna
```

#### Step 2: Run the Setup Wizard

```bash
python setup.py
```

The setup wizard will:
- Check if all required tools are installed
- Collect your API keys and configuration information
- Set up the Supabase database
- Configure environment files
- Install dependencies
- Start Suna using your preferred method

**Features of the Setup Wizard:**
- 14 guided steps with progress saving
- Resume capability if interrupted
- Automatic validation of API keys
- Choice between Docker and manual setup

#### Step 3: Complete Supabase Configuration

During setup, you'll need to:
1. Log in to the Supabase CLI
2. Link your local project to your Supabase project
3. Push database migrations
4. **Important**: Manually expose the 'basejump' schema in Supabase:
   - Go to your Supabase project dashboard
   - Navigate to Project Settings → API
   - Add 'basejump' to the Exposed Schema section

#### Step 4: Configure Daytona

Create a Daytona Snapshot with these settings:
- **Name**: `kortix/suna:0.1.3`
- **Image name**: `kortix/suna:0.1.3`
- **Entrypoint**: `/usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf`

### Method 2: Manual Setup

If you prefer manual configuration or need to customize the installation:

#### Step 1: Clone and Prepare

```bash
git clone https://github.com/kortix-ai/suna.git
cd suna
```

#### Step 2: Configure Backend Environment

Create `backend/.env` with the following configuration:

```env
# Environment Mode
ENV_MODE=local

# DATABASE
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# REDIS
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=false

# RABBITMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# LLM Providers
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key
MODEL_TO_USE=anthropic/claude-sonnet-4-20250514

# WEB SEARCH
TAVILY_API_KEY=your-tavily-key

# WEB SCRAPE
FIRECRAWL_API_KEY=your-firecrawl-key
FIRECRAWL_URL=https://api.firecrawl.dev

# Sandbox container provider
DAYTONA_API_KEY=your-daytona-key
DAYTONA_SERVER_URL=https://app.daytona.io/api
DAYTONA_TARGET=us

# Background job processing (Required)
QSTASH_URL=https://qstash.upstash.io
QSTASH_TOKEN=your-qstash-token
QSTASH_CURRENT_SIGNING_KEY=your-current-signing-key
QSTASH_NEXT_SIGNING_KEY=your-next-signing-key
WEBHOOK_BASE_URL=https://yourdomain.com

# MCP Configuration
MCP_CREDENTIAL_ENCRYPTION_KEY=your-generated-encryption-key

# Optional APIs
RAPID_API_KEY=your-rapidapi-key
SMITHERY_API_KEY=your-smithery-key

NEXT_PUBLIC_URL=http://localhost:3000
```

#### Step 3: Configure Frontend Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/api
NEXT_PUBLIC_URL=http://localhost:3000
NEXT_PUBLIC_ENV_MODE=LOCAL
```

#### Step 4: Set Up Supabase

```bash
# Login to Supabase CLI
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Push database migrations
supabase db push
```

## 🎯 Starting Suna AI

### Option 1: Docker Compose (Recommended)

Start all services with Docker:

```bash
# Start all services
docker compose up -d

# Or use the convenience script
python start.py
```

**Services included:**
- Redis (data caching)
- RabbitMQ (message queue)
- Backend API (port 8000)
- Backend Worker (background tasks)
- Frontend (port 3000)

### Option 2: Manual Startup

For development or troubleshooting:

1. **Start infrastructure services:**
```bash
docker compose up redis rabbitmq -d
```

2. **Start frontend** (in one terminal):
```bash
cd frontend
npm run dev
```

3. **Start backend API** (in another terminal):
```bash
cd backend
uv run api.py
```

4. **Start background worker** (in another terminal):
```bash
cd backend
uv run dramatiq run_agent_background
```

## 🌐 Accessing Suna AI

Once all services are running:

1. **Frontend Interface**: http://localhost:3000
2. **Backend API**: http://localhost:8000/api
3. **API Documentation**: http://localhost:8000/docs

## 🔧 Post-Installation

### Create Your First Account

1. Navigate to http://localhost:3000
2. Use Supabase authentication to create your account
3. Complete the initial setup wizard if prompted
4. Configure your AI model preferences in settings

### Verify Installation

Check that all services are healthy:

```bash
# Check Docker services
docker compose ps

# Check logs if needed
docker compose logs -f
```

## 🛠️ Troubleshooting

### Common Issues

1. **Docker services not starting**
   ```bash
   # Check Docker logs
   docker compose logs
   
   # Restart services
   docker compose down && docker compose up -d
   ```

2. **Database connection issues**
   - Verify Supabase configuration in `.env` files
   - Ensure 'basejump' schema is exposed in Supabase
   - Check network connectivity to Supabase

3. **LLM API key issues**
   - Verify API keys are correctly entered
   - Check for API usage limits or restrictions
   - Test API keys independently

4. **Daytona connection issues**
   - Verify Daytona API key
   - Check if the container image is correctly configured
   - Ensure Daytona snapshot exists

5. **QStash/Webhook issues**
   - Verify QStash token and signing keys
   - Ensure webhook base URL is publicly accessible
   - Check QStash console for delivery status

### Setup Wizard Issues

If the setup wizard fails:

```bash
# Reset setup progress
rm .setup_progress

# Run setup again
python setup.py
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f frontend
```

## 📊 System Requirements

### Minimum Requirements
- **RAM**: 4GB
- **Storage**: 2GB free disk space
- **CPU**: 2 cores
- **Network**: Stable internet connection for API calls

### Recommended Requirements
- **RAM**: 8GB or more
- **Storage**: 5GB free disk space
- **CPU**: 4 cores or more
- **Network**: High-speed internet connection

## 🔄 Managing Suna AI

### Starting/Stopping Services

```bash
# Start all services
python start.py

# Stop all services (when prompted)
python start.py

# Force start without confirmation
python start.py -f
```

### Updating Suna AI

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker compose build --no-cache

# Restart services
docker compose up -d
```

## 🆘 Getting Help

- **Discord Community**: [Join Suna Discord](https://discord.gg/Py6pCBUUPw)
- **GitHub Issues**: [Report bugs or request features](https://github.com/kortix-ai/suna/issues)
- **Documentation**: Check the `docs/` folder for additional guides

## 🔐 Security Notes

- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Ensure webhook URLs are properly secured
- Regularly update dependencies and Docker images
- Use strong passwords for Supabase and other services

## 📝 Notes

- Always use the latest stable version from the official repository
- The software is actively developed - check for updates regularly
- Configuration may change between versions - refer to the official documentation
- For production deployments, consider additional security measures and monitoring

---

**Repository**: https://github.com/kortix-ai/suna
**License**: Check the LICENSE file in the repository
**Version**: This guide is based on the latest version as of the documentation date