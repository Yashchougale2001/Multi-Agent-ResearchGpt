# Pydantic models
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class ResearchRequest(BaseModel):
    """Request model for starting research"""
    query: str = Field(..., min_length=10, max_length=1000, description="Research query")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    max_results: Optional[int] = Field(10, ge=1, le=50, description="Maximum results")


class ResearchResponse(BaseModel):
    """Response model for research results"""
    session_id: str
    status: str
    message: str
    data: Optional[Dict] = None


class DocumentUpload(BaseModel):
    """Model for uploading documents"""
    content: str = Field(..., description="Document content")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")


class ProgressUpdate(BaseModel):
    """Model for progress updates"""
    session_id: str
    current_step: str
    status: str
    progress_percentage: int
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ReportOutput(BaseModel):
    """Final report output"""
    query: str
    final_report: str
    metadata: Dict
    subtasks: List[Dict]
    research_results_count: int
    documents_retrieved_count: int
    timestamp: str