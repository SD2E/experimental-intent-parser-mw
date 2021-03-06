from intent_parser.table.cell_parser import CellParser
from intent_parser.table.intent_parser_cell import IntentParserCell
import unittest

class CellParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = CellParser()

    def tearDown(self):
        pass
    
    def test_reagent_header_without_timepoint(self):
        cell = IntentParserCell()
        cell.add_paragraph('name1')
        name, _ = self.parser.process_reagent_header(cell, units={'hour'}, unit_type='timepoints')
        self.assertEqual('name1', name['label'])
    
    def test_reagent_alphanumeric_header_with_timepoint(self):
        cell = IntentParserCell()
        cell.add_paragraph('BE1 @ 15 hours')
        name, timepoint = self.parser.process_reagent_header(cell, units={'hour'}, unit_type='timepoints')
        self.assertEqual('BE1', name['label'])
        self.assertEqual('NO PROGRAM DICTIONARY ENTRY', name['sbh_uri'])
        self.assertEqual(timepoint['value'], 15.0)
        self.assertEqual(timepoint['unit'], 'hour')
            
    def test_reagent_header_with_timepoint(self):
        cell = IntentParserCell()
        cell.add_paragraph('name @ 15 hours')
        name, timepoint = self.parser.process_reagent_header(cell, units={'hour'}, unit_type='timepoints')
        self.assertEqual('name', name['label'])
        self.assertEqual('NO PROGRAM DICTIONARY ENTRY', name['sbh_uri'])
        self.assertEqual(timepoint['value'], 15.0)
        self.assertEqual(timepoint['unit'], 'hour')
        
    def test_parse_content_item_with_name(self):
        cell = IntentParserCell()
        cell.add_paragraph('name')
        results = self.parser.parse_content_item(cell)
        self.assertEqual(len(results), 1)
        result = results[0]
        name = result['name']
        self.assertEqual(2, len(name))
        self.assertEqual('name', name['label'])
        self.assertEqual('NO PROGRAM DICTIONARY ENTRY', name['sbh_uri'])
        
    def test_parse_content_item_with_list_of_names(self):
        cell = IntentParserCell()
        cell.add_paragraph('name1, name2, name3')
        results = self.parser.parse_content_item(cell)
        self.assertEqual(len(results), 3)
        name1 = results[0]['name']
        name2 = results[1]['name']
        name3 = results[2]['name']
        self.assertEqual(name1, {'label': 'name1', 'sbh_uri': 'NO PROGRAM DICTIONARY ENTRY'})
        self.assertEqual(name2, {'label': 'name2', 'sbh_uri': 'NO PROGRAM DICTIONARY ENTRY'})
        self.assertEqual(name3, {'label': 'name3', 'sbh_uri': 'NO PROGRAM DICTIONARY ENTRY'})
        
    def test_parse_content_item_with_name_value_unit(self):
        cell = IntentParserCell()
        cell.add_paragraph('name1 123 unit')
        results = self.parser.parse_content_item(cell, timepoint_units={'unit', 'timeunit'})
        self.assertEqual(len(results), 1)
        result = results[0]
        name = result['name']
        self.assertEqual(2, len(name))
        self.assertEqual('name1', name['label'])
        self.assertEqual('NO PROGRAM DICTIONARY ENTRY', name['sbh_uri'])
        self.assertEqual('123', result['value'])
        self.assertEqual('unit', result['unit'])
        
    def test_parse_content_item_with_name_value_unit_timepoint(self):
        cell = IntentParserCell()
        cell.add_paragraph('name1 name2 123 unit @ 15 timeunit')
        results = self.parser.parse_content_item(cell, timepoint_units={'unit', 'timeunit'})
        self.assertEqual(len(results), 1)
        result = results[0]
        name = result['name']
        timepoints = result['timepoints']
        self.assertEqual(2, len(name))
        self.assertEquals(1, len(timepoints))
        self.assertEqual('name1 name2', name['label'])
        self.assertEqual('NO PROGRAM DICTIONARY ENTRY', name['sbh_uri'])
        self.assertEqual('123', result['value'])
        self.assertEqual('unit', result['unit'])
        self.assertEqual(15.0, timepoints[0]['value'])
        self.assertEqual('timeunit', timepoints[0]['unit'])
        
    def test_parse_content_item_with_name_uri_value_unit(self):
        cell = IntentParserCell()
        cell.add_paragraph('name1', link='https://hub.sd2e.org/user/sd2e/design/beta_estradiol/1')
        cell.add_paragraph('123 unit')
        results = self.parser.parse_content_item(cell, timepoint_units={'unit', 'timeunit'})
        self.assertEqual(len(results), 1)
        result = results[0]
        name = result['name']
        self.assertEqual(2, len(name))
        self.assertEqual('name1', name['label'])
        self.assertEqual('https://hub.sd2e.org/user/sd2e/design/beta_estradiol/1', name['sbh_uri'])
        self.assertEqual('123', result['value'])
        self.assertEqual('unit', result['unit'])

    def test_names_without_separators(self):
        cell = IntentParserCell()
        cell.add_paragraph('foo')
        self.assertTrue(self.parser.is_name(cell))
        
    def test_names_with_separators(self):
        cell = IntentParserCell()
        cell.add_paragraph('one, two X')
        self.assertTrue(self.parser.is_name(cell))
        
    def test_names_from_numerical_values(self):
        cell = IntentParserCell()
        cell.add_paragraph('1, 2')
        self.assertFalse(self.parser.is_name(cell))
        
    def test_numbers(self):
        cell = IntentParserCell()
        cell.add_paragraph('1, 2')
        self.assertTrue(self.parser.is_number(cell))
    
    def test_number(self):
        cell = IntentParserCell()
        cell.add_paragraph('12')
        self.assertTrue(self.parser.is_number(cell))
            
    def test_numbers_with_unit(self):
        cell = IntentParserCell()
        cell.add_paragraph('12, 24 X')
        self.assertFalse(self.parser.is_number(cell))
        
    def test_is_value(self):
        cell = IntentParserCell()
        cell.add_paragraph('1 X')
        self.assertTrue(self.parser.is_valued_cell(cell))
        
    def test_is_value_with_pairing_units(self):
        cell = IntentParserCell()
        cell.add_paragraph('1 X, 2 unit, 3 mm')
        self.assertTrue(self.parser.is_valued_cell(cell))
        
    def test_is_value_with_ending_unit(self):
        cell = IntentParserCell()
        cell.add_paragraph('1, 2, 3 X')
        self.assertTrue(self.parser.is_valued_cell(cell))
    
    def test_is_value_with_starting_unit(self):
        cell = IntentParserCell()
        cell.add_paragraph('1 X, 2, 3')
        self.assertFalse(self.parser.is_valued_cell(cell))
        
    def test_value_unit(self):
        cell = IntentParserCell()
        cell.add_paragraph('3 hour')
        result = self.parser.process_values_unit(cell, units={'hour'}, unit_type='timepoints')
        self.assertEqual(1, len(result))
        self.assertEqual({'value': 3.0, 'unit': 'hour'}, result[0])
        
    def test_leading_values_unit(self):
        cell = IntentParserCell()
        cell.add_paragraph('1, 2,3 hour')
        result = self.parser.process_values_unit(cell, units={'hour'}, unit_type='timepoints')
        self.assertEqual(3, len(result))
        self.assertEqual({'value': 1.0, 'unit': 'hour'}, result[0])   
        self.assertEqual({'value': 2.0, 'unit': 'hour'}, result[1])   
        self.assertEqual({'value': 3.0, 'unit': 'hour'}, result[2])   
        
    def test_value_unit_pairs(self):
        cell = IntentParserCell()
        cell.add_paragraph('1 X, 2 mM ,3 micromole')
        result = self.parser.process_values_unit(cell, units={'X', 'mM', 'micromole'}, unit_type='fluid')
        self.assertEqual(3, len(result))
        self.assertEqual({'value': 1.0, 'unit': 'X'}, result[0])   
        self.assertEqual({'value': 2.0, 'unit': 'mM'}, result[1])   
        self.assertEqual({'value': 3.0, 'unit': 'micromole'}, result[2]) 
    
    def test_false_table_caption(self):
        cell = IntentParserCell()
        cell.add_paragraph('foo 1: a table caption')
        self.assertFalse(self.parser.is_table_caption(cell))
        
    def test_table_caption_case_sensitive(self):
        cell = IntentParserCell()
        cell.add_paragraph('table 1:')
        self.assertTrue(self.parser.is_table_caption(cell))
        
    def test_is_table_caption_keyword(self):
        cell = IntentParserCell()
        cell.add_paragraph('Table 1')
        self.assertTrue(self.parser.is_table_caption(cell))
        
    def test_is_table_caption_with_description(self):
        cell = IntentParserCell()
        cell.add_paragraph('Table 1: a table caption')
        self.assertTrue(self.parser.is_table_caption(cell))
        
    def test_is_table_caption_without_spaces(self):
        cell = IntentParserCell()
        cell.add_paragraph('Table1:Controls')
        self.assertTrue(self.parser.is_table_caption(cell))
    
    def test_get_table_caption(self):
        cell = IntentParserCell()
        cell.add_paragraph('Table1:Controls')
        self.assertEqual('table1', self.parser.process_table_caption(cell))
        
if __name__ == "__main__":
    unittest.main()