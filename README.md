# ResearchGPT

# Multi-Agent Research Assistant

A production-ready AI-powered research assistant built with **LangGraph**, **LangChain**, **FastAPI**, **ChromaDB**, and **React**. The system uses specialized agents to decompose research queries, gather information, retrieve relevant documents, and generate comprehensive reports.

![System Architecture](docs/architecture.png)

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for planning, research, retrieval, and summarization
- **RAG Implementation**: Semantic search with ChromaDB for accurate document retrieval
- **Real-time Updates**: WebSocket integration for live progress monitoring
- **LangGraph Orchestration**: State-based workflow management
- **Modern UI**: React frontend with Tailwind CSS
- **Production Ready**: Docker support, error handling, logging

## 🏗️ Architecture

### Backend Components

- **Planner Agent**: Decomposes complex queries into actionable subtasks
- **Research Agent**: Gathers information from web searches and APIs
- **Retriever Agent**: Performs semantic search using ChromaDB
- **Summarizer Agent**: Generates comprehensive research reports

### Tech Stack

**Backend:**

- FastAPI (REST API & WebSockets)
- LangGraph (Agent orchestration)
- LangChain (LLM framework)
- ChromaDB (Vector database)
- OpenAI GPT-4 (Language model)

**Frontend:**

- React 18
- Tailwind CSS
- WebSocket client
- Axios

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (optional)
- OpenAI API key

### Installation

#### 1. Clone Repository

````bash
git clone
cd multi-agent-research-assistant
2. Backend Setup
Bash

cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run backend
uvicorn app.main:app --reload
3. Frontend Setup
Bash

cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
4. Access Application
Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Documentation: http://localhost:8000/docs
Docker Deployment
Bash

# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
📖 Usage
Basic Research Flow
Enter Query: Type your research question in the input field
Monitor Progress: Watch agents execute tasks in real-time
View Results: Get a comprehensive markdown-formatted report
Example Queries
text

"What are the latest developments in quantum computing?"
"Compare different machine learning frameworks for NLP"
"Analyze the impact of AI on healthcare industry"
"Best practices for implementing RAG systems"
API Usage
Start Research
Bash

curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "Your research question here"}'
Get Results
Bash

curl "http://localhost:8000/api/research/{session_id}"
Upload Document
Bash

curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your document content",
    "metadata": {"source": "manual", "tags": ["ai", "research"]}
  }'
🔧 Configuration
Environment Variables
env

# LLM Configuration
## 🆓 Free Tier Setup (Groq API)

This project uses **Groq API** with Llama 3 models - completely FREE!

### Get Your Free Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### Available Free Models

- **llama-3.3-70b-versatile** (Recommended - Fast & Powerful)
- **llama-3.1-8b-instant** (Ultra-fast responses)
- **mixtral-8x7b-32768** (Long context window)
- **gemma-7b-it** (Googles efficient model)

### Groq Limits (Free Tier)

- **Requests per minute**: 30
- **Requests per day**: 14,400
- **Tokens per minute**: 6,000
- **Context window**: Up to 8,192 tokens

Perfect for development and moderate production use!

### Embeddings (100% Free & Local)

We use **sentence-transformers** for embeddings:
- No API costs
- Runs locally on your machine
- Fast inference
- Models: all-MiniLM-L6-v2 (default), all-mpnet-base-v2

## 📦 Datasets

### Included Sample Datasets

1. **AI Research Papers** (10 documents)
   - Transformer architecture
   - BERT, GPT models
   - RAG systems
   - Multi-agent systems

2. **Programming Knowledge** (5 documents)
   - Python best practices
   - FastAPI, React
   - Docker, Git

3. **Business Knowledge** (3 documents)
   - Agile methodology
   - AI in healthcare
   - Cybersecurity

### Initialize Datasets

```bash
cd backend
python scripts/init_datasets.py

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=research_docs

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Research Settings
MAX_SEARCH_RESULTS=10
MAX_SUBTASKS=5
RETRIEVAL_TOP_K=5
🏛️ Project Structure
text

multi-agent-research-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent implementations
│   │   ├── api/             # API routes and schemas
│   │   ├── graph/           # LangGraph workflow
│   │   ├── services/        # ChromaDB, LLM, WebSocket
│   │   └── main.py          # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API and WebSocket clients
│   │   └── hooks/           # Custom React hooks
│   └── package.json
├── docker-compose.yml
└── README.md
📊 Agent Workflow
mermaid

graph LR
    A[User Query] --> B[Planner Agent]
    B --> C[Research Agent]
    C --> D[Retriever Agent]
    D --> E[Summarizer Agent]
    E --> F[Final Report]
🧪 Testing
Backend Tests
Bash

cd backend
pytest tests/
Frontend Tests
Bash

cd frontend
npm test
End-to-End Test
Bash

# Run test script
python backend/test_system.py
🔒 Security
API key encryption
Input validation
Rate limiting
CORS configuration
Secure WebSocket connections
📈 Performance
Async processing
Response caching
Connection pooling
Batch operations
Lazy loading
🛠️ Development
Adding New Agents
Create agent class in backend/app/agents/
Implement execute() method
Add node in backend/app/graph/nodes.py
Update workflow in backend/app/graph/workflow.py
Adding API Endpoints
Define schema in backend/app/api/schemas.py
Implement route in backend/app/api/routes.py
Update documentation
🐛 Troubleshooting
Common Issues
ChromaDB Connection Error

Bash

# Clear ChromaDB data
rm -rf backend/chroma_db
WebSocket Connection Failed

Bash

# Check CORS settings in .env
# Ensure backend is running on correct port
LLM Rate Limit

Bash

# Add retry logic or reduce concurrent requests
📝 Changelog
v1.0.0 (2024)
Initial release
Multi-agent architecture
RAG implementation
Real-time WebSocket updates
Docker support
🤝 Contributing
Fork the repository
Create feature branch (git checkout -b feature/amazing-feature)
Commit changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing-feature)
Open Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Authors
Yash chougale - Initial work - https://github.com/Yashchougale2001
🙏 Acknowledgments
OpenAI for GPT-4
LangChain team
ChromaDB developers
FastAPI community
📞 Support
Documentation: [Link to docs]
Issues: GitHub Issues
Email: yashachougale2001@gmail.com
🔮 Roadmap
 Add authentication (JWT)
 Implement user sessions
 Add conversation history
 Support multiple LLM providers
 Add export to PDF/DOCX
 Implement agent feedback loop
 Add voice input
 Mobile app
Built with ❤️ using LangGraph and FastAPI
````
