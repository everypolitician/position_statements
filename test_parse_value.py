from position_statements import parse_value

def test_parse_value_item_id():
    assert parse_value('Q42') == {
        'type': 'wikibase-entityid',
        'value': {
            'entity-type': 'item', 'id': 'Q42'
        }
    }

def test_parse_value_string():
    assert parse_value('" hello, i\'m a "string"  \"') == {
        'type': 'string',
        'value': 'hello, i\'m a "string"',
    }

def test_parse_value_time():
    assert parse_value('+2000-01-20T00:04:35Z/11') == {
        'type': 'time',
        'value': {
            'time': '+2000-01-20T00:04:35Z',
            'precision': 11
        }
    }

def test_parse_value_statement_raw_uuid():
    assert parse_value('Q42-DD45AFB0-7249-4690-AAE3-86C9FF996CE2') == {
        'type': 'x-wikidata-statementid',
        'value': 'Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2',
    }

def test_parse_value_statement_api_uuid():
    assert parse_value('Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2') == {
        'type': 'x-wikidata-statementid',
        'value': 'Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2',
     }

def test_parse_value_statement_wds_uuid():
    assert parse_value('wds:Q42-DD45AFB0-7249-4690-AAE3-86C9FF996CE2') == {
        'type': 'x-wikidata-statementid',
        'value': 'Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2',
    }
