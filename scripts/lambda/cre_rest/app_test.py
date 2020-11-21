import os
import unittest
from . import app
from pprint import pprint 
TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), "test_data.yaml")


class TestCRELambda(unittest.TestCase):
    expected = [{'CRE-ID-lookup-from-taxonomy-table': '011-040-026',
                    'CS': 'Session Management',
                    'CWE': 598,
                    'Description': 'Verify the application never reveals session tokens in URL '
                                    'parameters or error messages.',
                    'Development guide (does not exist for SessionManagement)': '',
                    'ID-taxonomy-lookup-from-ASVS-mapping': 'SESSION-MGT-TOKEN-DIRECTIVES-DISCRETE-HANDLING',
                    'Item': '3.1.1',
                    'Name': 'Session',
                    'OPC': '',
                    'Top10 (lookup)': 'https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control',
                    'WSTG': 'WSTG-SESS-04'},
                    {'CRE-ID-lookup-from-taxonomy-table': '011-040-033',
                    'CS': 'Session Management',
                    'CWE': 598,
                    'Description': 'Verify the application never reveals session tokens in URL '
                                    'parameters or error messages.',
                    'Development guide (does not exist for SessionManagement)': '',
                    'ID-taxonomy-lookup-from-ASVS-mapping': 'SESSION-MGT-TOKEN-DIRECTIVES-DISCRETE-HANDLING',
                    'Item': '3.1.1',
                    'Name': 'Session',
                    'OPC': '',
                    'Top10 (lookup)': 'https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control',
                    'WSTG': 'WSTG-SESS-04'}]

    def test_filter_all(self):
        self.maxDiff = None
        cre_file = TESTDATA_FILENAME
        with open(cre_file) as f:
            actual = app.filter_all(f)
            self.assertEqual(self.expected, actual, "actual doesn't match expected") 

    def test_filter_cre_id_no_data(self):
        self.maxDiff = None

        cre_file = TESTDATA_FILENAME
        with open(cre_file) as f:
            # empty cre_id == empty result test
            actual = app.filter_cre_id(f, "")
            self.assertEqual([], actual, "returned results while empty list should have been returned")

    def test_filter_cre_id_data(self):
        expected = [self.expected[1]]
        cre_file = TESTDATA_FILENAME
        cre_id = "011-040-033"
        with open(cre_file) as f:
            actual = app.filter_cre_id(f, cre_id)
            self.assertEqual(expected, actual, "actual doesn't match expected") 

    def test_filter_link_is_mentioned_in_cres_no_data(self):
        self.maxDiff = None
        cre_file = TESTDATA_FILENAME
        with open(cre_file,'r') as f:
            #  non existing link == empty result test
            actual = app.filter_link_is_mentioned_in_cres(f, 'foo', 'bar')
            self.assertEqual([], actual, "returned results while empty list should have been returned")
       
    def test_filter_link_is_mentioned_in_cres_data(self):
        cre_file = TESTDATA_FILENAME
        with open(cre_file,'r') as f:
                actual = app.filter_link_is_mentioned_in_cres(f, 'CWE', 598)
                self.assertEqual(self.expected, actual, "actual doesn't match expected") 
if __name__ == '__main__':
    unittest.main()
 
