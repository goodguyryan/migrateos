"""Tests for paths.py: runtime detection and install command suggestions.

TODO:
    - test_detect_runtime_node() (package.json present)
    - test_detect_runtime_python_requirements() (requirements.txt)
    - test_detect_runtime_python_pyproject() (pyproject.toml)
    - test_detect_runtime_python_setup() (setup.py)
    - test_detect_runtime_java_maven() (pom.xml)
    - test_detect_runtime_java_gradle() (build.gradle)
    - test_detect_runtime_go() (go.mod)
    - test_detect_runtime_rust() (Cargo.toml)
    - test_detect_runtime_ruby() (Gemfile)
    - test_detect_runtime_php() (composer.json)
    - test_detect_runtime_none() (no marker files)
    - test_detect_runtime_multiple() (multiple markers)
    - test_suggest_install_returns_commands() (each runtime returns install commands)
"""
