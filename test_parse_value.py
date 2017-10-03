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
