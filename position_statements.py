import pywikibot
import sys
import re
from pathlib import Path

# Regular expressions copied from http://tinyurl.com/yb37xlu7
item_re = re.compile('^[PQ]\d+$', re.IGNORECASE)
string_re = re.compile('^"(.*)"$', re.IGNORECASE)
time_re = re.compile(
    '^([+-]{0,1})(\d+)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)Z\/{0,1}(\d*)$',
    re.IGNORECASE
)


def entity_type(value):
    if value.startswith('Q'):
        return 'item'
    elif value.startswith('P'):
        return 'property'
    else:
        return 'unknown'


def parse_value(value):
    value = value.strip()

    m = item_re.match(value)
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
        return {'type': 'string', 'value': value}

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


def expanded_datavalue(datavalue):
    if datavalue['type'] == 'wikibase-entityid':
        entity = pywikibot.ItemPage(repo, datavalue['value']['id'])
        entity.get()
        return entity
    elif datavalue['type'] == 'string':
        return datavalue['value']
    elif datavalue['type'] == 'time':
        time = pywikibot.WbTime.fromTimestr(datavalue['value']['time'])
        time.precision = datavalue['value']['precision']
        return time


if len(sys.argv) == 1:
    sys.exit("Usage: %s <filename>" % sys.argv[0])

p = Path(sys.argv[1])

if not p.is_file():
    sys.exit('"%s" is not a file' % sys.argv[1])

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
    for p, v in qualifier_pairs:
        q = {'property': p, 'datavalue': parse_value(v)}
        command['qualifiers'].append(q)
    # TODO: Validate that items start with Q and properties start with P
    commands.append(command)

for command in commands:
    # Get the item we want to modify
    item = pywikibot.ItemPage(repo, command['item'])
    item.get()

    # Get the claim we're dealing with
    claim = pywikibot.Claim(site, command['property'])

    # Create a new P39 statement pointing to Q123
    claim.setTarget(expanded_datavalue(command['datavalue']))

    # Add the claim to the item.
    item.addClaim(claim)

    for qualifier in command['qualifiers']:
        qualifier_claim = pywikibot.Claim(
            site, qualifier['property'], isQualifier=True
        )
        qualifier_claim.setTarget(expanded_datavalue(qualifier['datavalue']))
        claim.addQualifier(qualifier_claim)
