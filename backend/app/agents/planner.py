# Planner Agent
from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from app.agents.base import BaseAgent
from app.graph.state import SubTask
import json
import uuid


class PlannerAgent(BaseAgent):
    """Agent responsible for decomposing research queries into subtasks"""
    
    def __init__(self):
        super().__init__("Planner", temperature=0.3)
        
        self.planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert research planner. Your task is to decompose complex research queries into actionable subtasks.

For each query, create a structured research plan with:
1. Web search tasks for recent information
2. Document retrieval tasks for in-depth knowledge
3. Data analysis tasks if needed

Guidelines:
- Create 3-5 focused subtasks
- Prioritize tasks (1=highest, 5=lowest)
- Specify task type: "web_search", "document_query", or "data_analysis"
- Make each subtask specific and actionable

Return ONLY a valid JSON array of subtasks with this structure:
[
  {{
    "description": "specific task description",
    "type": "web_search|document_query|data_analysis",
    "priority": 1-5,
    "search_queries": ["query1", "query2"] // if applicable
  }}
]"""),
            ("user", "Research Query: {query}\n\nCreate a research plan:")
        ])
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose query into subtasks"""
        self.log_execution(f"Planning for query: {state['query']}")
        
        try:
            # Generate plan
            response = self.llm.invoke(
                self.planning_prompt.format_messages(query=state['query'])
            )
            
            # Parse subtasks
            subtasks_data = self._parse_subtasks(response.content)
            
            # Create SubTask objects
            subtasks = []
            for idx, task_data in enumerate(subtasks_data):
                subtask = {
                    "id": str(uuid.uuid4()),
                    "description": task_data["description"],
                    "type": task_data["type"],
                    "priority": task_data.get("priority", 3),
                    "status": "pending",
                    "result": None,
                    "search_queries": task_data.get("search_queries", [])
                }
                subtasks.append(subtask)
            
            self.log_execution(f"Created {len(subtasks)} subtasks")
            
            return {
                "subtasks": subtasks,
                "planning_thoughts": response.content,
                "current_step": "planning_complete",
                "status": "researching",
                "messages": [self.create_message("assistant", f"Created research plan with {len(subtasks)} tasks")]
            }
            
        except Exception as e:
            self.log_execution(f"Planning failed: {str(e)}", "error")
            return {
                "errors": [f"Planning error: {str(e)}"],
                "status": "failed"
            }
    
    def _parse_subtasks(self, content: str) -> List[Dict]:
        """Parse LLM response to extract subtasks"""
        try:
            # Try to find JSON array in response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create single task
                return [{
                    "description": content[:200],
                    "type": "web_search",
                    "priority": 1
                }]
        except json.JSONDecodeError:
            self.log_execution("Failed to parse JSON, using fallback", "warning")
            return [{
                "description": f"Research: {content[:200]}",
                "type": "web_search",
                "priority": 1
            }]