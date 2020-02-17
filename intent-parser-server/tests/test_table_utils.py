from intent_parser_exceptions import TableException
import table_utils as tu
import unittest

class TableUtilsTest(unittest.TestCase):
    """Unit test for table_utils class"""

    def test_cell_with_propagated_unit(self):
        cell_str = '1 X, 2 X, 3 X'
        expected_values = ['1', '2', '3']
        for value, unit in tu.transform_cell(cell_str, ['X'], cell_type='fluid'):
           self.assertEqual(unit, 'X')
           self.assertTrue(value in expected_values) 
           
    def test_cell_without_propagated_unit(self):
        cell_str = '1, 2, 3 X'
        expected_values = ['1', '2', '3']
        for value, unit in tu.transform_cell(cell_str, ['X'], cell_type='fluid'):
           self.assertEqual(unit, 'X')
           self.assertTrue(value in expected_values) 

    def test_cell_without_units(self):
        cell_str = '1, 2, 3'
        expected_values = ['1', '2', '3']
        with self.assertRaises(TableException):
            value, unit = tu.transform_cell(cell_str, ['X'], cell_type='fluid')

    def test_cell_with_unit_abbreviation(self):
        cell_str = '1, 2, 3 fold'
        expected_values = ['1', '2', '3']
        for value, unit in tu.transform_cell(cell_str, ['X'], cell_type='fluid'):
           self.assertEqual(unit, 'X')
           self.assertTrue(value in expected_values)
    
    def test_cell_with_unspecified_unit(self):
        cell_str = '1, 2, 3 foo'
        with self.assertRaises(TableException):
            value, unit = tu.transform_cell(cell_str, ['X'], cell_type='fluid')
    
    def test_cell_with_incorrect_unit_location(self):
        cell_str = '1 X, 2, 3'
        with self.assertRaises(TableException):
            value, unit = tu.transform_cell(cell_str, ['X'], cell_type='fluid')
    
    def test_cell_with_incorrect_unit_value_swapped(self):
        cell_str = '1, 2, X 3'
        with self.assertRaises(TableException):
            value, unit = tu.transform_cell(cell_str, ['X'], cell_type='fluid')
    
    def test_cell_with_unit_without_spacing(self):
        cell_str = '1X'
        for value, unit in tu.transform_cell(cell_str, ['X'], cell_type='fluid'):
           self.assertEqual(unit, 'X')
           self.assertEqual('1', value)
           
    def test_cell_with_multiple_value_unit_without_space(self):
        cell_str = '1X,2X,3X'
        expected_values = ['1', '2', '3']
        for value, unit in tu.transform_cell(cell_str, ['X'], cell_type='fluid'):
           self.assertEqual(unit, 'X')
           self.assertTrue(value in expected_values)
           
    def test_cell_with_single_value(self):
        cell_str = '1 X'
        expected_values = ['1']
        for value, unit in tu.transform_cell(cell_str, ['X'], cell_type='fluid'):
           self.assertEqual(unit, 'X')
           self.assertTrue(value in expected_values)       

    def test_cell_with_nonvalues(self):
        cell_str = 'one, two X'
        with self.assertRaises(TableException):
            value, unit = tu.transform_cell(cell_str, ['X'], cell_type='fluid')

    def test_cell_not_type_value_unit(self):
        cell_str = 'A simple string'
        with self.assertRaises(TableException):
            value, unit = tu.transform_cell(cell_str, ['celsius', 'fahrenheit'], cell_type='temperature')
                
    
    def test_cell_without_cell_type(self):
        cell_str = '1, 2 hour'
        expected_values = ['1', '2']
        for value, unit in tu.transform_cell(cell_str, ['hour']):
            self.assertEqual(unit, 'hour')
            self.assertTrue(value in expected_values) 
    
    def test_cell_values_with_numbers(self):
        cell_str = '1, 2'
        expected_values = ['1', '2']
        self.assertListEqual(expected_values, tu.extract_number_value(cell_str))
        
    def test_cell_values_with_name_containing_underscore_numbers(self):
        cell_str = 'AND_00, NAND_00'
        expected_values = ['AND_00', 'NAND_00']
        self.assertListEqual(expected_values, tu.extract_name_value(cell_str))
        
    def test_cell_values_with_long_name(self):
        cell_str = 'B_subtilis_WT_JH642_Colony_1, B_subtilis_WT_JH642_Colony_2, B_subtilis_WT_JH642_Colony_3'
        expected_values = ['B_subtilis_WT_JH642_Colony_1', 
                           'B_subtilis_WT_JH642_Colony_2', 
                           'B_subtilis_WT_JH642_Colony_3']
        self.assertListEqual(expected_values, tu.extract_name_value(cell_str)) 
         
    
    def test_cell_values_without_underscore(self):
        cell_str = 'CSV, FCS'
        expected_values = ['CSV', 'FCS']
        self.assertListEqual(expected_values, tu.extract_name_value(cell_str))
    
    def test_cell_values_with_one_name(self):
        cell_str = 'CSV'
        expected_values = ['CSV']
        self.assertListEqual(expected_values, tu.extract_name_value(cell_str))
    
    def test_cell_is_number(self):  
        self.assertTrue(tu.is_number('3'))
        
    def test_cell_list_is_number(self):
        self.assertTrue(tu.is_number('3, 5, 7'))
    
    def test_cell_list_is_number(self):
        self.assertFalse(tu.is_number('3, X'))
        
    def test_cell_is_number_with_unit(self):
        self.assertFalse(tu.is_number('3 X'))
    
    def test_cell_unit_is_not_number(self):
        self.assertFalse(tu.is_number('x'))
        
    def test_extract_number_value_with_unit(self):
        self.assertListEqual(['1', '2'], tu.extract_number_value('1, 2 X'))
        
    def test_cell_values_with_special_character(self):
        for value,unit in tu.transform_cell('8 %', ['%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L']):
            self.assertEqual('8', value)
            self.assertEqual('%', unit)
        
    def test_cell_values_with_backslash(self):
        for value,unit in tu.transform_cell('9 g/L', ['%', 'M', 'mM', 'X', 'micromole', 'nM', 'g/L']):
            self.assertEqual('9', value)
            self.assertEqual('g/L', unit)
    
    def test_cell_values_with_exponent(self):
        self.assertTrue(tu.is_number('5e-06'))  
        self.assertTrue(tu.is_number('5e+06'))  
        self.assertTrue(tu.is_number('5e06'))  
        self.assertTrue(tu.is_number('2.05e7'))  
        self.assertFalse(tu.is_number('2.0e.07'))  
        self.assertFalse(tu.is_number('2.0e'))  
                             
    def test_cell_values_with_named_spacing(self):
        cell_str = 'Yeast_Extract_Peptone_Adenine_Dextrose (a.k.a. YPAD Media)'   
        for name in tu.extract_name_value(cell_str):
            self.assertEquals(cell_str, name)
    
    def test_cell_values_with_named_and_numerical_spacing(self):
        cell_str = 'B. subtilis 168 PmtlA-comKS'   
        for name in tu.extract_name_value(cell_str):
            self.assertEquals(cell_str, name)
    
    def test_cell_with_trailing_whitespace(self):
        cell_str = 'Yeast1_, Yeast2_, Yeast3_ '
        exp_res = ['Yeast1_', 'Yeast2_', 'Yeast3_']
        for name in tu.extract_name_value(cell_str):
            self.assertTrue(name in exp_res)

    def test_cell_with_number_name(self):
        cell_str = '5 microliter'
        actual_res = tu.transform_number_name_cell(cell_str)   
        self.assertEquals(1, len(actual_res))
        self.assertEquals('5:microliter', actual_res[0])
        
    def test_cell_with_name(self):
        cell_str = 'sc_media'
        actual_res = tu.transform_number_name_cell(cell_str)   
        self.assertEquals(1, len(actual_res))
        self.assertEquals('sc_media', actual_res[0])
    
    def test_cell_with_numbered_list(self):
        cell_str = '0.1, 0.2, 0.3'
        actual_res = tu.transform_number_name_cell(cell_str)   
        self.assertEquals(3, len(actual_res))
        self.assertEquals('0.1', actual_res[0])    
        self.assertEquals('0.2', actual_res[1]) 
        self.assertEquals('0.3', actual_res[2])    
                        
    def test_cell_with_unit_containing_multiple_abbreviations(self):
        cell_str = '1 h, 2 hr, 3 hours'
        expected_values = ['1', '2', '3']
        for value, unit in tu.transform_cell(cell_str, ['hour'], cell_type='timepoints'):
           self.assertEqual(unit, 'hour')
           self.assertTrue(value in expected_values)
          
    def test_cell_with_unicode_characters(self):
        cell_str = '\x0bApp'
        self.assertTrue('App', tu.extract_name_value(cell_str))
        
        
        
if __name__ == "__main__":
    unittest.main()