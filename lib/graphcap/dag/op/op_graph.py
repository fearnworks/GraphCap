from typing import List, Optional, Dict, Any

from .node import BaseNode 

class GraphDefinition:
    """
    Defines a graph of interconnected OpNodes in graphcap.

    This class allows you to compose complex workflows by connecting
    multiple OpNodes and defining dependencies between them.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        nodes: Optional[List[BaseNode]] = None, # List of OpNode instances (or BaseNode initially)
        dependencies: Optional[Dict[str, List[str]]] = None # Dictionary defining node dependencies
    ):
        """
        Args:
            name (str): Name of the graph. Must be unique within the graphcap system.
            description (Optional[str]): Human-readable description of the graph.
            nodes (Optional[List[BaseNode]]): List of OpNode instances (or BaseNode initially) in the graph.
            dependencies (Optional[Dict[str, List[str]]]): Dictionary defining dependencies between nodes in the graph.
                Keys are node IDs, and values are lists of node IDs that the key node depends on.
        """
        self._name = check_str_param(name, "name")
        self._description = check_opt_str_param(description, "description")
        self._nodes = tuple(check_opt_list_param(nodes, "nodes", of_type=BaseNode)) if nodes else () # Store nodes as tuple
        self._dependencies = check.opt_mapping_param(dependencies, "dependencies", key_type=str, value_type=list) or {} # Store dependencies


    @property
    def name(self) -> str:
        """str: The name of this graph."""
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Optional[str]: Human-readable description of the graph."""
        return self._description

    @property
    def nodes(self) -> List[BaseNode]:
        """List[BaseNode]: Returns the list of nodes (OpNodes) in this graph."""
        return list(self._nodes) # Return as list for mutability if needed

    @property
    def dependency_map(self) -> Dict[str, List[str]]:
        """Dict[str, List[str]]: Returns the dependency map for this graph."""
        return self._dependencies


    def validate_graph_structure(self) -> bool:
        """
        Validates the graph structure (e.g., cycle detection, dependency correctness).

        Returns:
            bool: True if graph structure is valid, raises ValueError if invalid.
        """
        # (Implementation of graph validation logic - cycle detection, etc. - from dag/dag.py)
        # ... (Reuse or adapt validation logic from existing graphcap DAG validation) ...
        # For MVP, focus on cycle detection and dependency existence.
        pass # Placeholder for validation logic

    # (Potentially add methods for adding/removing nodes, getting nodes by ID, etc. if needed for more dynamic graph manipulation in future)

def check_str_param(val: str, param_name: str) -> str: # Reuse check functions
    if not isinstance(val, str):
        raise TypeError(f"Param '{param_name}' must be a string, got {type(val).__name__}")
    return val


def check_opt_str_param(val: Optional[str], param_name: str) -> Optional[str]: # Reuse check functions
    if val is not None and not isinstance(val, str):
        raise TypeError(f"Optional param '{param_name}' must be a string or None, got {type(val).__name__}")
    return val

def check_opt_list_param(val: Optional[List[Any]], param_name: str, of_type: type) -> Optional[List[Any]]: # Reuse check functions
    if val is None:
        return None
    if not isinstance(val, list):
        raise TypeError(f"Param '{param_name}' must be a list, got {type(val).__name__}")
    for item in val:
        if not isinstance(item, of_type):
            raise TypeError(f"Items in list '{param_name}' must be of type {of_type.__name__}, got {type(item).__name__}")
    return val


def check_opt_mapping_param(val: Optional[Mapping[str, Any]], param_name: str, key_type: type = str, value_type: type = Any) -> Optional[Mapping[str, Any]]: # Reuse check functions
    if val is None:
        return None
    if not isinstance(val, Mapping):
        raise TypeError(f"Param '{param_name}' must be a mapping (dict-like), got {type(val).__name__}")
    for key, value in val.items():
        if not isinstance(key, key_type):
            raise TypeError(f"Keys in mapping '{param_name}' must be of type {key_type.__name__}, got {type(key).__name__} for key '{key}'")
        if not isinstance(value, value_type):
            raise TypeError(f"Values in mapping '{param_name}' must be of type {value_type.__name__}, got {type(value).__name__} for key '{key}'")
    return val