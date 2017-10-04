import pywikibot
import sys
import re
import time
from pathlib import Path

# Regular expressions copied from http://tinyurl.com/yb37xlu7
item_or_property_re = re.compile('^[PQ]\d+$', re.IGNORECASE)
item_re = re.compile('^Q\d+$', re.IGNORECASE)
property_re = re.compile('^P\d+$', re.IGNORECASE)
string_re = re.compile('^"(.*)"$', re.IGNORECASE)
time_re = re.compile(
    '^([+-]{0,1})(\d+)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)Z\/{0,1}(\d*)$',
    re.IGNORECASE
)
uuid_re = r'(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\Z'
statement_re = re.compile(r'(wds:)?(?P<q>Q\d+)[-\$]' + uuid_re, re.I)

def entity_type(value):
    if value.startswith('Q'):
        return 'item'
    elif value.startswith('P'):
        return 'property'
    else:
        return 'unknown'


def parse_value(value):
    value = value.strip()

    m = item_or_property_re.match(value)
    if m is not None:
        return {
            'type': 'wikibase-entityid',
            'value': {
                'entity-type': entity_type(value),
                'id': value.upper()
            }
        }

    m = string_re.match(value)
    if m is not None:
        return {'type': 'string', 'value': m.group(1).strip()}

    m = time_re.match(value)
    if m is not None:
        precision = 9
        if m.group(8) != '':
            precision = int(m.group(8))
        return {
            'type': 'time',
            'value': {
                'time': re.sub(r'\/\d+$', '', value),
                'precision': precision
            }
        }

    m = statement_re.match(value)
    if m:
        return {
            'type': 'x-wikidata-statementid',
            'value': m.group('q') + '$' + m.group('uuid')
        }

    sys.exit("Unrecognised value: {}".format(value))


def expanded_datavalue(datavalue):
    if datavalue['type'] == 'wikibase-entityid':
        entity = pywikibot.ItemPage(repo, datavalue['value']['id'])
        try:
            entity.get()
        except pywikibot.IsRedirectPage:
            entity = entity.getRedirectTarget()
        return entity
    elif datavalue['type'] == 'string':
        return datavalue['value']
    elif datavalue['type'] == 'time':
        time = pywikibot.WbTime.fromTimestr(datavalue['value']['time'])
        time.precision = datavalue['value']['precision']
        return time


def get_existing_claim(item, property_id, statement_uuid):
    if property_id not in item.claims:
        raise Exception('No property {} found in claims of {}'.format(
            property_id, item
        ))
    for claim in item.claims[property_id]:
        if claim.snak == statement_uuid:
            return claim
    msg = 'The snak {statement_uuid} was not found for any claim on ' \
          '\'{item}\' with property {property_id}'
    raise Exception(msg.format(
        statement_uuid=statement_uuid,
        item=item,
        property_id=property_id,
    ))

if __name__ == '__main__':

    if len(sys.argv) == 1:
        sys.exit("Usage: %s <filename> [<user_for_attribution>]" % sys.argv[0])

    p = Path(sys.argv[1])

    if not p.is_file():
        sys.exit('"%s" is not a file' % sys.argv[1])

    try:
        user_name = sys.argv[2]
    except IndexError:
        user_name = None

    site = pywikibot.Site()
    repo = site.data_repository()

    with p.open() as f:
        statements_string = f.read()

    statements = [s for s in statements_string.split("\n") if s.strip() != '']

    commands = []

    # Parse statements
    for statement in statements:
        command = {}
        parts = [s.strip() for s in statement.split("\t")]
        command['item'] = parts[0]
        command['property'] = parts[1]
        command['datavalue'] = parse_value(parts[2])
        qualifiers = parts[3:]
        qualifier_pairs = list(zip(qualifiers[::2], qualifiers[1::2]))
        command['qualifiers'] = []
        command['sources'] = []
        for p, v in qualifier_pairs:
            what = 'sources' if p.startswith('S') else 'qualifiers'
            prop = re.sub(r'^S', 'P', p)
            q = {'property': prop, 'datavalue': parse_value(v)}
            command[what].append(q)

        # Validate statements
        m = item_re.match(command['item'])
        if m is None:
            sys.exit("Invalid item ID format: {}".format(command['item']))

        if command['property'] != 'P39':
            sys.exit("Only P39 statements are supported currently. (Got {})".format(command['property']))

        if len(qualifiers) % 2 != 0:
            sys.exit("Odd number of qualifier/source pairs detected: {}".format(qualifiers))

        for qualifier in command['qualifiers']:
            m = property_re.match(qualifier['property'])
            if m is None:
                sys.exit("Invalid qualifier property: {}".format(qualifier['property']))

        for source in command['sources']:
            m = property_re.match(source['property'])
            if m is None:
                sys.exit("Invalid source property: {}".format(source['property']))

        # Validations passed, add to list of commands.
        commands.append(command)

    for command in commands:
        print(command)
        summary = 'Edited with PositionStatements'
        if user_name:
            summary += ' on behalf of [[User:{}]]'.format(user_name)

        # Get the item we want to modify
        item = pywikibot.ItemPage(repo, command['item'])
        try:
            item.get()
        except pywikibot.IsRedirectPage:
            item = item.getRedirectTarget()

        if command['datavalue']['type'] == 'x-wikidata-statementid':
            claim = get_existing_claim(
                item,
                command['property'],
                command['datavalue']['value'],
            )
        else:
            # Get the claim we're dealing with
            claim = pywikibot.Claim(site, command['property'])

            # Create a new P39 statement pointing to Q123
            claim.setTarget(expanded_datavalue(command['datavalue']))

            # Add the claim to the item.
            item.addClaim(claim, summary=summary)

        for qualifier in command['qualifiers']:
            qualifier_claim = pywikibot.Claim(
                site, qualifier['property'], isQualifier=True
            )
            qualifier_claim.setTarget(expanded_datavalue(qualifier['datavalue']))
            claim.addQualifier(qualifier_claim, summary=summary)

        sources = []
        for source in command['sources']:
            source_claim = pywikibot.Claim(
                site, source['property'], isReference=True
            )
            source_claim.setTarget(expanded_datavalue(source['datavalue']))
            sources.append(source_claim)
        if sources:
            claim.addSources(sources, summary=summary)
