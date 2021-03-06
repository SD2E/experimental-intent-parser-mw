from intent_parser.table.intent_parser_table_factory import IntentParserTableFactory
from intent_parser.table.parameter_table import ParameterTable
import unittest

class ParameterTableTest(unittest.TestCase):
    """
    Test parsing contents from a parameter table
    """
    
    @classmethod
    def setUpClass(self):
        self.parameter_fields = {
            'Flow cytometer configuration' : 'measurement_info.flow_info',
            'Induction inducer'            : 'induction_info.induction_reagents.inducer',
            'Inoculation increment time 1' : 'inoc_info.inc_time_1',
            'Inoculation media'            : 'inoc_info.inoculation_media',
            'Inoculation media volume'     : 'inoc_info.inoc_media_vol',
            'Inoculation volume'           : 'inoc_info.inoc_vol',
            'Kill switch'                  : 'reagent_info.kill_switch',
            'Media well ids'               : 'exp_info.media_well_strings',
            'Plate reader gain'            : 'plate_reader_info.gain',
            'Sample has sbh_uri as an aliquot property' : 'validate_samples'
            }
    
    def setUp(self):
        self.ip_table_factory = IntentParserTableFactory()
        
    def test_parameter_field_with_empty_value(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Inoculation volume\n'}}]}}]}]}]
        } 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(0, len(param_result))
       
    def test_parameter_string_value_with_colon_separator(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Inoculation volume\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '5 microliter\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        self.assertEqual('5:microliter', param_result['inoc_info.inoc_vol'])
    
    def test_parameter_string_value_with_list_of_numbers(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Media well ids\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '94,95\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        self.assertEqual('94,95', param_result['exp_info.media_well_strings'])
        
    def test_one_parameter_string_value_without_colon_separator(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Inoculation media\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'sc_media\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        self.assertEqual('sc_media', param_result['inoc_info.inoculation_media'])
    
    def test_two_parameter_string_value_without_colon_separator(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Inoculation media\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'S750, Modified M9 Media\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        expected_result = {'inoc_info.inoculation_media.0': 'S750', 
                           'inoc_info.inoculation_media.1' : 'Modified M9 Media'}
        self.assertEqual(2, len(param_result))
        self.assertDictEqual(expected_result, param_result)
    
    def test_parameter_string_for_hardcoded_kill_switch_json_values(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Kill switch\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': ' {"value": "false", "inputs": {"false": {}}}\n'
                }}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        expected_output = {
            "value": "false",
            "inputs": {
                "false": {}
            }
        }

        self.assertEqual(expected_output, param_result['reagent_info.kill_switch'])
    
    def test_parameter_string_for_hardcoded_measurement_info_flow_info_json_values(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Flow cytometer configuration\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '{"do_flow": {"value": "every-sampling","inputs": {"every-sampling": {"flow_params" : "yeast"}}}}\n'
                }}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        expected_output = {
            "do_flow": {
                "value": "every-sampling",
                "inputs": {
                    "every-sampling": {
                        "flow_params" : "yeast"
                    }
                }
            }
        }

        self.assertEqual(expected_output, param_result['measurement_info.flow_info'])
        
    def test_parameter_string_for_hardcoded_induction_info_induction_reagents_inducer_json_values(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Induction inducer\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '{"containerId" : "ct1e262bek47rkx","wellIndex" : 0}\n'
                }}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        expected_output = {
            "containerId" : "ct1e262bek47rkx",
            "wellIndex" : 0
        }
        self.assertEqual(expected_output, param_result['induction_info.induction_reagents.inducer'])
    
    def test_parameter_boolean_value(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Sample has sbh_uri as an aliquot property\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'false\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        self.assertEqual(False, param_result['validate_samples'])
    
    def test_parameter_with_case_insensitive_boolean_value(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Sample has sbh_uri as an aliquot property\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'FaLse\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        self.assertEqual(False, param_result['validate_samples'])
    
    def test_parameter_with_non_boolean_value(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Sample has sbh_uri as an aliquot property\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'neither\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(0, len(param_result))
       
    def test_parameter_with_one_float_value(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Plate reader gain\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '0.1\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        self.assertEqual(1, len(param_result))
        self.assertEqual(0.1, param_result['plate_reader_info.gain'])
    
    def test_parameter_with_three_float_values(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Parameter\n' }}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Value\n' }}]}}]}
            ]},
            
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Plate reader gain\n'}}]}}]},
                {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '0.1, 0.2, 0.3\n'}}]}}]}
            ]}
        ]} 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        param_table = ParameterTable(ip_table, parameter_fields=self.parameter_fields)
        param_result = param_table.process_table()
        expected_result = {'plate_reader_info.gain.0': 0.1, 
                           'plate_reader_info.gain.1' : 0.2,
                           'plate_reader_info.gain.2' : 0.3}
        self.assertEqual(3, len(param_result))
        self.assertDictEqual(expected_result, param_result)
 
if __name__ == "__main__":
    unittest.main()