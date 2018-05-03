from collections import OrderedDict
from os.path import join

from hdx.utilities.downloader import Download
from hdx.utilities.loader import load_json
from hdx.utilities.saver import save_json


def get_rule(rule_template, iso3, adm=None):
    rule = OrderedDict()
    for key in rule_template:
        value = rule_template[key]
        if isinstance(value, str):
            value = value.replace('{ISO}', iso3.lower())
            if adm:
                value = value.replace('{ADM}', str(adm))
        rule[key] = value
    return rule


def schemacreator(start_url, base_url, template_path, output_folder):
    with Download() as downloader:
        response = downloader.download(start_url)
        countryisos = set()
        for service in response.json()['services']:
            servicenameright = service['name'].split('/')[1]
            iso3 = servicenameright[:3]
            countryisos.add(iso3)

        template = load_json(template_path)
        for iso3 in sorted(countryisos):
            print(iso3)
            url = base_url % iso3
            response = downloader.download(url)
            adminlevels = set()
            for layer in response.json()['layers']:
                layername = layer['name'].lower()
                if 'feature' in layer['type'].lower() and 'admin' in layername and not 'lines' in layername:
                    adminlevel = int(layername[-1])
                    if adminlevel > 0:
                        adminlevels.add(adminlevel)
            adminlevels = sorted(list(adminlevels))
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
            save_json(schema, join(output_folder, 'validation-schema-pcodes-%s.json' % iso3.lower()), pretty=True)


if __name__ == '__main__':
    start_url = 'http://gistmaps.itos.uga.edu/arcgis/rest/services/COD_External?f=pjson'
    base_url = 'http://gistmaps.itos.uga.edu/arcgis/rest/services/COD_External/%s_pcode/MapServer/layers?f=pjson'
    template_path = join('..', 'validation-schema-pcodes.json')
    output_folder = join('..', 'pcodes')
    schemacreator(start_url, base_url, template_path, output_folder)
