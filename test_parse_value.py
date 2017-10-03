from unittest.mock import Mock

import pytest

from position_statements import get_existing_claim, parse_value

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

def test_get_existing_claim_unknown_property():
    mock_item = Mock(claims={})
    with pytest.raises(Exception) as excinfo:
        get_existing_claim(
            mock_item,
            'P123456',
            'Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2'
        )
    assert 'No property P123456 found in claims of' in str(excinfo.value)

def test_get_claim_missing():
    mock_item = Mock(claims={'P123456': []})
    mock_item.__str__ = Mock()
    mock_item.__str__.return_value = '<Item: Some item or other>'
    with pytest.raises(Exception) as excinfo:
        get_existing_claim(
            mock_item,
            'P123456',
            'Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2'
        )
    assert 'The snak Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2 was ' \
        'not found for any claim on \'<Item: Some item or other>\' ' \
        'with property P123456' in str(excinfo.value)

def test_get_claim_found():
    mock_claim = Mock(snak='Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2')
    mock_item = Mock(claims={'P123456': [mock_claim]})
    assert get_existing_claim(
        mock_item,
        'P123456',
        'Q42$DD45AFB0-7249-4690-AAE3-86C9FF996CE2'
    ) is mock_claim
