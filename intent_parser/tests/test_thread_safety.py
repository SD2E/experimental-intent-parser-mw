from intent_parser.server.http_message import HttpMessage
from intent_parser.server.intent_parser_server import IntentParserServer
from http import HTTPStatus
from unittest.mock import Mock, patch
import unittest

class TestThreadSafety(unittest.TestCase):

    @patch('intent_parser.intent_parser_factory.IntentParserFactory')
    @patch('intent_parser.accessor.strateos_accessor.StrateosAccessor')
    @patch('intent_parser.accessor.sbol_dictionary_accessor.SBOLDictionaryAccessor')
    @patch('intent_parser.intent_parser_sbh.IntentParserSBH')
    def setUp(self, mock_intent_parser_sbh, mock_sbol_dictionary_accessor, mock_strateos_accessor,
              mock_intent_parser_factory):
        self.mock_intent_parser_sbh = mock_intent_parser_sbh
        self.mock_sbol_dictionary_accessor = mock_sbol_dictionary_accessor
        self.mock_strateos_accessor = mock_strateos_accessor
        self.mock_intent_parser_factory = mock_intent_parser_factory

        self.mock_intent_parser = Mock()
        self.mock_intent_parser_factory.create_intent_parser.return_value = self.mock_intent_parser

        self.ip_server = IntentParserServer(self.mock_intent_parser_sbh, self.mock_sbol_dictionary_accessor,
                                            self.mock_strateos_accessor, self.mock_intent_parser_factory, 'localhost',
                                            8081)

    def tearDown(self):
        pass

    def test_thread_safety_on_sequential_requests(self):
        expected_structured_request = {'foo': 'bar'}
        number_of_runs = 10
        try:
            for _ in range(number_of_runs):
                self.mock_intent_parser.get_structured_request.return_value = expected_structured_request
                self.mock_intent_parser.get_validation_errors.return_value = []

                http_message = HttpMessage()
                http_message.resource = '/document_request?foo'
                response = self.ip_server.process_document_request(http_message)
        except HTTPStatus.INTERNAL_SERVER_ERROR as e:
            self.assertFail('Encountered internal server error when running %d document requests in sequential order' % number_of_runs)


if __name__ == '__main__':
    unittest.main()
