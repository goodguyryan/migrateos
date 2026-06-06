"""Tests for ansible_generator.py: verify generated Ansible project structure and content.

TODO:
    - test_generated_output_structure_exists() (all files and folders present)
    - test_site_yml_references_role() (site.yml has migrated_server role)
    - test_inventory_has_change_me() (inventory.ini contains ansible_host=CHANGE_ME)
    - test_group_vars_has_expected_keys() (new_server.yml has packages, services, users, etc.)
    - test_group_vars_service_tier_split() (infrastructure before application)
    - test_handlers_exist() (handlers/main.yml is not empty)
    - test_main_yml_import_order() (import order matches spec: bootstrap -> verification)
    - test_warnings_md_has_secrets_section() (when secrets present)
    - test_warnings_md_no_secrets_section() (when no secrets)
    - test_warnings_md_has_databases_section() (when databases detected)
    - test_requirements_yml_has_ansible_posix()
    - test_template_variable_construction() (verify computed booleans, service splits)
"""
