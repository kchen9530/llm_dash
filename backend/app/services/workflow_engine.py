"""
Workflow Execution Engine for Multi-Agent LLM Pipelines
Supports DAG-based workflows with topological execution
"""
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import asyncio
import logging

logger = logging.getLogger(__name__)


class WorkflowNode:
    """Represents a single node in the workflow"""
    
    def __init__(
        self,
        node_id: str,
        model_id: str,
        model_name: str,
        prompt_template: str,
        position: Optional[Dict[str, float]] = None
    ):
        self.node_id = node_id
        self.model_id = model_id
        self.model_name = model_name
        self.prompt_template = prompt_template
        self.position = position or {"x": 0, "y": 0}
        self.output: Optional[str] = None
        self.error: Optional[str] = None
        self.execution_time: float = 0.0


class WorkflowEdge:
    """Represents a connection between two nodes"""
    
    def __init__(self, source: str, target: str, edge_id: Optional[str] = None):
        self.source = source
        self.target = target
        self.edge_id = edge_id or f"{source}-{target}"


class WorkflowExecutor:
    """
    Executes a DAG workflow of LLM models
    
    Features:
    - Topological sorting for correct execution order
    - Parallel execution of independent nodes
    - Dynamic prompt building with predecessor outputs
    - Error handling and partial execution
    """
    
    def __init__(self):
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: List[WorkflowEdge] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = defaultdict(int)
    
    def add_node(self, node: WorkflowNode):
        """Add a node to the workflow"""
        self.nodes[node.node_id] = node
        if node.node_id not in self.in_degree:
            self.in_degree[node.node_id] = 0
    
    def add_edge(self, edge: WorkflowEdge):
        """Add an edge to the workflow"""
        self.edges.append(edge)
        self.adjacency[edge.source].append(edge.target)
        self.in_degree[edge.target] += 1
        
        # Ensure source node is in in_degree
        if edge.source not in self.in_degree:
            self.in_degree[edge.source] = 0
    
    def validate_dag(self) -> tuple[bool, Optional[str]]:
        """
        Validate that the workflow is a valid DAG (no cycles)
        
        Returns:
            (is_valid, error_message)
        """
        # Check if there are any nodes
        if not self.nodes:
            return False, "Workflow has no nodes"
        
        # Detect cycles using topological sort
        temp_in_degree = self.in_degree.copy()
        queue = deque([node_id for node_id, degree in temp_in_degree.items() if degree == 0])
        processed = 0
        
        while queue:
            current = queue.popleft()
            processed += 1
            
            for neighbor in self.adjacency[current]:
                temp_in_degree[neighbor] -= 1
                if temp_in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if processed != len(self.nodes):
            return False, "Workflow contains cycles (not a valid DAG)"
        
        return True, None
    
    def get_execution_order(self) -> List[List[str]]:
        """
        Get execution order as layers (nodes in same layer can run in parallel)
        
        Returns:
            List of layers, where each layer is a list of node IDs
        """
        temp_in_degree = self.in_degree.copy()
        layers = []
        
        while any(degree == 0 for degree in temp_in_degree.values()):
            # Get all nodes with in-degree 0 (can execute now)
            current_layer = [
                node_id for node_id, degree in temp_in_degree.items() 
                if degree == 0
            ]
            
            if not current_layer:
                break
            
            layers.append(current_layer)
            
            # Remove these nodes and update in-degrees
            for node_id in current_layer:
                temp_in_degree[node_id] = -1  # Mark as processed
                for neighbor in self.adjacency[node_id]:
                    if temp_in_degree[neighbor] > 0:
                        temp_in_degree[neighbor] -= 1
        
        return layers
    
    def build_prompt(
        self, 
        node: WorkflowNode, 
        user_input: str,
        predecessor_outputs: Dict[str, str]
    ) -> str:
        """
        Build the prompt for a node by substituting variables
        
        Variables:
        - {input} - Original user input
        - {node_id} - Output from a specific predecessor node
        
        Example template:
        "Based on this analysis: {analysis_node}, provide recommendations: {input}"
        """
        prompt = node.prompt_template
        
        # Replace {input} with user input
        prompt = prompt.replace("{input}", user_input)
        
        # Replace {node_id} with predecessor outputs
        for pred_id, pred_output in predecessor_outputs.items():
            prompt = prompt.replace(f"{{{pred_id}}}", pred_output)
        
        return prompt
    
    async def execute_node(
        self,
        node: WorkflowNode,
        user_input: str,
        predecessor_outputs: Dict[str, str]
    ) -> None:
        """
        Execute a single node
        
        Args:
            node: The node to execute
            user_input: Original user input
            predecessor_outputs: Dict of {node_id: output} from predecessors
        """
        import time
        from app.services.lightweight_model_manager import LightweightModelManager
        
        start_time = time.time()
        
        try:
            # Build the prompt
            prompt = self.build_prompt(node, user_input, predecessor_outputs)
            
            logger.info(f"Executing node {node.node_id} ({node.model_name})")
            logger.debug(f"Prompt: {prompt[:100]}...")
            
            # Get model manager
            manager = LightweightModelManager()
            model = manager.get_model(node.model_id)
            
            if not model or model.status != "RUNNING":
                raise ValueError(f"Model {node.model_id} is not running")
            
            # Execute the model
            output = await manager.generate(
                model_id=node.model_id,
                prompt=prompt,
                max_tokens=256,
                temperature=0.7
            )
            
            node.output = output.strip()
            node.execution_time = time.time() - start_time
            
            logger.info(f"Node {node.node_id} completed in {node.execution_time:.2f}s")
            
        except Exception as e:
            node.error = str(e)
            node.execution_time = time.time() - start_time
            logger.error(f"Node {node.node_id} failed: {e}")
    
    async def execute(self, user_input: str) -> Dict[str, Any]:
        """
        Execute the entire workflow
        
        Args:
            user_input: The initial user input to the workflow
            
        Returns:
            Execution results with outputs for each node
        """
        # Validate DAG
        is_valid, error = self.validate_dag()
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "nodes": {}
            }
        
        # Get execution order
        layers = self.get_execution_order()
        
        logger.info(f"Executing workflow with {len(self.nodes)} nodes in {len(layers)} layers")
        
        # Track outputs
        all_outputs: Dict[str, str] = {}
        
        # Execute layer by layer
        for layer_idx, layer in enumerate(layers):
            logger.info(f"Executing layer {layer_idx + 1}/{len(layers)}: {layer}")
            
            # Execute all nodes in this layer in parallel
            tasks = []
            for node_id in layer:
                node = self.nodes[node_id]
                
                # Get predecessor outputs
                predecessors = [
                    edge.source for edge in self.edges 
                    if edge.target == node_id
                ]
                predecessor_outputs = {
                    pred_id: all_outputs.get(pred_id, "") 
                    for pred_id in predecessors
                }
                
                # Create task
                task = self.execute_node(node, user_input, predecessor_outputs)
                tasks.append((node_id, task))
            
            # Wait for all tasks in this layer
            for node_id, task in tasks:
                await task
                node = self.nodes[node_id]
                if node.output:
                    all_outputs[node_id] = node.output
        
        # Prepare results
        results = {
            "success": True,
            "total_execution_time": sum(node.execution_time for node in self.nodes.values()),
            "layers": len(layers),
            "nodes": {
                node_id: {
                    "model_id": node.model_id,
                    "model_name": node.model_name,
                    "output": node.output,
                    "error": node.error,
                    "execution_time": node.execution_time
                }
                for node_id, node in self.nodes.items()
            }
        }
        
        return results


def create_workflow_from_definition(definition: Dict[str, Any]) -> WorkflowExecutor:
    """
    Create a workflow executor from a JSON definition
    
    Definition format:
    {
        "nodes": [
            {
                "id": "node1",
                "model_id": "gpt2-123",
                "model_name": "GPT-2",
                "prompt_template": "Analyze this: {input}",
                "position": {"x": 100, "y": 100}
            }
        ],
        "edges": [
            {"source": "node1", "target": "node2", "id": "edge1"}
        ]
    }
    """
    executor = WorkflowExecutor()
    
    # Add nodes
    for node_data in definition.get("nodes", []):
        node = WorkflowNode(
            node_id=node_data["id"],
            model_id=node_data["model_id"],
            model_name=node_data["model_name"],
            prompt_template=node_data.get("prompt_template", "{input}"),
            position=node_data.get("position")
        )
        executor.add_node(node)
    
    # Add edges
    for edge_data in definition.get("edges", []):
        edge = WorkflowEdge(
            source=edge_data["source"],
            target=edge_data["target"],
            edge_id=edge_data.get("id")
        )
        executor.add_edge(edge)
    
    return executor
