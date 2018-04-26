import json
import re
from collections import OrderedDict
from os.path import join

from bs4 import BeautifulSoup
from hdx.utilities.downloader import Download

start_url = 'http://gistmaps.itos.uga.edu/arcgis/rest/services/COD_External'
base_url = 'http://gistmaps.itos.uga.edu/arcgis/rest/services/COD_External/%s_pcode/FeatureServer'


def get_rule(rule_template, iso3, adm=None):
    rule = OrderedDict()
    for key in rule_template:
        value = rule_template[key]
        if isinstance(value, str):
            value = value.replace('{ISO}', iso3)
            if adm:
                value = value.replace('{ADM}', adm)
        rule[key] = value
    return rule


with Download() as downloader:
    response = downloader.download(start_url)
    soup = BeautifulSoup(response.text, 'html5lib')
    countryisos = set()
    for element in soup.findAll(text=re.compile('.*pcode.*')):
        elementstr = str(element)
        ind = elementstr.find('pcode')
        iso3 = elementstr[ind-4:ind-1]
        countryisos.add(iso3)
    with open('validation-schema-pcodes.json', 'rt') as f:
        template = json.loads(f.read(), object_pairs_hook=OrderedDict)
        for iso3 in sorted(countryisos):
            print(iso3)
            url = base_url % iso3
            response = downloader.download(url)
            soup = BeautifulSoup(response.text, 'html5lib')
            adminlevels = list()
            for element in soup.findAll(text=re.compile('Admin[1-5]')):
                adminlevels.append(str(element)[-1])
            print(adminlevels)
            schema = list()
            admrules = list()
            for rule_template in template:
                if '{ADM}' in str(rule_template):
                    admrules.append(rule_template)
                else:
                    for adminlevel in adminlevels:
                        for admrule in admrules:
                            schema.append(get_rule(admrule, iso3, adminlevel))
                    admrules = list()
                    schema.append(get_rule(rule_template, iso3))
            for adminlevel in adminlevels:
                for admrule in admrules:
                    schema.append(get_rule(admrule, iso3, adminlevel))
            with open(join('pcodes', 'validation-schema-pcodes-%s.json' % iso3), 'w') as outfile:
                json.dump(schema, outfile, indent=2)

