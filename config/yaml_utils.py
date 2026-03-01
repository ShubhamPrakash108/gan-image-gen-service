import yaml
from pathlib import Path

def read_yaml(path):
    """
    Read a YAML file and return its contents as a dictionary.

    Args:
        path (str | Path): Path to the YAML file

    Returns:
        dict: Parsed YAML content

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the YAML file is empty or invalid
    """
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError(f"YAML file is empty: {path}")

        return data

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format in {path}") from e


def write_yaml(path, data):
    """
    Write a dictionary to a YAML file.

    Args:
        path (str | Path): Path where YAML will be written
        data (dict): Data to serialize

    Raises:
        IOError: If the file cannot be written
        ValueError: If data is not a dictionary
    """
    try:
        if not isinstance(data, dict):
            raise ValueError("YAML data must be a dictionary")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    except yaml.YAMLError as e:
        raise ValueError(f"Failed to serialize YAML to {path}") from e


def update_yaml_param(path, key, value):
    """
    Update a nested YAML parameter using dot-notation and save the file.

    Args:
        path (str | Path): Path to the YAML file
        key (str): Dot-separated key (e.g. "training.batch_size")
        value (Any): New value to set

    Raises:
        KeyError: If the key path is invalid
        ValueError: If key is empty or YAML structure is invalid
    """
    if not key or not isinstance(key, str):
        raise ValueError("Key must be a non-empty string")

    data = read_yaml(path)
    keys = key.split(".")

    d = data
    try:
        for k in keys[:-1]:
            if not isinstance(d, dict):
                raise KeyError(f"Invalid key path at '{k}'")
            d = d.setdefault(k, {})
        d[keys[-1]] = value
    except Exception as e:
        raise KeyError(f"Failed to update key '{key}'") from e

    write_yaml(path, data)
