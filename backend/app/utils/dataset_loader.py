import os
import json
import requests
from typing import List, Dict
from app.services.chromadb_service import chroma_service
import uuid
import logging

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Load and index various datasets into ChromaDB"""
    
    def __init__(self):
        self.datasets_dir = "./datasets"
        os.makedirs(self.datasets_dir, exist_ok=True)
    
    def load_sample_ai_research_papers(self):
        """Load sample AI research papers"""
        papers = [
            {
                "title": "Attention Is All You Need",
                "content": """The Transformer architecture revolutionized natural language processing by introducing 
                the attention mechanism. This model relies entirely on self-attention to compute representations 
                of input and output, without using sequence-aligned RNNs or convolution. The multi-head attention 
                mechanism allows the model to jointly attend to information from different representation subspaces 
                at different positions.""",
                "metadata": {
                    "year": 2017,
                    "authors": "Vaswani et al.",
                    "category": "NLP",
                    "topic": "transformers"
                }
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "content": """BERT is designed to pre-train deep bidirectional representations from unlabeled text 
                by jointly conditioning on both left and right context in all layers. The pre-trained BERT model 
                can be fine-tuned with just one additional output layer to create state-of-the-art models for a 
                wide range of NLP tasks, such as question answering and language inference.""",
                "metadata": {
                    "year": 2018,
                    "authors": "Devlin et al.",
                    "category": "NLP",
                    "topic": "language_models"
                }
            },
            {
                "title": "Retrieval-Augmented Generation for Knowledge-Intensive Tasks",
                "content": """RAG models combine the benefits of retrieval-based and generation-based approaches. 
                They use a pre-trained seq2seq model as the generator and a dense vector index of Wikipedia as a 
                non-parametric memory, accessed through a neural retriever. This approach achieves state-of-the-art 
                results on several knowledge-intensive tasks.""",
                "metadata": {
                    "year": 2020,
                    "authors": "Lewis et al.",
                    "category": "NLP",
                    "topic": "rag"
                }
            },
            {
                "title": "LangChain: Building Applications with LLMs",
                "content": """LangChain is a framework for developing applications powered by language models. 
                It enables applications that are context-aware (connecting language models to sources of context) 
                and agentic (allowing language models to interact with their environment). The framework provides 
                components for working with language models and off-the-shelf chains for accomplishing specific tasks.""",
                "metadata": {
                    "year": 2023,
                    "authors": "Chase et al.",
                    "category": "Framework",
                    "topic": "llm_applications"
                }
            },
            {
                "title": "Vector Databases for AI Applications",
                "content": """Vector databases like ChromaDB, Pinecone, and Weaviate are designed to store and 
                query high-dimensional vectors efficiently. They use approximate nearest neighbor (ANN) algorithms 
                like HNSW to enable fast similarity search. These databases are crucial for RAG systems, 
                semantic search, and recommendation engines.""",
                "metadata": {
                    "year": 2023,
                    "authors": "Various",
                    "category": "Infrastructure",
                    "topic": "vector_databases"
                }
            },
            {
                "title": "Multi-Agent Systems with LLMs",
                "content": """Multi-agent systems using LLMs involve multiple AI agents working together to solve 
                complex tasks. Each agent can have specialized roles (e.g., planner, researcher, critic) and 
                communicate through structured protocols. Frameworks like AutoGen and LangGraph enable the 
                orchestration of these agents with state management and conditional workflows.""",
                "metadata": {
                    "year": 2024,
                    "authors": "Various",
                    "category": "AI_Systems",
                    "topic": "multi_agent"
                }
            },
            {
                "title": "Llama 3: Open Foundation and Fine-tuned Models",
                "content": """Llama 3 is a family of large language models ranging from 8B to 70B parameters. 
                These models are trained on over 15T tokens and support a context window of up to 8K tokens. 
                Llama 3 achieves state-of-the-art performance on various benchmarks and can be fine-tuned for 
                specific tasks. The models are optimized for efficiency and can run on consumer hardware.""",
                "metadata": {
                    "year": 2024,
                    "authors": "Meta AI",
                    "category": "LLM",
                    "topic": "open_source_models"
                }
            },
            {
                "title": "Prompt Engineering Best Practices",
                "content": """Effective prompt engineering involves clear instructions, context provision, 
                and few-shot examples. Techniques include chain-of-thought prompting (asking the model to think 
                step-by-step), role prompting (assigning a persona), and structured output formatting. 
                Temperature and top-p parameters control randomness vs. determinism in responses.""",
                "metadata": {
                    "year": 2024,
                    "authors": "Various",
                    "category": "Techniques",
                    "topic": "prompt_engineering"
                }
            },
            {
                "title": "Fine-tuning vs RAG: When to Use Each",
                "content": """Fine-tuning adapts a pre-trained model to specific tasks by training on domain data, 
                changing model weights. RAG retrieves relevant information at inference time without modifying 
                the model. Use fine-tuning for style/format adaptation and specialized domains. Use RAG for 
                frequently updated information, source attribution, and when training data is limited.""",
                "metadata": {
                    "year": 2024,
                    "authors": "Various",
                    "category": "Techniques",
                    "topic": "model_optimization"
                }
            },
            {
                "title": "Quantum Computing and AI Integration",
                "content": """Quantum computing leverages quantum mechanical phenomena like superposition and 
                entanglement to perform computations. Quantum machine learning combines quantum algorithms with 
                classical ML techniques. Applications include optimization problems, drug discovery, and 
                cryptography. Companies like IBM, Google, and IonQ are developing quantum processors.""",
                "metadata": {
                    "year": 2024,
                    "authors": "Various",
                    "category": "Emerging_Tech",
                    "topic": "quantum_computing"
                }
            }
        ]
        
        self._index_documents(papers, "ai_research_papers")
    
    def load_programming_knowledge(self):
        """Load programming and software development knowledge"""
        docs = [
            {
                "title": "Python Best Practices",
                "content": """Follow PEP 8 style guide, use type hints, write docstrings, keep functions small 
                and focused, use list comprehensions, leverage context managers, prefer f-strings, use virtual 
                environments, write unit tests, and handle exceptions properly.""",
                "metadata": {"category": "Programming", "language": "Python"}
            },
            {
                "title": "FastAPI Framework Guide",
                "content": """FastAPI is a modern web framework for building APIs with Python. Features include 
                automatic OpenAPI documentation, type validation with Pydantic, async support, dependency 
                injection, and high performance. Use path parameters, query parameters, request bodies, 
                and response models effectively.""",
                "metadata": {"category": "Programming", "language": "Python", "framework": "FastAPI"}
            },
            {
                "title": "React Hooks Explained",
                "content": """React Hooks allow functional components to use state and lifecycle features. 
                Common hooks: useState for state management, useEffect for side effects, useContext for 
                context API, useCallback for memoized functions, and useMemo for expensive computations. 
                Custom hooks enable code reuse.""",
                "metadata": {"category": "Programming", "language": "JavaScript", "framework": "React"}
            },
            {
                "title": "Docker Containerization",
                "content": """Docker packages applications and dependencies into containers. Benefits include 
                consistency across environments, isolation, portability, and scalability. Use multi-stage 
                builds, minimize layers, leverage caching, and use .dockerignore. Docker Compose orchestrates 
                multi-container applications.""",
                "metadata": {"category": "DevOps", "tool": "Docker"}
            },
            {
                "title": "Git Version Control",
                "content": """Git tracks changes in source code. Key commands: git init, clone, add, commit, 
                push, pull, branch, merge, and rebase. Use meaningful commit messages, create feature branches, 
                review pull requests, and maintain a clean history. .gitignore excludes files from tracking.""",
                "metadata": {"category": "DevOps", "tool": "Git"}
            }
        ]
        
        self._index_documents(docs, "programming_knowledge")
    
    def load_business_knowledge(self):
        """Load business and industry knowledge"""
        docs = [
            {
                "title": "Agile Software Development",
                "content": """Agile emphasizes iterative development, collaboration, and flexibility. 
                Scrum framework uses sprints, daily standups, sprint planning, reviews, and retrospectives. 
                Kanban visualizes workflow with boards. Benefits include faster delivery, better quality, 
                and customer satisfaction.""",
                "metadata": {"category": "Business", "topic": "methodology"}
            },
            {
                "title": "AI in Healthcare",
                "content": """AI applications in healthcare include medical imaging analysis, drug discovery, 
                personalized treatment plans, predictive analytics, and robotic surgery. Challenges include 
                data privacy, regulatory compliance, and integration with existing systems. AI can improve 
                diagnosis accuracy and reduce costs.""",
                "metadata": {"category": "Business", "industry": "Healthcare"}
            },
            {
                "title": "Cybersecurity Best Practices",
                "content": """Key practices: use strong passwords, enable 2FA, keep software updated, 
                encrypt sensitive data, implement zero trust architecture, conduct security audits, 
                train employees, use VPNs, backup data regularly, and have incident response plans.""",
                "metadata": {"category": "Business", "topic": "security"}
            }
        ]
        
        self._index_documents(docs, "business_knowledge")
    
    def _index_documents(self, documents: List[Dict], source: str):
        """Helper to index documents into ChromaDB"""
        try:
            docs = []
            metadatas = []
            ids = []
            
            for doc in documents:
                content = f"Title: {doc['title']}\n\nContent: {doc['content']}"
                docs.append(content)
                
                metadata = doc.get('metadata', {})
                metadata['source'] = source
                metadata['title'] = doc['title']
                metadatas.append(metadata)
                
                ids.append(str(uuid.uuid4()))
            
            success = chroma_service.add_documents(docs, metadatas, ids)
            
            if success:
                logger.info(f"Indexed {len(docs)} documents from {source}")
            else:
                logger.error(f"Failed to index documents from {source}")
                
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
    
    def load_all_datasets(self):
        """Load all available datasets"""
        logger.info("Loading all datasets...")
        self.load_sample_ai_research_papers()
        self.load_programming_knowledge()
        self.load_business_knowledge()
        logger.info("All datasets loaded successfully!")


# Initialize and load
dataset_loader = DatasetLoader()