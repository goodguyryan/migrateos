"""Tests for yaml_utils.py: YAML save/load roundtrip integrity."""

from src.utils.yaml_utils import load_yaml, save_yaml

def test_save_load_roundtrip_simple_dict(temp_dir):
    data = {"name": "test", "version": 1}
    path = temp_dir / "manifest.yml"
    save_yaml(data, path)
    assert load_yaml(path) == data


def test_save_load_roundtrip_nested_dict(temp_dir):
    data = {"server": {"hostname": "web01", "ip": "10.0.0.1"}}
    path = temp_dir / "nested.yml"
    save_yaml(data, path)
    assert load_yaml(path) == data


def test_save_load_roundtrip_with_lists(temp_dir):
    data = {"packages": ["nginx", "python3", "git"]}
    path = temp_dir / "lists.yml"
    save_yaml(data, path)
    assert load_yaml(path) == data


def test_load_missing_file_returns_empty_dict(temp_dir):
    path = temp_dir / "does_not_exist.yml"
    assert load_yaml(path) == {}


def test_load_empty_file_returns_empty_dict(temp_dir):
    path = temp_dir / "empty.yml"
    path.write_text("")
    assert load_yaml(path) == {}


def test_save_creates_parent_directories(temp_dir):
    path = temp_dir / "deep" / "nested" / "output.yml"
    save_yaml({"key": "value"}, path)
    assert path.is_file()
    assert load_yaml(path) == {"key": "value"}