import unittest
import warnings
import json
import getopt
import sys
import os
import time
import urllib.request
import pickle

from unittest.mock import Mock, patch, DEFAULT

try:
    from intent_parser_server import IntentParserServer
except Exception as e:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../src'))
    from intent_parser_server import IntentParserServer

from google_accessor import GoogleAccessor


class TestIntentParserServer(unittest.TestCase):

    spellcheckFile = 'doc_1xMqOx9zZ7h2BIxSdWp2Vwi672iZ30N_2oPs8rwGUoTA.json'

    spellcheckResults = 'spell_results.pickle'

    dataDir = 'data'
    
    def compare_spell_results(self, r1, r2):
        """
        Compares two spellcheck search results to see if they are equal.
        r1 and r2 are lists of search results, where each result contains a term, selection start, and selection end.
        """
        if not len(r1) == len(r2):
            return False

        for idx in range(len(r1)):
            entry1 = r1[idx]
            entry2 = r2[idx]
            if not entry1['term'] == entry2['term']:
                return False
            if not entry1['select_start']['paragraph_index'] == entry2['select_start']['paragraph_index']:
                return False
            if not entry1['select_start']['cursor_index']    == entry2['select_start']['cursor_index']:
                return False
            if not entry1['select_start']['element_index']   == entry2['select_start']['element_index']:
                return False
            if not entry1['select_end']['paragraph_index'] == entry2['select_end']['paragraph_index']:
                return False
            if not entry1['select_end']['cursor_index']    == entry2['select_end']['cursor_index']:
                return False
            if not entry1['select_end']['element_index']   == entry2['select_end']['element_index']:
                return False

        return True

    def setUp(self):
        """
        Configure an instance of IntentParserServer for spellcheck testing.
        """
        self.doc_content = None
        with open(os.path.join(self.dataDir,self.spellcheckFile), 'r') as fin:
            self.doc_content = json.loads(fin.read())

        if self.doc_content is None:
            self.fail('Failed to read in test document! Path: ' + os.path.join(self.dataDir,self.spellcheckFile))
        
        # Clear all dictionary information
        if os.path.exists(IntentParserServer.dict_path):
            for file in os.listdir(IntentParserServer.dict_path):
                os.remove(os.path.join(IntentParserServer.dict_path, file))
            os.rmdir(IntentParserServer.dict_path)

        self.doc_id = '1xMqOx9zZ7h2BIxSdWp2Vwi672iZ30N_2oPs8rwGUoTA'
        self.user = 'bbnTest'
        self.user_email = 'test@bbn.com'
        self.json_body = {'documentId' : self.doc_id, 'user' : self.user, 'userEmail' : self.user_email}

        self.ips = IntentParserServer(initialize=False)
        self.ips.client_state_lock = Mock()
        self.ips.client_state_map = {}
        self.ips.google_accessor = Mock()
        self.ips.google_accessor.get_document = Mock(return_value=self.doc_content)
        self.ips.send_response = Mock()
        self.ips.get_json_body = Mock(return_value=self.json_body)
        
        self.ips.process_add_by_spelling([], [])
        
        self.spelling_gt = None
        with open(os.path.join(self.dataDir, self.spellcheckResults), 'rb') as fin:
            self.spelling_gt = pickle.load(fin)

        if self.spelling_gt is None:
            self.fail('Failed to read in spelling results! Path: ' + os.join(self.dataDir, self.spellcheckResults))

    def test_spellcheck_basic(self):
        """
        Basic check, ensure that spellcheck runs and the results are as expected
        """
        # Basic sanity checks
        self.assertTrue(self.ips.client_state_map[self.doc_id]['user_id'] == self.user_email)
        self.assertTrue(self.ips.client_state_map[self.doc_id]['document_id'] == self.doc_id)
        self.assertTrue(self.ips.client_state_map[self.doc_id]['spelling_size'] is 164)
        self.assertTrue(self.ips.client_state_map[self.doc_id]['spelling_index'] is 0)
        self.assertTrue(self.compare_spell_results(self.spelling_gt, self.ips.client_state_map[self.doc_id]['spelling_results']), 'Spelling result sets do not match!')
    
    def test_spellcheck_add_dictionary(self):
        """
        Test the ability to add a term into the spelling dictionary
        """
        remove_term = 'proteomics'
        # Find the index of the first instance of 'proteomics'
        first_proteomics_idx = 0
        while not self.ips.client_state_map[self.doc_id]['spelling_results'][first_proteomics_idx]['term'] == remove_term:
            first_proteomics_idx += 1  
        self.ips.client_state_map[self.doc_id]['spelling_index'] = first_proteomics_idx
        
        # Remove proteomics
        self.ips.spellcheck_add_dictionary([], self.ips.client_state_map[self.doc_id])
        
        # The GT should not match
        self.assertFalse(self.compare_spell_results(self.spelling_gt, self.ips.client_state_map[self.doc_id]['spelling_results']), 'Spelling result sets should not match!')
        
        # We expected to remove 15 results
        self.assertTrue(self.ips.client_state_map[self.doc_id]['spelling_size'] is 149)
        
        # Compare to removed entry
        spelling_gt_no_prot = [res for res in self.spelling_gt if not res['term'] == remove_term]
        self.assertTrue(self.compare_spell_results(spelling_gt_no_prot, self.ips.client_state_map[self.doc_id]['spelling_results'])) 

    def tearDown(self):
        pass


if __name__ == '__main__':
    print('Run unit tests')

    unittest.main(argv=[sys.argv[0]])
