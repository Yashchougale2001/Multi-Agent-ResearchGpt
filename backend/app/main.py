# FastAPI entry point
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.schemas import (
    ResearchRequest, 
    ResearchResponse, 
    DocumentUpload,
    ReportOutput
)
from app.graph.workflow import research_workflow
from app.services.websocket_manager import ws_manager
from app.services.chromadb_service import chroma_service
import uuid
import logging
from typing import Dict
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="AI-powered research assistant using LangGraph and ChromaDB",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active research sessions
active_sessions: Dict[str, Dict] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Multi-Agent Research Assistant",
        "version": "1.0.0"
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "active_sessions": len(active_sessions),
        "chromadb_stats": chroma_service.get_collection_stats()
    }


@app.post("/api/research", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """Start a new research task"""
    try:
        # Generate session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize session
        active_sessions[session_id] = {
            "query": request.query,
            "status": "initializing",
            "started_at": datetime.now().isoformat()
        }
        
        # Start research in background
        background_tasks.add_task(
            execute_research_workflow,
            session_id,
            request.query
        )
        
        logger.info(f"Research started for session: {session_id}")
        
        return ResearchResponse(
            session_id=session_id,
            status="started",
            message="Research task initiated successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start research: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_research_workflow(session_id: str, query: str):
    """Execute research workflow and send updates via WebSocket"""
    try:
        # Send initial update
        await ws_manager.send_update(session_id, {
            "type": "status",
            "step": "planning",
            "message": "Analyzing query and creating research plan..."
        })
        
        # Execute workflow
        final_state = await research_workflow.execute(query, session_id)
        
        # Send progress updates for each step
        steps = [
            ("planning", "Research plan created"),
            ("researching", "Gathering information..."),
            ("retrieving", "Retrieving relevant documents..."),
            ("summarizing", "Generating final report...")
        ]
        
        for idx, (step, message) in enumerate(steps):
            await ws_manager.send_update(session_id, {
                "type": "progress",
                "step": step,
                "progress": int((idx + 1) / len(steps) * 100),
                "message": message
            })
            await asyncio.sleep(0.5)  # Small delay for UX
        
        # Send final result
        if final_state["status"] == "completed":
            await ws_manager.send_update(session_id, {
                "type": "completed",
                "data": {
                    "final_report": final_state["final_report"],
                    "metadata": final_state["summary_metadata"],
                    "subtasks": final_state["subtasks"]
                }
            })
            
            active_sessions[session_id]["status"] = "completed"
            active_sessions[session_id]["result"] = final_state
        else:
            await ws_manager.send_update(session_id, {
                "type": "error",
                "message": f"Research failed: {final_state.get('errors', ['Unknown error'])}"
            })
            
            active_sessions[session_id]["status"] = "failed"
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        await ws_manager.send_update(session_id, {
            "type": "error",
            "message": str(e)
        })


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, session_id)
        logger.info(f"WebSocket disconnected: {session_id}")


@app.get("/api/research/{session_id}", response_model=ReportOutput)
async def get_research_result(session_id: str):
    """Get research results for a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Research not completed. Current status: {session['status']}"
        )
    
    result = session["result"]
    
    return ReportOutput(
        query=result["query"],
        final_report=result["final_report"],
        metadata=result["summary_metadata"],
        subtasks=result["subtasks"],
        research_results_count=len(result["research_results"]),
        documents_retrieved_count=len(result["retrieved_docs"]),
        timestamp=session["started_at"]
    )


@app.post("/api/documents/upload")
async def upload_document(document: DocumentUpload):
    """Upload a document to ChromaDB"""
    try:
        doc_id = str(uuid.uuid4())
        
        success = chroma_service.add_documents(
            documents=[document.content],
            metadatas=[document.metadata],
            ids=[doc_id]
        )
        
        if success:
            return {"status": "success", "doc_id": doc_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to upload document")
    
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a research session"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"status": "success", "message": "Session deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )