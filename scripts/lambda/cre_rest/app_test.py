import os
import unittest
from . import function
TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), "test_data.yaml")


class TestCRELambda(unittest.TestCase):

    def test_filter_all(self):
        self.maxDiff = None
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

        cre_file = TESTDATA_FILENAME
        with open(cre_file) as f:
            actual = function.filter_all(f)
            self.assertEqual(expected, actual, "actual doesn't match expected") 

    def test_filter_cre_id(self):
        self.maxDiff = None
        expected = [
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

        cre_file = TESTDATA_FILENAME
        cre_id = "011-040-033"
        actual = ""
        with open(cre_file) as f:
            # empty cre_id == empty result test
            actual = function.filter_cre_id(f, "")
            self.assertEqual([], actual, "returned results while empty list should have been returned")

            f.seek(0)
            actual = function.filter_cre_id(f, cre_id)
            self.assertEqual(expected, actual, "actual doesn't match expected") 

    def test_filter_link_is_mentioned_in_cres(self):
        self.maxDiff = None
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

        cre_file = TESTDATA_FILENAME
        actual = ""
        with open(cre_file) as f:
            #  non existing link == empty result test
            actual = function.filter_link_is_mentioned_in_cres(f, 'foo', 'bar')
            self.assertEqual([], actual, "returned results while empty list should have been returned")

            f.seek(0)
            actual = function.filter_link_is_mentioned_in_cres(f, 'cwe', 598)
            self.assertEqual(expected, actual, "actual doesn't match expected") 
        # self.fail()


if __name__ == '__main__':
    unittest.main()
 
