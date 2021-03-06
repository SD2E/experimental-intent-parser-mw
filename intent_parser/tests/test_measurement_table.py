from intent_parser.table.controls_table import ControlsTable
from intent_parser.table.measurement_table import MeasurementTable
from intent_parser.table.intent_parser_table_factory import IntentParserTableFactory
import unittest

class MeasurementTableTest(unittest.TestCase):
    """
    Test parsing information from a measurement table.
    """
    def setUp(self):
        self.ip_table_factory = IntentParserTableFactory()

    def tearDown(self):
        pass
              
    def test_table_with_measurement_type(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'measurement-type\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'FLOW\n'}}]}}]}]}]
        } 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, measurement_types={'PLATE_READER', 'FLOW'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEquals(meas_result[0]['measurement_type'], 'FLOW')

    def test_table_with_empty_file_type(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'file-type\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(0, len(meas_result))
    
    def test_table_with_file_type(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'file-type\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'FASTQ\n'}}]}}]}]}]
        } 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        meas_table = MeasurementTable(ip_table)
        ip_table.set_header_row_index(0)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEquals(1, len(meas_result[0]['file_type']))
        self.assertEquals(meas_result[0]['file_type'][0], 'FASTQ')  
    
    def test_table_with_1_replicate(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'replicate\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '3\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEquals(meas_result[0]['replicates'], 3) 
        
    def test_table_with_3_replicates(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'replicate\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '1,2,3\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEquals(meas_result[0]['replicates'], 1) 
    
    def test_table_with_1_strain(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'strains\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'AND_00\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEqual(1, len(meas_result[0]['strains']))
        self.assertEqual('AND_00', meas_result[0]['strains'][0]) 
    
    def test_strains_using_uri_as_string(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'strains\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'https://hub.sd2e.org/user/sd2e/design/UWBF_7376/1\n'}}]}}]}]}]
        } 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEqual(1, len(meas_result[0]['strains']))
        self.assertEqual('https://hub.sd2e.org/user/sd2e/design/UWBF_7376/1', meas_result[0]['strains'][0])    
        
    def test_table_with_1_timepoint(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'timepoint\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '3 hour\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, timepoint_units={'hour'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'value': 3.0, 'unit': 'hour'}
        self.assertEquals(1, len(meas_result[0]['timepoints']))
        self.assertDictEqual(exp_res1, meas_result[0]['timepoints'][0])
                  
    def test_table_with_3_timepoint(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'timepoint\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '6, 12, 24 hour\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, timepoint_units={'hour'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'value': 6.0, 'unit': 'hour'}
        exp_res2 = {'value': 12.0, 'unit': 'hour'}
        exp_res3 = {'value': 24.0, 'unit': 'hour'}
        self.assertEquals(3, len(meas_result[0]['timepoints']))
        for timepoint in meas_result[0]['timepoints']:
            self.assertFalse(timepoint != exp_res1 and timepoint != exp_res2 and timepoint != exp_res3)
    
    def test_table_with_1_temperature(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'temperature\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '1 fahrenheit\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, temperature_units={'fahrenheit'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'value': 1.0, 'unit': 'fahrenheit'}
        self.assertEquals(1, len(meas_result[0]['temperatures']))
        self.assertDictEqual(exp_res1, meas_result[0]['temperatures'][0]) 
        
    def test_table_with_1_temperature_and_unspecified_unit(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'temperature\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '1 dummy\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, temperature_units={'celsius', 'fahrenheit'})
        meas_result = meas_table.process_table()
        self.assertEquals(0, len(meas_result))
        
    
    def test_table_with_2_temperature_and_unit_abbreviation(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'temperature\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '3, 2, 1 C\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, temperature_units={'celsius'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'value': 3.0, 'unit': 'celsius'}
        exp_res2 = {'value': 2.0, 'unit': 'celsius'}
        exp_res3 = {'value': 1.0, 'unit': 'celsius'}
        self.assertEquals(3, len(meas_result[0]['temperatures']))
        for temperature in meas_result[0]['temperatures']:
            self.assertFalse(temperature != exp_res1 and temperature != exp_res2 and temperature != exp_res3)  
             
    def test_table_with_3_temperature(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'temperature\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '3, 2, 1 celsius\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, temperature_units={'celsius'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'value': 3.0, 'unit': 'celsius'}
        exp_res2 = {'value': 2.0, 'unit': 'celsius'}
        exp_res3 = {'value': 1.0, 'unit': 'celsius'}
        self.assertEquals(3, len(meas_result[0]['temperatures']))
        for temperature in meas_result[0]['temperatures']:
            self.assertFalse(temperature != exp_res1 and temperature != exp_res2 and temperature != exp_res3)  
    
    def test_table_with_samples(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'samples\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '5, 10, 15\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(0, len(meas_result))
    
    def test_table_with_notes(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'notes\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'A simple string\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(0, len(meas_result))
    
    def test_table_with_1_ods(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'ods\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '3\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEquals(1, len(meas_result[0]['ods']))
        self.assertListEqual([3.0], meas_result[0]['ods'])
        
    def test_table_with_3_ods(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'ods\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '33, 22, 11\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEquals(3, len(meas_result[0]['ods']))
        self.assertListEqual([33.0, 22.0, 11.0], meas_result[0]['ods'])
        
    def test_table_with_one_value_reagent(self):
        reagent_name = 'L-arabinose'
        reagent_uri = 'https://hub.sd2e.org/user/sd2e/design/Larabinose/1'
        
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': reagent_name, 'textStyle': {'link': {'url': reagent_uri}
                        }}},
                {'textRun': {
                    'content': '\n'}}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '9 mM\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, fluid_units={'%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : reagent_name, 'sbh_uri' : reagent_uri}, 'value' : '9', 'unit' : 'mM'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
            
    def test_table_with_three_value_reagent(self):
        reagent_name = 'L-arabinose'
        reagent_uri = 'https://hub.sd2e.org/user/sd2e/design/Larabinose/1'
        
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': reagent_name, 'textStyle': {'link': {'url': reagent_uri}
                        }}},
                {'textRun': {
                    'content': '\n'}}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '0, 1, 2 micromole\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, fluid_units={'%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : reagent_name, 'sbh_uri' : reagent_uri}, 'value' : '0', 'unit' : 'micromole'}
        exp_res2 = {'name' : {'label' : reagent_name, 'sbh_uri' : reagent_uri}, 'value' : '1', 'unit' : 'micromole'}
        exp_res3 = {'name' : {'label' : reagent_name, 'sbh_uri' : reagent_uri}, 'value' : '2', 'unit' : 'micromole'}
        self.assertEquals(3, len(meas_result[0]['contents'][0]))
        for act_res in meas_result[0]['contents'][0]:
            self.assertFalse(act_res != exp_res1 and act_res != exp_res2 and act_res != exp_res3)
            
    def test_table_with_reagent_and_unit_abbreviation(self):
        reagent_name = 'L-arabinose'
        reagent_uri = 'https://hub.sd2e.org/user/sd2e/design/Larabinose/1'
        
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': reagent_name, 'textStyle': {'link': {'url': reagent_uri}
                        }}},
                {'textRun': {
                    'content': '\n'}}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '1 fold\n'}}]}}]}]}]
        } 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, fluid_units={'%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : reagent_name, 'sbh_uri' : reagent_uri}, 'value' : '1', 'unit' : 'X'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
    
    def test_table_with_reagent_and_percentage_unit(self):
        reagent_name = 'L-arabinose'
        reagent_uri = 'https://hub.sd2e.org/user/sd2e/design/Larabinose/1'
        
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': reagent_name, 'textStyle': {'link': {'url': reagent_uri}
                        }}},
                {'textRun': {
                    'content': '\n'}}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '11 %\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, fluid_units={'%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : reagent_name, 'sbh_uri' : reagent_uri}, 'value' : '11', 'unit' : '%'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
        
    def test_table_with_reagent_and_unit_containing_backslash(self):
        reagent_name = 'L-arabinose'
        reagent_uri = 'https://hub.sd2e.org/user/sd2e/design/Larabinose/1'
        
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': reagent_name, 'textStyle': {'link': {'url': reagent_uri}}
                        }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '11 g/L\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, fluid_units={'%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : reagent_name, 'sbh_uri' : reagent_uri}, 'value' : '11', 'unit' : 'g/L'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
        
    def test_table_with_reagent_and_timepoint(self):
        reagent_uri = 'https://hub.sd2e.org/user/sd2e/design/beta0x2Destradiol/1'
        
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'SC_Media @ 18 hour', 'textStyle': {'link': {'url': reagent_uri}}
                        }}
                ]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '0 M\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, timepoint_units={'hour'}, fluid_units={'%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : 'SC_Media', 'sbh_uri' : 'NO PROGRAM DICTIONARY ENTRY'}, 'value' : '0', 'unit' : 'M', 
                    'timepoint' : {'value' : 18.0, 'unit' : 'hour'}}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])

    def test_table_text_with_reagent_and_timepoint(self):
        reagent_uri = 'https://hub.sd2e.org/user/sd2e/design/IPTG/1'

        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'IPTG', 'textStyle': {'link': {'url': reagent_uri}}
                        }}, {'textRun': {
                'content': '@ 40 hours'}}
                ]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'NA\n'}}]}}]}]}]
        }

        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table, timepoint_units={'hour'}, fluid_units={'%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L'})
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))

        exp_res1 = {'name' : {'label' : 'IPTG', 'sbh_uri' : reagent_uri}, 'value' : 'NA',
                    'timepoint' : {'value' : 40.0, 'unit' : 'hour'}}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])

    def test_table_with_media(self):
        media_uri = 'https://hub.sd2e.org/user/sd2e/design/Media/1'
        input_table ={'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Media','textStyle': {'link': {'url': media_uri}, 'bold': True}}},
                    {'textRun': {
                        'content': '\n'}}
                  ]}}]}]} ,
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'sc_media\n'}}]}}]}]}]
        } 
 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : 'Media', 'sbh_uri' : media_uri}, 'value' : 'sc_media'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
     
    def test_table_with_media_containing_period_values(self):
        input_table ={'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'media','textStyle': {'bold': True}}},
                    {'textRun': {
                        'content': '\n'}}
                  ]}}]}]} ,
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Yeast_Extract_Peptone_Adenine_Dextrose (a.k.a. YPAD Media)\n'}}]}}]}]}]
        } 
 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : 'media', 'sbh_uri' : 'NO PROGRAM DICTIONARY ENTRY'}, 
                    'value' : 'Yeast_Extract_Peptone_Adenine_Dextrose (a.k.a. YPAD Media)'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
        
    def test_table_with_media_containing_percentage_values(self):
        input_table ={'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'media','textStyle': {'bold': True}}},
                    {'textRun': {
                        'content': '\n'}}
                  ]}}]}]} ,
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Synthetic_Complete_2%Glycerol_2%Ethanol\n'}}]}}]}]}]
        } 
 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : 'media', 'sbh_uri' : 'NO PROGRAM DICTIONARY ENTRY'}, 'value' : 'Synthetic_Complete_2%Glycerol_2%Ethanol'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
    
    def test_table_with_media_containing_numerical_values(self):
        input_table ={'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'media','textStyle': {'bold': True}}},
                    {'textRun': {
                        'content': '\n'}}
                  ]}}]}]} ,
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'SC+Glucose+Adenine+0.8M\n'}}]}}]}]}]
        } 
 
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        
        exp_res1 = {'name' : {'label' : 'media', 'sbh_uri' : 'NO PROGRAM DICTIONARY ENTRY'}, 'value' : 'SC+Glucose+Adenine+0.8M'}
        self.assertEquals(1, len(meas_result[0]['contents'][0]))
        self.assertEquals(exp_res1, meas_result[0]['contents'][0][0])
        
    def test_table_with_batch_values(self):
        input_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'batch\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': '0, 1\n'}}]}}]}]}]
        } 
    
        ip_table = self.ip_table_factory.from_google_doc(input_table)
        ip_table.set_header_row_index(0)
        meas_table = MeasurementTable(ip_table)
        meas_result = meas_table.process_table()
        self.assertEquals(1, len(meas_result))
        self.assertEquals(meas_result[0]['batch'], [0,1])
        
    def test_table_with_1_reference_control(self):
        measurement_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 2\n'}}]}}]}]}]
        }
        control_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 2: Control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Control Type\n' }}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Strains\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'HIGH_FITC\n'}}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'UWBF_25784\n' }}]}}]}]}]
        }
        ip_measurement_table = self.ip_table_factory.from_google_doc(measurement_table)
        ip_measurement_table.set_header_row_index(0)
        ip_control_table = self.ip_table_factory.from_google_doc(control_table)
        ip_control_table.set_caption_row_index(0)
        ip_control_table.set_header_row_index(1)
        
        control_parser = ControlsTable(ip_control_table, control_types={'HIGH_FITC'})
        control_result = control_parser.process_table()
        
        measurement_parser = MeasurementTable(ip_measurement_table)
        meas_result = measurement_parser.process_table(control_tables={control_parser.get_table_caption(): control_result})
        self.assertEquals(1, len(meas_result))
        self.assertEquals(1, len(meas_result[0]['controls']))
        control = meas_result[0]['controls'][0]
        self.assertEqual(control['type'], 'HIGH_FITC')
        self.assertListEqual(control['strains'], ['UWBF_25784'])
    
    def test_table_with_2_reference_control_in_one_measurement(self): 
        measurement_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 1, Table 2\n'}}]}}]}]}]
        }
        control_table1 = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 1: Control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Control Type\n' }}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Strains\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'HIGH_FITC\n'}}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'UWBF_25784\n' }}]}}]}]}]
        }
        control_table2 = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 2: Control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Control Type\n' }}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Strains\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'foo\n'}}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'UWBF_6390\n','textStyle': {'link': {'url': 'https://hub.sd2e.org/user/sd2e/design/UWBF_6390/1'}
                        } }}]}}]}]}]
        }
        ip_measurement_table = self.ip_table_factory.from_google_doc(measurement_table)
        ip_measurement_table.set_header_row_index(0)
        
        ip_control_table1 = self.ip_table_factory.from_google_doc(control_table1)
        ip_control_table1.set_caption_row_index(0)
        ip_control_table1.set_header_row_index(1)
        
        ip_control_table2 = self.ip_table_factory.from_google_doc(control_table2)
        ip_control_table2.set_caption_row_index(0)
        ip_control_table2.set_header_row_index(1)
        
        control1_parser = ControlsTable(ip_control_table1, control_types={'HIGH_FITC'})
        control1_result = control1_parser.process_table()
        control2_parser = ControlsTable(ip_control_table2, control_types={'foo'})
        control2_result = control2_parser.process_table()
        
        measurement_parser = MeasurementTable(ip_measurement_table)
        meas_result = measurement_parser.process_table(control_tables={control1_parser.get_table_caption(): control1_result,
                                                                       control2_parser.get_table_caption(): control2_result})
        self.assertEquals(1, len(meas_result))
        self.assertEquals(2, len(meas_result[0]['controls']))
        
        control1 = meas_result[0]['controls'][0]
        self.assertEqual(control1['type'], 'HIGH_FITC')
        self.assertListEqual(control1['strains'], ['UWBF_25784'])
        control2 = meas_result[0]['controls'][1]
        self.assertEqual(control2['type'], 'foo')
        self.assertListEqual(control2['strains'], ['UWBF_6390'])
    
    def test_table_with_2_reference_control_in_seperate_measurements(self): 
        measurement_table = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 1\n'}}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 2\n'}}]}}]}]}]
        }
        control_table1 = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 1: Control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Control Type\n' }}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Strains\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'HIGH_FITC\n'}}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'UWBF_25784\n' }}]}}]}]}]
        }
        control_table2 = {'tableRows': [
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Table 2: Control\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Control Type\n' }}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'Strains\n' }}]}}]}]},
            {'tableCells': [{'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'foo\n'}}]}}]}, {'content': [{'paragraph': {'elements': [{'textRun': {
                'content': 'UWBF_6390\n','textStyle': {'link': {'url': 'https://hub.sd2e.org/user/sd2e/design/UWBF_6390/1'}
                        } }}]}}]}]}]
        }
        ip_measurement_table = self.ip_table_factory.from_google_doc(measurement_table)
        ip_measurement_table.set_header_row_index(0)
        
        ip_control_table1 = self.ip_table_factory.from_google_doc(control_table1)
        ip_control_table1.set_caption_row_index(0)
        ip_control_table1.set_header_row_index(1)
        
        ip_control_table2 = self.ip_table_factory.from_google_doc(control_table2)
        ip_control_table2.set_caption_row_index(0)
        ip_control_table2.set_header_row_index(1)
        
        control1_parser = ControlsTable(ip_control_table1, control_types={'HIGH_FITC'})
        control1_result = control1_parser.process_table()
        control2_parser = ControlsTable(ip_control_table2, control_types={'foo'})
        control2_result = control2_parser.process_table()
        
        measurement_parser = MeasurementTable(ip_measurement_table)
        meas_result = measurement_parser.process_table(control_tables={control1_parser.get_table_caption(): control1_result,
                                                                       control2_parser.get_table_caption(): control2_result})
        self.assertEquals(2, len(meas_result))
        self.assertEquals(1, len(meas_result[0]['controls']))
        
        control1 = meas_result[0]['controls'][0]
        self.assertEqual(control1['type'], 'HIGH_FITC')
        self.assertListEqual(control1['strains'], ['UWBF_25784'])
        control2 = meas_result[1]['controls'][0]
        self.assertEqual(control2['type'], 'foo')
        self.assertListEqual(control2['strains'], ['UWBF_6390'])
      
        
if __name__ == '__main__':
    unittest.main()