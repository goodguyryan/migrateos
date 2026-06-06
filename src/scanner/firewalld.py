"""Scan firewalld configuration: zones, services, ports, rich rules, direct rules, ipsets, policies.

TODO:
    - _list_zones() -> List[str] (firewall-cmd --get-zones)
    - _parse_zone_list_all(text: str) -> dict (parse --list-all output: services, ports, masquerade, target, etc.)
    - _parse_rich_rules(text: str) -> List[str] (parse --list-rich-rules output)
    - _parse_direct_rules() -> dict (firewall-cmd --direct --get-all-rules)
    - _scan_custom_services() -> List[dict] (scan /etc/firewalld/services/*.xml, skip stock service names)
    - _scan_custom_ipsets() -> List[dict] (scan /etc/firewalld/ipsets/*.xml)
    - _parse_ipsets(text: str) -> List[str] (firewall-cmd --get-ipsets)
    - _parse_policies(text: str) -> List[str] (firewall-cmd --get-policies)
    - collect() -> dict (orchestrate all, skip if firewalld not running)
    - Return: {enabled, default_zone, zones: [...], custom_services_xml, custom_ipsets_xml, policies, direct_rules_xml}
"""
