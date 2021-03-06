from os.path import join

from hdx.utilities.compare import assert_files_same

from tempfile import gettempdir
from run.schemacreator import schemacreator


class TestSchemaCreator:
    def test_schemacreator(self):
        start_url = 'https://raw.githubusercontent.com/OCHA-DAP/tools-datacheck-validation/master/tests/fixtures/COD_External.json'
        base_url = 'https://raw.githubusercontent.com/OCHA-DAP/tools-datacheck-validation/master/tests/fixtures/%s_layers.json'
        template_path = 'validation-schema-pcodes.json'
        output_folder = gettempdir()
        schemacreator(start_url, base_url, template_path, output_folder)
        expected = join('tests', 'fixtures', 'validation-schema-pcodes-syr.json')
        result = join(output_folder, 'validation-schema-pcodes-syr.json')
        assert_files_same(expected, result)
