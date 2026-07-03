def test_parse_xml_string_parses_nmap_xml():
    from vulnbot.safe_xml import parse_xml_string

    root = parse_xml_string(
        '<?xml version="1.0"?><nmaprun><host><status state="up"/></host></nmaprun>'
    )
    assert root.tag == "nmaprun"
