
class Error(Exception):
    pass

class ConnectionException(Exception):
    def __init__(self, code, message, content=""):
        super(ConnectionException, self).__init__(message);
        self.code = code
        self.message = message
        self.content = content

class TableException(Error):
    '''
    Class for catch exceptions related to parsing a table. 
    '''
       
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message    
    
    def get_message(self):
        ''' 
        Message reporting the error. 
        '''
        return self.message

    def get_expression(self):
        ''' 
        The expression causing the error. 
        '''
        return self.expression
    
class DictionaryMaintainerException(Error):
    '''
    Class to detect SBOL Dictionary Maintainer exceptions
    '''
    
    def __init__(self, expression, message):
        self._expression = expression
        self._message = message 
        
    def get_message(self):
        return self._message
    
    def get_expression(self):
        return self._expression
    
    