from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Query
from typing import List, Optional
from app.api.schemas import (
    ResearchRequest, 
    ResearchResponse,
    DocumentUpload,
    ReportOutput,
    ProgressUpdate
)
from app.graph.workflow import research_workflow
from app.services.chromadb_service import chroma_service
from app.services.websocket_manager import ws_manager
import uuid
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["research"])

# In-memory session storage (use Redis in production)
active_sessions = {}


@router.post("/research", response_model=ResearchResponse)
async def create_research_task(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new research task
    
    - **query**: Research question or topic (10-1000 characters)
    - **session_id**: Optional session ID for resuming
    - **max_results**: Maximum number of results to return (1-50)
    """
    try:
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Check if session already exists
        if session_id in active_sessions and active_sessions[session_id]["status"] in ["processing", "planning", "researching", "retrieving", "summarizing"]:
            raise HTTPException(
                status_code=400,
                detail="Research task already in progress for this session"
            )
        
        # Initialize session
        active_sessions[session_id] = {
            "query": request.query,
            "status": "initializing",
            "created_at": datetime.now().isoformat(),
            "max_results": request.max_results or 10
        }
        
        # Start research workflow in background
        background_tasks.add_task(
            execute_research_workflow,
            session_id,
            request.query,
            request.max_results
        )
        
        logger.info(f"Research task created for session: {session_id}")
        
        return ResearchResponse(
            session_id=session_id,
            status="started",
            message="Research task initiated successfully",
            data={
                "query": request.query,
                "created_at": active_sessions[session_id]["created_at"]
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create research task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start research: {str(e)}")


async def execute_research_workflow(session_id: str, query: str, max_results: int = 10):
    """Execute the research workflow and send WebSocket updates"""
    try:
        # Update session status
        active_sessions[session_id]["status"] = "planning"
        
        # Send initial WebSocket update
        await ws_manager.send_update(session_id, {
            "type": "status",
            "step": "planning",
            "message": "Analyzing query and creating research plan...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Execute workflow
        final_state = await research_workflow.execute(query, session_id)
        
        # Send progress updates
        await ws_manager.send_update(session_id, {
            "type": "progress",
            "step": "planning",
            "progress": 25,
            "message": "Research plan created"
        })
        
        await ws_manager.send_update(session_id, {
            "type": "progress",
            "step": "researching",
            "progress": 50,
            "message": "Gathering information..."
        })
        
        await ws_manager.send_update(session_id, {
            "type": "progress",
            "step": "retrieving",
            "progress": 75,
            "message": "Retrieving relevant documents..."
        })
        
        await ws_manager.send_update(session_id, {
            "type": "progress",
            "step": "summarizing",
            "progress": 90,
            "message": "Generating final report..."
        })
        
        # Check if workflow completed successfully
        if final_state.get("status") == "completed":
            # Store result
            active_sessions[session_id]["status"] = "completed"
            active_sessions[session_id]["result"] = final_state
            active_sessions[session_id]["completed_at"] = datetime.now().isoformat()
            
            # Send completion update
            await ws_manager.send_update(session_id, {
                "type": "completed",
                "progress": 100,
                "data": {
                    "final_report": final_state["final_report"],
                    "metadata": final_state["summary_metadata"],
                    "subtasks": final_state["subtasks"]
                },
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Research completed for session: {session_id}")
        else:
            # Handle errors
            active_sessions[session_id]["status"] = "failed"
            error_msg = final_state.get("errors", ["Unknown error"])
            
            await ws_manager.send_update(session_id, {
                "type": "error",
                "message": f"Research failed: {error_msg}",
                "timestamp": datetime.now().isoformat()
            })
            
            logger.error(f"Research failed for session {session_id}: {error_msg}")
            
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        active_sessions[session_id]["status"] = "failed"
        
        await ws_manager.send_update(session_id, {
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        })


@router.get("/research/{session_id}", response_model=ReportOutput)
async def get_research_result(session_id: str):
    """
    Get research results for a specific session
    
    - **session_id**: Unique session identifier
    """
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
        research_results_count=len(result.get("research_results", [])),
        documents_retrieved_count=len(result.get("retrieved_docs", [])),
        timestamp=session["created_at"]
    )


@router.get("/research/{session_id}/status")
async def get_research_status(session_id: str):
    """
    Get current status of a research session
    
    - **session_id**: Unique session identifier
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "query": session["query"],
        "created_at": session["created_at"],
        "completed_at": session.get("completed_at"),
        "has_result": "result" in session
    }


@router.delete("/research/{session_id}")
async def delete_research_session(session_id: str):
    """
    Delete a research session
    
    - **session_id**: Unique session identifier
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del active_sessions[session_id]
    logger.info(f"Session deleted: {session_id}")
    
    return {
        "status": "success",
        "message": f"Session {session_id} deleted successfully"
    }


@router.get("/sessions")
async def list_sessions(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List all research sessions
    
    - **status**: Optional status filter (completed, failed, processing)
    - **limit**: Maximum number of sessions to return
    """
    sessions = []
    
    for session_id, session_data in list(active_sessions.items())[:limit]:
        if status is None or session_data["status"] == status:
            sessions.append({
                "session_id": session_id,
                "query": session_data["query"],
                "status": session_data["status"],
                "created_at": session_data["created_at"],
                "completed_at": session_data.get("completed_at")
            })
    
    return {
        "total": len(sessions),
        "sessions": sessions
    }


# Document Management Routes

@router.post("/documents/upload")
async def upload_document(document: DocumentUpload):
    """
    Upload a document to the knowledge base
    
    - **content**: Document text content
    - **metadata**: Optional metadata dictionary
    """
    try:
        doc_id = str(uuid.uuid4())
        
        # Add document to ChromaDB
        success = chroma_service.add_documents(
            documents=[document.content],
            metadatas=[{
                **document.metadata,
                "uploaded_at": datetime.now().isoformat(),
                "doc_id": doc_id
            }],
            ids=[doc_id]
        )
        
        if success:
            logger.info(f"Document uploaded: {doc_id}")
            return {
                "status": "success",
                "doc_id": doc_id,
                "message": "Document uploaded successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload document")
    
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document file to the knowledge base
    
    - **file**: Document file (txt, md, pdf)
    """
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        doc_id = str(uuid.uuid4())
        
        # Add to ChromaDB
        success = chroma_service.add_documents(
            documents=[text_content],
            metadatas=[{
                "filename": file.filename,
                "content_type": file.content_type,
                "uploaded_at": datetime.now().isoformat(),
                "doc_id": doc_id
            }],
            ids=[doc_id]
        )
        
        if success:
            logger.info(f"File uploaded: {file.filename} ({doc_id})")
            return {
                "status": "success",
                "doc_id": doc_id,
                "filename": file.filename,
                "message": "File uploaded successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file")
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported. Use UTF-8 text files.")
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/search")
async def search_documents(
    query: str = Query(..., min_length=3),
    top_k: int = Query(5, ge=1, le=20)
):
    """
    Search documents in the knowledge base
    
    - **query**: Search query
    - **top_k**: Number of results to return
    """
    try:
        results = chroma_service.query(query_text=query, n_results=top_k)
        
        documents = []
        if results["documents"] and results["documents"][0]:
            for idx, doc in enumerate(results["documents"][0]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][idx] if results["metadatas"] else {},
                    "similarity_score": 1 - results["distances"][0][idx]
                })
        
        return {
            "query": query,
            "total_results": len(documents),
            "documents": documents
        }
    
    except Exception as e:
        logger.error(f"Document search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/stats")
async def get_document_stats():
    """Get statistics about the document collection"""
    try:
        stats = chroma_service.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get document stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Health and Status Routes

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions),
        "chromadb_status": "connected"
    }


@router.get("/stats")
async def get_system_stats():
    """Get overall system statistics"""
    try:
        chroma_stats = chroma_service.get_collection_stats()
        
        session_stats = {
            "total": len(active_sessions),
            "completed": len([s for s in active_sessions.values() if s["status"] == "completed"]),
            "processing": len([s for s in active_sessions.values() if s["status"] in ["planning", "researching", "retrieving", "summarizing"]]),
            "failed": len([s for s in active_sessions.values() if s["status"] == "failed"])
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sessions": session_stats,
            "documents": chroma_stats,
            "system_status": "operational"
        }
    except Exception as e:
        logger.error(f"Failed to get system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))