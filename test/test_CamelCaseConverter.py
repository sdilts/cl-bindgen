import unittest

from cl_bindgen.mangler import CamelCaseConverter

class CamelCaseConverterTest(unittest.TestCase):
    mangler = CamelCaseConverter()

    def test_title_case_converts(self):
        result = self.mangler.mangle('TestTitleCase')
        self.assertEqual('test-title-case', result)

    def test_converts_camelcase(self):
        result = self.mangler.mangle('camelCase')
        self.assertEqual('camel-case', result)

    def test_converts_all_lowercase(self):
        result = self.mangler.mangle('camels')
        self.assertEqual('camels', result)

    def test_converts_consective_at_end(self):
        result = self.mangler.mangle('ThingDNE')
        self.assertEqual('thing-dne', result)

    def test_converts_consective_at_begining(self):
        result = self.mangler.mangle('IString')
        self.assertEqual('istring', result)

    def test_converts_snakecase_names(self):
        result = self.mangler.mangle('GRAVITY_TOP_RIGHT')
        self.assertEqual('gravity_top_right', result)
