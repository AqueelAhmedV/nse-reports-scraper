class RetryableException(Exception):
    def __init__(self, message):
        super().__init__(message)

class ReportNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)    
