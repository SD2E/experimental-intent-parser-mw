from intent_parser.intent_parser_exceptions import TableException
import intent_parser.constants.intent_parser_constants as intent_parser_constants
import intent_parser.table.cell_parser as cell_parser
import logging

class ControlsTable(object):
    """
    Process information from Intent Parser's Controls Table
    """
    _logger = logging.getLogger('intent_parser')
    
    def __init__(self, intent_parser_table, control_types={}, fluid_units={}, timepoint_units={}):
        self._control_types = control_types
        self._fluid_units = fluid_units
        self._timepoint_units = timepoint_units
        self._validation_errors = []
        self._validation_warnings = []
        self._intent_parser_table = intent_parser_table 
        self._table_caption = ''
    
    def get_table_caption(self):
        return self._table_caption
    
    def process_table(self):
        controls = []
        self._table_caption = self._intent_parser_table.caption()
        for row_index in range(self._intent_parser_table.data_row_index(), self._intent_parser_table.number_of_rows()):
            control_data = self._process_row(row_index)
            controls.append(control_data)
        return controls 
         
    def _process_row(self, row_index):
        row = self._intent_parser_table.get_row(row_index)
        control_data = {}
        timepoint = None 
        for cell_index in range(len(row)):
            cell = self._intent_parser_table.get_cell(row_index, cell_index)
            # Cell type based on column header
            header_row_index = self._intent_parser_table.header_row_index()
            header_cell = self._intent_parser_table.get_cell(header_row_index, cell_index)
            cell_type = cell_parser.PARSER.get_header_type(header_cell)
            if not cell.get_text() :
                continue
            if 'CONTROL_TYPE' == cell_type:
                control_type = self._process_control_type(cell)
                if control_type:
                    control_data['type'] = control_type
            elif 'STRAINS' == cell_type:
                strains = self._process_control_strains(cell)    
                if strains:
                    control_data['strains'] = strains
            elif 'CHANNEL' == cell_type:
                channel = self._process_channels(cell)
                if channel:
                    control_data['channel'] = channel
            elif 'CONTENTS' == cell_type:
                contents = self._process_contents(cell)
                if contents:
                    control_data['contents'] = contents
            elif 'TIMEPOINT' == cell_type:
                timepoint = self._process_timepoint(cell)
                control_data['timepoints'] = timepoint 
                
        return control_data 
    
    def _process_channels(self, cell):
        cell_content = cell.get_text()
        if not cell_parser.PARSER.is_name(cell):
            message = ('Controls table has invalid %s value: '
                       'Identified %s as a numerical value when ' 
                       'expecting alpha-numeric values.') % (intent_parser_constants.COL_HEADER_CONTROL_CHANNEL, cell.get_text())
            self._validation_errors.append(message)
            return None  
        list_of_channels = cell_parser.PARSER.process_names(cell)
        if len(list_of_channels) > 1:
            message = ('Controls table for %s has more than one channel provided. '
                       'Only the first channel will be used from %s.') % (intent_parser_constants.COL_HEADER_CONTROL_CHANNEL, cell_content)
            self._logger.warning(message)
        return list_of_channels[0]
    
    def _process_contents(self, cell):
        try:
            return cell_parser.PARSER.parse_content_item(cell, fluid_units=self._fluid_units, timepoint_units=self._timepoint_units)
        except TableException as err:
            message = 'Controls table has invalid %s value: %s' % (intent_parser_constants.COL_HEADER_CONTROL_CONTENT, err.get_message())
            self._validation_errors.append(message)
            return []
        
    def _process_control_strains(self, cell):
        if cell_parser.PARSER.is_valued_cell(cell):
            message = ('Controls table has invalid %s value: %s' 
                       'Identified %s as a numerical value when '
                       'expecting alpha-numeric values.') % (intent_parser_constants.COL_HEADER_CONTROL_STRAINS, cell.get_text())
            self._validation_errors.append(message)
            return []
        return cell_parser.PARSER.process_names(cell)
                
    def _process_control_type(self, cell):
        control_type = cell.get_text()
        if control_type not in self._control_types:
            err = '%s does not match one of the following control types: \n %s' % (control_type, ' ,'.join((map(str, self._control_types))))
            message = 'Controls table has invalid %s value: %s' % (intent_parser_constants.COL_HEADER_CONTROL_TYPE, err)
            self._validation_errors.append(message)
            return None 
        return control_type

    def _process_timepoint(self, cell):
        try:
            return cell_parser.PARSER.process_values_unit(cell, self._timepoint_units, 'timepoints')
        except TableException as err:
            message = 'Controls table has invalid %s value: %s' % (intent_parser_constants.COL_HEADER_CONTROL_TYPE, err.get_message())
            self._validation_errors.append(message)
            return []
        
    def get_validation_errors(self):
        return self._validation_errors

    def get_validation_warnings(self):
        return self._validation_warnings 
        