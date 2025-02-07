# graphcap/dag/job_definition.py

from typing import Optional

from .dag import DAG  # Import DAG class

class JobDefinition:
    """
    Defines a runnable Job in graphcap, encapsulating a DAG and execution settings.

    Jobs are the primary unit of execution and monitoring in graphcap.
    """

    def __init__(
        self,
        name: str,
        dag: DAG,  # JobDefinition holds a DAG instance
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None, # Simplified tags for MVP
        metadata: Optional[Dict[str, Any]] = None # Simplified metadata for MVP
    ):
        """
        Args:
            name (str): Name of the job. Must be unique within the graphcap system.
            dag (DAG): The DAG instance that this job will execute.
            description (Optional[str]): Human-readable description of the job.
            tags (Optional[Dict[str, str]]): Tags for categorizing and filtering jobs.
            metadata (Optional[Dict[str, Any]]): Metadata for the job.
        """
        self._name = check_str_param(name, "name")
        self._description = check_opt_str_param(description, "description")
        self._dag = check.inst_param(dag, "dag", DAG) # Ensure it's a DAG instance
        self._tags = check.opt_mapping_param(tags, "tags", key_type=str, value_type=str)
        self._metadata = check.opt_mapping_param(metadata, "metadata", key_type=str)


    @property
    def name(self) -> str:
        """str: The name of this job."""
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Optional[str]: Human-readable description of the job."""
        return self._description

    @property
    def dag(self) -> DAG:
        """DAG: Returns the DAG instance associated with this job."""
        return self._dag

    @property
    def tags(self) -> Mapping[str, str]:
        """Mapping[str, str]: Returns the tags dictionary associated with this job."""
        return self._tags or {}

    @property
    def metadata_items(self) -> Mapping[str, Any]:
        """Mapping[str, Any]: Returns the metadata dictionary associated with this job."""
        return self._metadata or {}


    async def execute(self, start_node: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the job, running the underlying DAG.

        Args:
            start_node (Optional[str]): Optional node ID to start execution from within the DAG.

        Returns:
            Dict[str, Any]: Results from the DAG execution.
        """
        # (Execution logic - call dag.execute, potentially handle job-level context/logging in future)
        return await self._dag.execute(start_node=start_node) # For MVP, simply delegate to DAG execution


def check_str_param(val: str, param_name: str) -> str: # Reuse validation functions
    if not isinstance(val, str):
        raise TypeError(f"Param '{param_name}' must be a string, got {type(val).__name__}")
    return val


def check_opt_str_param(val: Optional[str], param_name: str) -> Optional[str]: # Reuse validation functions
    if val is not None and not isinstance(val, str):
        raise TypeError(f"Optional param '{param_name}' must be a string or None, got {type(val).__name__}")
    return val

def check_inst_param(val: Any, param_name: str, cls: type) -> Any: # Reuse validation functions
    if not isinstance(val, cls):
        raise TypeError(f"Param '{param_name}' must be an instance of {cls.__name__}, got {type(val).__name__}")
    return val

def check_opt_mapping_param(val: Optional[Mapping[str, Any]], param_name: str, key_type: type = str, value_type: type = Any) -> Optional[Mapping[str, Any]]: # Reuse validation functions
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