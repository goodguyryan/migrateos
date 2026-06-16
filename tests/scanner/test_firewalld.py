"""Tests for firewalld.py: zone, service, port, rich-rule, direct-rule, ipset, and policy parsing.

TODO:
    - test_parse_zone_list_all_services()
    - test_parse_zone_list_all_ports()
    - test_parse_zone_list_all_masquerade() (masquerade: yes/no → boolean)
    - test_parse_zone_list_all_target()
    - test_parse_zone_list_all_empty() (no config in zone → empty defaults)
    - test_parse_rich_rules_multiple()
    - test_parse_rich_rules_empty()
    - test_parse_ipsets() (ipsets output → parsed list)
    - test_parse_direct_rules() (direct rules split into ipv4/ipv6/ebtables)
    - test_scan_custom_services_skips_stock() (ssh.xml skipped, custom.xml kept)
"""
