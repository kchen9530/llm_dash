"""
Playground API Router
Visual workflow builder for multi-agent LLM pipelines
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.services.workflow_engine import create_workflow_from_definition

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playground", tags=["playground"])


class NodeDefinition(BaseModel):
    """Definition of a workflow node"""
    id: str
    model_id: str
    model_name: str
    prompt_template: str = "{input}"
    position: Optional[Dict[str, float]] = None


class EdgeDefinition(BaseModel):
    """Definition of a workflow edge"""
    source: str
    target: str
    id: Optional[str] = None


class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {
                        "id": "node1",
                        "model_id": "gpt2-123",
                        "model_name": "GPT-2",
                        "prompt_template": "Analyze this text: {input}",
                        "position": {"x": 100, "y": 100}
                    },
                    {
                        "id": "node2",
                        "model_id": "gpt2-456",
                        "model_name": "GPT-2",
                        "prompt_template": "Based on this analysis: {node1}, provide recommendations",
                        "position": {"x": 400, "y": 100}
                    }
                ],
                "edges": [
                    {"source": "node1", "target": "node2", "id": "edge1"}
                ]
            }
        }


class ExecuteWorkflowRequest(BaseModel):
    """Request to execute a workflow"""
    workflow: WorkflowDefinition
    input: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow": {
                    "nodes": [
                        {
                            "id": "analyzer",
                            "model_id": "gpt2-123",
                            "model_name": "GPT-2",
                            "prompt_template": "Analyze the sentiment of: {input}"
                        }
                    ],
                    "edges": []
                },
                "input": "This is a great product!"
            }
        }


class ExecuteWorkflowResponse(BaseModel):
    """Response from workflow execution"""
    success: bool
    error: Optional[str] = None
    total_execution_time: Optional[float] = None
    layers: Optional[int] = None
    nodes: Dict[str, Any] = {}


@router.post("/execute", response_model=ExecuteWorkflowResponse)
async def execute_workflow(request: ExecuteWorkflowRequest):
    """
    Execute a multi-agent workflow
    
    The workflow is defined as a DAG where:
    - Nodes are LLM models with custom prompts
    - Edges define data flow between models
    - Execution follows topological order
    - Nodes in the same layer execute in parallel
    
    Prompt templates support variables:
    - {input} - Original user input
    - {node_id} - Output from predecessor node
    
    Example:
        Node 1: "Analyze: {input}"
        Node 2: "Based on {node1}, suggest improvements"
    """
    try:
        # Convert to dict for workflow creation
        workflow_dict = {
            "nodes": [node.model_dump() for node in request.workflow.nodes],
            "edges": [edge.model_dump() for edge in request.workflow.edges]
        }
        
        # Create workflow executor
        executor = create_workflow_from_definition(workflow_dict)
        
        # Validate before execution
        is_valid, error = executor.validate_dag()
        if not is_valid:
            return ExecuteWorkflowResponse(
                success=False,
                error=error
            )
        
        # Execute workflow
        logger.info(f"Executing workflow with {len(request.workflow.nodes)} nodes")
        result = await executor.execute(request.input)
        
        return ExecuteWorkflowResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.post("/validate")
async def validate_workflow(workflow: WorkflowDefinition):
    """
    Validate a workflow without executing it
    
    Checks:
    - No cycles (valid DAG)
    - All referenced models exist and are running
    - All edge references are valid
    """
    try:
        workflow_dict = {
            "nodes": [node.model_dump() for node in workflow.nodes],
            "edges": [edge.model_dump() for edge in workflow.edges]
        }
        
        executor = create_workflow_from_definition(workflow_dict)
        is_valid, error = executor.validate_dag()
        
        if not is_valid:
            return {
                "valid": False,
                "error": error
            }
        
        # Check if all models are available
        from app.services.lightweight_model_manager import LightweightModelManager
        manager = LightweightModelManager()
        
        unavailable_models = []
        for node in workflow.nodes:
            model = manager.get_model(node.model_id)
            if not model or model.status != "RUNNING":
                unavailable_models.append({
                    "node_id": node.id,
                    "model_id": node.model_id,
                    "model_name": node.model_name
                })
        
        if unavailable_models:
            return {
                "valid": False,
                "error": "Some models are not running",
                "unavailable_models": unavailable_models
            }
        
        # Get execution order
        layers = executor.get_execution_order()
        
        return {
            "valid": True,
            "layers": len(layers),
            "execution_order": layers,
            "total_nodes": len(workflow.nodes)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


@router.get("/available-models")
async def get_available_models():
    """
    Get list of deployed models available for the playground
    
    Returns both chat and embedding models that are currently running
    """
    from app.services.factory import get_model_manager
    
    manager = get_model_manager()
    
    chat_models = manager.list_chat_models()
    embed_models = manager.list_embedding_models()
    
    # Filter only running models
    available_chat = [
        {
            "id": m.id,
            "name": m.model_name,
            "type": "chat",
            "status": m.status
        }
        for m in chat_models if m.status == "RUNNING"
    ]
    
    available_embed = [
        {
            "id": m.id,
            "name": m.model_name,
            "type": "embedding",
            "status": m.status
        }
        for m in embed_models if m.status == "RUNNING"
    ]
    
    return {
        "models": available_chat + available_embed,
        "total": len(available_chat) + len(available_embed)
    }
