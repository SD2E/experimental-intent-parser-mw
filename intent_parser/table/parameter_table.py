from intent_parser.intent_parser_exceptions import TableException, DictionaryMaintainerException
import intent_parser.constants.intent_parser_constants as intent_parser_constants
import intent_parser.table.table_utils as table_utils
import intent_parser.utils.intent_parser_utils as intent_parser_utils
import json
import logging

class ParameterTable(object):
    """
    Process information from Intent Parser's Parameter Table
    """

    _logger = logging.getLogger('src')
    
    FIELD_WITH_BOOLEAN_VALUE = [intent_parser_constants.PARAMETER_MEASUREMENT_INFO_36_HR_READ, 
                                intent_parser_constants.PARAMETER_RUN_INFO_READ_EACH_RECOVER,
                                intent_parser_constants.PARAMETER_RUN_INFO_READ_EACH_INDUCTION,
                                intent_parser_constants.PARAMETER_RUN_INFO_SAVE_FOR_RNASEQ, 
                                intent_parser_constants.PARAMETER_RUN_INFO_SKIP_FIRST_FLOW, 
                                intent_parser_constants.PARAMETER_RUN_INFO_ONLY_ENDPOINT_FLOW, 
                                intent_parser_constants.PARAMETER_VALIDATE_SAMPLES]
    
    FIELD_WITH_FLOAT_VALUE = [intent_parser_constants.PARAMETER_PLATE_READER_INFO_GAIN]
    
    FIELD_WITH_NESTED_STRUCTURE = [intent_parser_constants.PARAMETER_INDUCTION_INFO_REAGENTS_INDUCER, 
                                   intent_parser_constants.PARAMETER_MEASUREMENT_INFO_FLOW_INFO,
                                   intent_parser_constants.PARAMETER_MEASUREMENT_INFO_PLATE_READER_INFO, 
                                   intent_parser_constants.PARAMETER_REAGENT_INFO_INDUCER_INFO, 
                                   intent_parser_constants.PARAMETER_REAGENT_INFO_KILL_SWITCH,
                                   intent_parser_constants.PARAMETER_RECOVERY_INFO]
    
    FIELD_WITH_LIST_OF_STRING = [intent_parser_constants.PARAMETER_EXP_INFO_MEDIA_WELL_STRINGS]
     
    def __init__(self, parameter_fields={}):
        self._parameter_fields = parameter_fields
        self._validation_errors = []
        
    
    def parse_table(self, table):
        parameter_data = {}
        rows = table['tableRows']
        for row in rows[1:]:
            try:
                param_field, param_value_list = self._parse_row(rows[0], row)
                if len(param_value_list) == 0:
                    continue
                elif len(param_value_list) == 1:
                    parameter_data[param_field] = param_value_list[0]
                else:
                    for i in range(len(param_value_list)):
                        param_field_id = param_field + '.' + str(i)
                        parameter_data[param_field_id] = param_value_list[i]
            except ValueError as value_err:
                message = str(value_err)
                self._validation_errors.append(message)       
            except TableException as table_err:
                message = table_err.get_message()
                self._validation_errors.append(message)
            except DictionaryMaintainerException as dictionary_err:
                self._validation_errors.append(dictionary_err.get_message())
        return parameter_data
    
    def _parse_parameter_field_value(self, parameter_field, parameter_value):
        if parameter_field in self.FIELD_WITH_FLOAT_VALUE: 
            values = table_utils.extract_number_value(parameter_value)
            return parameter_field, [float(float_val) for float_val in values]
        elif parameter_field in self.FIELD_WITH_BOOLEAN_VALUE:
            parameter_value = parameter_value.lower()
            if parameter_value == 'false':
                return parameter_field, [False]
            elif parameter_value == 'true':
                return parameter_field, [True]
            else:
                raise TableException('Parameter table has invalid %s value: %s should be a boolean value' % (parameter_field, parameter_value))
        elif parameter_field in self.FIELD_WITH_LIST_OF_STRING:
            # Return the original form for parameters that contain a list of string 
            return parameter_field, [parameter_value] 
        elif parameter_field in self.FIELD_WITH_NESTED_STRUCTURE:
            json_parameter_value = json.loads(parameter_value)
            return parameter_field, [json_parameter_value] 
        
        return parameter_field, table_utils.transform_strateos_string(parameter_value)
    
    def _parse_row(self, header_row, row):
        num_cols = len(row['tableCells'])
        param_field = ''
        param_value = '' 
        for col_index in range(0, num_cols): 
            paragraph_element = header_row['tableCells'][col_index]['content'][0]['paragraph']
            header = intent_parser_utils.get_paragraph_text(paragraph_element).strip()
            cell_txt = ' '.join([intent_parser_utils.get_paragraph_text(content['paragraph']).strip() for content in row['tableCells'][col_index]['content']])
            
            if header == intent_parser_constants.COL_HEADER_PARAMETER:
                param_field = self._get_parameter_field(cell_txt)
            elif header == intent_parser_constants.COL_HEADER_PARAMETER_VALUE:
                param_value = cell_txt

        if not param_field:
            raise TableException('Parameter field should not be empty')
        
        if not param_value:
            return param_field, []
        
        return self._parse_parameter_field_value(param_field, param_value)        
            
    def _get_parameter_field(self, cell_txt):
        if not self._parameter_fields:
            raise DictionaryMaintainerException('There are no parameters that could map to a Strateos protocol')
        if cell_txt not in self._parameter_fields:
            raise TableException('%s does not map to a Strateos UID' % cell_txt)
        return self._parameter_fields[cell_txt]

    def get_validation_errors(self):
        return self._validation_errors