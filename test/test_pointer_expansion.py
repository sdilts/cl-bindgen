import unittest

from cl_bindgen.pointer_expansion import process_pointer_expansion_rules

class PointerExpansionTest(unittest.TestCase):

    def test_include_and_empty_match_field(self):
        try:
            rules = {
                'include': {}
            }
            process_pointer_expansion_rules(rules, 'names')
        except Exception as e:
            self.fail('process_pointer_expansion_rules failed with exception',
                      e)

    def test_exclude_and_empty_match_field(self):
        try:
            rules = {
		'include': {}
	    }
            process_pointer_expansion_rules(rules, 'names')
        except Exception as e:
            self.fail('process_pointer_expansion_rules failed with exception',
                      e)

    def test_whitelist_list_works(self):
        allowed = ['foo', 'bar', 'baz']
        rules = {
            'include': {
                'names': allowed
            }
        }
        result = process_pointer_expansion_rules(rules, 'names')
        self.assertTrue(all([ result(i) for i in allowed]))
        self.assertFalse(result('fooBar'))

    def test_blacklist_list_works(self):
        banned = ['foo', 'bar', 'baz']
        rules = {
            'exclude': {
	        'names': banned
            }
        }
        result = process_pointer_expansion_rules(rules, 'names')
        self.assertTrue(all([ not result(i) for i in banned]))
        self.assertTrue(result('fooBar'))

    def test_whitelist_blacklist_list_works(self):
        banned = ['foo', 'bar', 'baz']
        allowed = ['foo', 'cheese', 'curds']
        rules = {
            'exclude': {
                'names': banned
            },
            'include': {
                'names': allowed
            }
        }
        result = process_pointer_expansion_rules(rules, 'names')
        self.assertTrue(all([ not result(i) for i in banned]))
        actual_allowed = ['cheese', 'curds']
        self.assertTrue(all([ result(i) for i in actual_allowed]))
        self.assertFalse(result('fish'))
