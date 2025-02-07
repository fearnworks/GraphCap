# graphcap/dag/asset_definition.py
# Note: Building a simplified, standalone AssetDefinition for graphcap,
# inspired by Dagster but without Dagster dependencies.

from typing import Any, List, Mapping, Optional


class AssetDefinition:
    """
    Defines a graphcap Asset Definition.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        keys: Optional[List[str]] = None,  # List of string keys representing the asset (simplified AssetKey)
        dependencies: Optional[List[str]] = None,  # List of dependency Node IDs
        asset_metadata: Optional[Mapping[str, Any]] = None,  # Dictionary for metadata
        tags: Optional[Mapping[str, str]] = None,  # Dictionary for tags
        group_name: Optional[str] = None,  # Group name for organization
    ):
        self.name = check_str_param(name, "name")
        self.description = check_opt_str_param(description, "description")
        self.keys = tuple(check_opt_list_param(keys, "keys", of_type=str)) if keys else (name,)  # Default key to name
        self.dependencies = (
            tuple(check_opt_list_param(dependencies, "dependencies", of_type=str)) if dependencies else ()
        )
        self.asset_metadata = check.opt_mapping_param(asset_metadata, "asset_metadata", key_type=str)
        self.tags = check.opt_mapping_param(tags, "tags", key_type=str, value_type=str)
        self.group_name = check.opt_str_param(group_name, "group_name")


    @property
    def asset_key(self) -> str:
        """Returns the primary asset key (name) for this definition."""
        return self.name

    @property
    def dependency_ids(self) -> List[str]:
        """List[str]: The list of node IDs that are upstream dependencies of this asset."""
        return list(self.dependencies)

    @property
    def all_asset_keys(self) -> List[str]:
        """List[str]: Returns a list of all asset keys associated with this definition."""
        return list(self.keys)

    @property
    def asset_metadata_items(self) -> Mapping[str, Any]:
        """Mapping[str, Any]: Returns the metadata dictionary associated with this asset."""
        return self.asset_metadata or {}

    @property
    def definition_tags(self) -> Mapping[str, str]:
        """Mapping[str, str]: Returns the tags dictionary associated with this asset definition."""
        return self.tags or {}

    @property
    def asset_group_name(self) -> Optional[str]:
        """Optional[str]: Returns the group name for this asset, if any."""
        return self.group_name

    @property
    def asset_description(self) -> Optional[str]:
        """Optional[str]: Returns the description for this asset, if any."""
        return self.description


def check_str_param(val: str, param_name: str) -> str:
    if not isinstance(val, str):
        raise TypeError(f"Param '{param_name}' must be a string, got {type(val).__name__}")
    return val


def check_opt_str_param(val: Optional[str], param_name: str) -> Optional[str]:
    if val is not None and not isinstance(val, str):
        raise TypeError(f"Optional param '{param_name}' must be a string or None, got {type(val).__name__}")
    return val


def check_opt_list_param(val: Optional[List[str]], param_name: str, of_type: type) -> Optional[List[str]]:
    if val is None:
        return None
    if not isinstance(val, list):
        raise TypeError(f"Param '{param_name}' must be a list, got {type(val).__name__}")
    for item in val:
        if not isinstance(item, of_type):
            raise TypeError(
                f"Items in list '{param_name}' must be of type {of_type.__name__}, got {type(item).__name__}"
            )
    return val


def check_opt_mapping_param(
    val: Optional[Mapping[str, Any]], param_name: str, key_type: type = str, value_type: type = Any
) -> Optional[Mapping[str, Any]]:
    if val is None:
        return None
    if not isinstance(val, Mapping):
        raise TypeError(f"Param '{param_name}' must be a mapping (dict-like), got {type(val).__name__}")
    for key, value in val.items():
        if not isinstance(key, key_type):
            raise TypeError(
                f"Keys in mapping '{param_name}' must be of type {key_type.__name__}, got {type(key).__name__} for key '{key}'"
            )
        if not isinstance(value, value_type):
            raise TypeError(
                f"Values in mapping '{param_name}' must be of type {value_type.__name__}, got {type(value).__name__} for key '{key}'"
            )
    return val
